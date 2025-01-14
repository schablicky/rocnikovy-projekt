import os
import glob
from datetime import datetime
import numpy as np
import tensorflow as tf
import logging

logger = logging.getLogger(__name__)

"""
DQLModel - třída, která reprezentuje model pro reinforcement learning
Model obsahuje konvoluční a LSTM vrstvy, následně je použit mechanismus attention
"""

class DQLModel:
    def __init__(self, state_size=10, action_size=4, load_saved=True):
        self.state_size = state_size
        self.action_size = action_size # Počet akcí (kupovat/prodat/nezmenit/uzavřít)
        self.memory = []
        self.gamma = 0.95
        self.epsilon = 1  # Jak moc model bude "experimentovat" a ne se zlepšovat v ověřených taktikách, z důvodu vyhnutí se lokální propasti
        self.epsilon_min = 0.01  # Minimální hodnota epsilon
        self.epsilon_decay = 0.995  # Jak rychle se bude epsilon snižovat
        self.total_steps = 0 # Celkový počet kroků
        self.warmup_steps = 1  # Počet kroků, po kterých se začne snižovat epsilon
        self.save_dir = 'saved_models'
        
        # Načtení modelu
        if load_saved:
            loaded_model = self.load_latest_model()
            if loaded_model:
                self.model = loaded_model
                self.target_model = loaded_model
            else:
                self.model = self._build_model()
                self.target_model = self._build_model()
        else:
            self.model = self._build_model()
            self.target_model = self._build_model()

    # Vytvoření modelu
    def _build_model(self):
        inputs = tf.keras.layers.Input(shape=(self.state_size, 6)) # Vstupní vrstva, 6 hodnot pro každý časový krok
        
        # CNN vrstva, extrakce "vzorů" z dat, normalně využívaná pro extrakci vzorů z obrázků
        x1 = tf.keras.layers.Conv1D(128, 3, padding='same')(inputs)
        x1 = tf.keras.layers.BatchNormalization()(x1)
        x1 = tf.keras.layers.Activation('relu')(x1)
        
        # LSTM vrstva, využití pro predikci na základě sekvencí dat
        x2 = tf.keras.layers.LSTM(128, return_sequences=True)(inputs) # 128 neuronů
        x2 = tf.keras.layers.Dropout(0.2)(x2)
        
        # Spojení vrstev
        x = tf.keras.layers.Concatenate()([x1, x2])
        
        # Attention mechanismus, zvýraznění důležitých částí dat
        attention = tf.keras.layers.Dense(1)(x)
        attention = tf.keras.layers.Flatten()(attention)
        attention = tf.keras.layers.Activation('softmax')(attention)
        attention = tf.keras.layers.RepeatVector(256)(attention)
        attention = tf.keras.layers.Permute([2, 1])(attention)
        
        # Násobení vrstev
        x = tf.keras.layers.Multiply()([x, attention])
        x = tf.keras.layers.GlobalAveragePooling1D()(x)
        
        # Plně propojená vrstva (Dense)
        x = tf.keras.layers.Dense(64, activation='relu')(x)
        x = tf.keras.layers.Dropout(0.2)(x)
        
        # Dvojitý výstup, jeden pro hodnoty Q a druhý pro hodnotu stavu
        q_values = tf.keras.layers.Dense(self.action_size)(x)
        state_value = tf.keras.layers.Dense(1)(x)
        
        # Přidání hodnot
        outputs = tf.keras.layers.Add()([q_values, state_value])
        
        # Vytvoření modelu
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        # Kompilace modelu
        model.compile(
            optimizer=tf.keras.optimizers.Adam(0.0001), # Adam optimizer, učení s adaptivním learning ratem, spojuje výhody Adagrad a RMSprop
            loss=self._huber_loss # Huber loss
        )
        return model
        
    # Huber loss funkce, řeší problémy s extrémními hodnotami
    def _huber_loss(self, y_true, y_pred):
        return tf.keras.losses.Huber(delta=1.0)(y_true, y_pred)
        
    def act(self, state):
        """  Provede akci na základě stavu """
        self.total_steps += 1
        
        # Snížení epsilonu, pokud je větší než epsilon_min (1, začíná již po prvním kroku)
        if self.total_steps > self.warmup_steps:
            self.epsilon = max(
                self.epsilon_min,
                self.epsilon * self.epsilon_decay
            )
            
        # Náhodná akce, pokud je náhodné číslo menší než epsilon, (experimentování)
        if np.random.rand() <= self.epsilon:
            action = np.random.randint(self.action_size)
            logger.debug(f"Random action: {action}, epsilon: {self.epsilon:.4f}, steps: {self.total_steps}")
            return action
        
        # Predikce akce na základě modelu
        q_values = self.model.predict(state, verbose=0) # Predikce hodnoty Q
        action = np.argmax(q_values[0]) # Vybrání akce s nejvyšší hodnotou
        logger.debug(f"Model action: {action}, epsilon: {self.epsilon:.4f}, steps: {self.total_steps}")
        return action
        
    # Funkce pro trénování modelu
    def train(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # Přidání do paměti
        if len(self.memory) > 1000:
            self.memory.pop(0) # Omezení paměti na 1000 záznamů
        
        if len(self.memory) >= 32:
            indices = np.random.choice(len(self.memory), 32, replace=False) # Náhodný výběr 32 záznamů, z důvodu zamezení korelace (overfitting)
            minibatch = [self.memory[i] for i in indices]
            
            # Příprava dat pro trénování
            states = np.array([x[0][0] for x in minibatch])
            next_states = np.array([x[3][0] for x in minibatch])
            
            # Příprava cílových hodnot, výpočet hodnoty Q
            targets = self.model.predict(states)
            next_q_values = self.target_model.predict(next_states)
            
            # Výpočet odměny, pokud je stav konečný, tak je odměna rovna hodnotě, jinak je odměna rovna hodnotě + gamma * max(next_q_values)
            for i, (_, action, reward, _, done) in enumerate(minibatch):
                if done:
                    targets[i][action] = reward
                else:
                    targets[i][action] = reward + self.gamma * np.amax(next_q_values[i])
            
            # Trénování modelu
            self.model.fit(states, targets, epochs=1, verbose=0)
            
            # Snížení hodnoty epsilonu (explorace)
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay

    # Uložení modelu
    def save_model(self, timestamp):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        self.model.save(f'{self.save_dir}/model_{timestamp}.h5')
    
    # Načtení posledního modelu
    def load_latest_model(self):
        if not os.path.exists(self.save_dir):
            return None
            
        model_files = glob.glob(f'{self.save_dir}/model_*.h5')
        if not model_files:
            return None
            
        latest_model = max(model_files, key=os.path.getctime)
        try:
            return tf.keras.models.load_model(latest_model)
        except:
            return None
