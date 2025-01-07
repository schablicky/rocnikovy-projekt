import os
import glob
from datetime import datetime
import numpy as np
import tensorflow as tf
import logging

logger = logging.getLogger(__name__)

class DQLModel:
    def __init__(self, state_size=10, action_size=4, load_saved=True):  # Increased state_size
        self.state_size = state_size
        self.action_size = action_size
        self.memory = []
        self.gamma = 0.95
        self.epsilon = 1  # exploration
        self.epsilon_min = 0.01  # Minimum exploration rate
        self.epsilon_decay = 0.995  # Slower decay rate
        self.total_steps = 0
        self.warmup_steps = 1  # Steps before starting decay
        self.save_dir = 'saved_models'
        
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

    def _build_model(self):
        inputs = tf.keras.layers.Input(shape=(self.state_size, 6))
        
        # CNN for feature extraction
        x1 = tf.keras.layers.Conv1D(128, 3, padding='same')(inputs)
        x1 = tf.keras.layers.BatchNormalization()(x1)
        x1 = tf.keras.layers.Activation('relu')(x1)
        
        # LSTM branch
        x2 = tf.keras.layers.LSTM(128, return_sequences=True)(inputs)
        x2 = tf.keras.layers.Dropout(0.2)(x2)
        
        # Merge branches
        x = tf.keras.layers.Concatenate()([x1, x2])
        
        # Attention mechanism
        attention = tf.keras.layers.Dense(1)(x)
        attention = tf.keras.layers.Flatten()(attention)
        attention = tf.keras.layers.Activation('softmax')(attention)
        attention = tf.keras.layers.RepeatVector(256)(attention)
        attention = tf.keras.layers.Permute([2, 1])(attention)
        
        x = tf.keras.layers.Multiply()([x, attention])
        x = tf.keras.layers.GlobalAveragePooling1D()(x)
        
        # Decision layers
        x = tf.keras.layers.Dense(64, activation='relu')(x)
        x = tf.keras.layers.Dropout(0.2)(x)
        
        # Dual output (Q-values and State value)
        q_values = tf.keras.layers.Dense(self.action_size)(x)
        state_value = tf.keras.layers.Dense(1)(x)
        
        outputs = tf.keras.layers.Add()([q_values, state_value])
        
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        model.compile(
            optimizer=tf.keras.optimizers.Adam(0.0001),
            loss=self._huber_loss
        )
        return model
        
    def _huber_loss(self, y_true, y_pred):
        return tf.keras.losses.Huber(delta=1.0)(y_true, y_pred)
        
    def act(self, state):
        """Select action with enhanced logging"""
        self.total_steps += 1
        
        # Only start decaying after warmup period
        if self.total_steps > self.warmup_steps:
            self.epsilon = max(
                self.epsilon_min,
                self.epsilon * self.epsilon_decay
            )
            
        if np.random.rand() <= self.epsilon:
            action = np.random.randint(self.action_size)
            logger.debug(f"Random action: {action}, epsilon: {self.epsilon:.4f}, steps: {self.total_steps}")
            return action
            
        q_values = self.model.predict(state, verbose=0)
        action = np.argmax(q_values[0])
        logger.debug(f"Model action: {action}, epsilon: {self.epsilon:.4f}, steps: {self.total_steps}")
        return action
        
    def train(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        if len(self.memory) > 1000:
            self.memory.pop(0)
        
        if len(self.memory) >= 32:
            indices = np.random.choice(len(self.memory), 32, replace=False)
            minibatch = [self.memory[i] for i in indices]
            
            states = np.array([x[0][0] for x in minibatch])
            next_states = np.array([x[3][0] for x in minibatch])
            
            targets = self.model.predict(states)
            next_q_values = self.target_model.predict(next_states)
            
            for i, (_, action, reward, _, done) in enumerate(minibatch):
                if done:
                    targets[i][action] = reward
                else:
                    targets[i][action] = reward + self.gamma * np.amax(next_q_values[i])
            
            self.model.fit(states, targets, epochs=1, verbose=0)
            
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay

    def save_model(self, timestamp):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        self.model.save(f'{self.save_dir}/model_{timestamp}.h5')
        
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
