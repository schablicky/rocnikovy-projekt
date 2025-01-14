import numpy as np
import pandas as pd
import logging
from datetime import datetime
from technical_indicators import *

logger = logging.getLogger(__name__)


'''
TradingEnv - třída, která reprezentuje prostředí pro obchodování.
Třída obsahuje metody pro výpočet indikátorů, generování stavu, provedení obchodu a kontrolu pozice.
'''

class TradingEnv:
    def __init__(self, window_size=10):
        self.window_size = window_size # kolik minulých hodnot použijeme pro rozhodování
        self.position = None
        self.position_id = None
        self.entry_price = None
        self.stop_loss = None
        self.take_profit = None
        self.max_position_time = 60  # Maximalni doba drzeni pozice v minutach
        self.position_start_time = None
        self.trades_count = 0
        self.total_profit = 0
        self.last_trade_time = None
        self.min_trade_interval = 1  # Minimalni cas mezi obchody v minutach
        self.save_threshold = 5  # Save model after every 5 trades
        self.logger = logging.getLogger(__name__)
        
        # indikatory
        self.sma = None
        self.rsi = None 
        self.macd = None

    def calculate_features(self, data):
        df = data.copy()
        
        # Cenove indikatory
        df['returns'] = df['close'].pct_change()
        df['momentum'] = df['returns'].rolling(5).mean()
        df['volatility'] = df['returns'].rolling(10).std()
        
        # Trendovy indikator
        df['sma_short'] = df['close'].rolling(5).mean()
        df['sma_long'] = df['close'].rolling(20).mean()
        df['trend'] = (df['sma_short'] - df['sma_long']) / df['sma_long']
        
        # High-low rozdil
        df['high_low_diff'] = df['high'] - df['low']
        df['resistance'] = df['high'].rolling(10).max()
        df['support'] = df['low'].rolling(10).min()
        
        # Objemovy indikator
        df['volume_ma'] = df['tickVolume'].rolling(5).mean()
        df['volume_pressure'] = df['tickVolume'] / df['volume_ma']
        
        # Normalizace hodnot
        features = ['returns', 'momentum', 'volatility', 'trend', 
                   'high_low_diff', 'volume_pressure']
        for feature in features:
            mean = df[feature].mean()
            std = df[feature].std()
            df[feature] = (df[feature] - mean) / (std + 1e-8)
            
        return df[features].fillna(0)

    def calculate_indicators(self, data):
        logger.debug("Starting indicator calculations...")
        df = data.copy()
        
        try:
            # vypocet sma (simple moving average)
            self.sma = df['close'].rolling(window=20).mean().iloc[-1]
            
            # vypocet rsi (relative strength index)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            self.rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            # vypocet macd (moving average convergence divergence)
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            self.macd = (exp1 - exp2).iloc[-1]
            
            # vypocet stochastickych oscilatoru
            df['returns'] = df['close'].pct_change()
            df['momentum'] = df['returns'].rolling(5).mean()
            df['volatility'] = df['returns'].rolling(10).std()
            
            # Trendovy indikator
            df['sma_short'] = df['close'].rolling(5).mean()
            df['sma_long'] = df['close'].rolling(10).mean()
            df['trend'] = (df['sma_short'] - df['sma_long']) / df['sma_long']
            
            # 6 hodnot pro ai model
            features = [
                'returns',
                'momentum', 
                'volatility',
                'trend',
                'tickVolume',  # Obchodovany objem
                'close'        # Aktualni cena
            ]
            
            result = pd.DataFrame()
            for feature in features:
                mean = df[feature].mean()
                std = df[feature].std()
                result[feature] = (df[feature] - mean) / (std + 1e-8)
                logger.debug(f"Normalized {feature}: mean={mean:.4f}, std={std:.4f}")
            
            logger.debug(f"Final feature shape: {result.shape}")
            return result.fillna(0)
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            raise e

    def get_state(self, data):
        """  Vytvori stavovy prostor pro AI model """
        if len(data) < self.window_size:
            logger.warning(f"Insufficient data: {len(data)}/{self.window_size} candles")
            return None
            
        try:
            # Konverze dat do numerickych hodnot
            numeric_data = data[['open', 'high', 'low', 'close', 'tickVolume']].astype(float)
            logger.debug(f"Numeric data shape: {numeric_data.shape}")
            
            # Kalulace indikatoru
            features = self.calculate_indicators(numeric_data)
            logger.debug(f"Features calculated: {features.columns.tolist()}")
            logger.debug(f"Feature statistics: \n{features.describe()}")
            
            # Vytvoreni stavu
            state = features.iloc[-self.window_size:].values
            logger.debug(f"Final state shape: {state.shape}")
            
            return state.astype(np.float32)
        except Exception as e:
            logger.error(f"State generation error: {e}")
            return None

    async def check_position(self, data_fetcher, symbol):
        positions = await data_fetcher.get_positions()
        return next((pos for pos in positions if pos['symbol'] == symbol), None)
        
    async def step(self, action, current_price, data_fetcher, symbol):
        """  Provede krok obchodovani """
        reward = 0
        done = False
        save_model = False
        
        try:
            # Získání aktuálních pozic
            positions = await data_fetcher.get_positions()
            current_position = next((pos for pos in positions if pos['symbol'] == symbol), None)
            logger.debug(f"Current position check: {current_position}")
            
            if not current_position and not self.position:
                if action in [0, 1]:  # BUY nebo SELL
                    action_type = "ORDER_TYPE_BUY" if action == 0 else "ORDER_TYPE_SELL"
                    logger.info(f"Attempting to execute {action_type}")
                    
                    # Provedeni obchodu
                    result = await data_fetcher.execute_trade(action_type, symbol)

                    # Kontrola vysledku provedeni obchodu
                    if result and 'orderId' in result:
                        self.position = 'long' if action == 0 else 'short'
                        self.position_id = result['orderId']
                        self.entry_price = current_price
                        self.trades_count += 1
                        logger.info(f"Trade executed: {action_type}, ID: {result['orderId']}")
                    else:
                        logger.error("Trade execution failed")
                        
            elif current_position and action == 3:  # Uzavreni pozice
                profit = float(current_position['unrealizedProfit'])
                logger.info(f"Attempting to close position, current P/L: {profit}")
                
                # Uzavreni pozice
                result = await data_fetcher.close_position(current_position['id'])

                # Kontrola vysledku uzavreni pozice
                if result:
                    reward = profit
                    self.total_profit += reward
                    self.position = None
                    self.position_id = None
                    logger.info(f"Position closed, Profit: {profit}") # Vypsani zisku/ztraty
                else:
                    logger.error("Position closing failed")
                    
            if reward != 0:  # Pokud proveden a uzavren obchod
                done = True
                self.trades_count += 1
                if self.trades_count % self.save_threshold == 0: # Ulozeni modelu po kazdem 5. obchodu
                    save_model = True
                    
            logger.debug(f"Step complete - Position: {self.position}, Trades: {self.trades_count}")
            return reward, done, save_model
            
        except Exception as e:
            logger.exception("Error in trading step")
            return 0, False, False