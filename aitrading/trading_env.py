import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pandas as pd
import logging
from datetime import datetime
from technical_indicators import *
from django.contrib.auth import get_user_model
from trading_web.trading.models import Trade
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

class TradingEnv:
    def __init__(self, window_size=10):  # Changed window size to 10
        self.window_size = window_size
        self.position = None
        self.position_id = None
        self.entry_price = None
        self.stop_loss = None
        self.take_profit = None
        self.max_position_time = 60  # minutes
        self.position_start_time = None
        self.trades_count = 0
        self.total_profit = 0
        self.last_trade_time = None
        self.min_trade_interval = 1  # Minimum minutes between trades
        self.save_threshold = 5  # Save every 5 trades
        self.logger = logging.getLogger(__name__)
        self.ai_user = get_user_model().objects.get(username='AI')

    def calculate_features(self, data):
        df = data.copy()
        
        # Price action features
        df['returns'] = df['close'].pct_change()
        df['momentum'] = df['returns'].rolling(5).mean()
        df['volatility'] = df['returns'].rolling(10).std()
        
        # Trend features
        df['sma_short'] = df['close'].rolling(5).mean()
        df['sma_long'] = df['close'].rolling(20).mean()
        df['trend'] = (df['sma_short'] - df['sma_long']) / df['sma_long']
        
        # Support/Resistance
        df['high_low_diff'] = df['high'] - df['low']
        df['resistance'] = df['high'].rolling(10).max()
        df['support'] = df['low'].rolling(10).min()
        
        # Volume pressure
        df['volume_ma'] = df['tickVolume'].rolling(5).mean()
        df['volume_pressure'] = df['tickVolume'] / df['volume_ma']
        
        # Normalize features
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
            # Price features
            df['returns'] = df['close'].pct_change()
            df['momentum'] = df['returns'].rolling(5).mean()
            df['volatility'] = df['returns'].rolling(10).std()
            
            # Trend features
            df['sma_short'] = df['close'].rolling(5).mean()
            df['sma_long'] = df['close'].rolling(10).mean()
            df['trend'] = (df['sma_short'] - df['sma_long']) / df['sma_long']
            
            # Final features (exactly 6 to match model)
            features = [
                'returns',
                'momentum', 
                'volatility',
                'trend',
                'tickVolume',  # Raw volume
                'close'        # Current price
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
        """Generate state from price history"""
        if len(data) < self.window_size:
            logger.warning(f"Insufficient data: {len(data)}/{self.window_size} candles")
            return None
            
        try:
            # Convert to numeric and calculate features
            numeric_data = data[['open', 'high', 'low', 'close', 'tickVolume']].astype(float)
            logger.debug(f"Numeric data shape: {numeric_data.shape}")
            
            # Calculate features
            features = self.calculate_indicators(numeric_data)
            logger.debug(f"Features calculated: {features.columns.tolist()}")
            logger.debug(f"Feature statistics: \n{features.describe()}")
            
            # Get last window_size rows
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
        """Execute trading step with enhanced logging"""
        reward = 0
        done = False
        save_model = False
        
        try:
            # Get current positions
            positions = await data_fetcher.get_positions()
            current_position = next((pos for pos in positions if pos['symbol'] == symbol), None)
            logger.debug(f"Current position check: {current_position}")
            
            if not current_position and not self.position:
                if action in [0, 1]:  # BUY or SELL
                    action_type = "ORDER_TYPE_BUY" if action == 0 else "ORDER_TYPE_SELL"
                    trade_type = 'buy' if action == 0 else 'sell'
                    logger.info(f"Attempting to execute {action_type}")
                    
                    result = await data_fetcher.execute_trade(action_type, symbol)
                    if result and 'orderId' in result:
                        Trade.objects.create(
                            user=self.ai_user,
                            symbol=symbol,
                            trade_type=trade_type,
                            price=current_price,
                            volume=1.0,
                            position_id=result['orderId']
                        )

                        self.position = 'long' if action == 0 else 'short'
                        self.position_id = result['orderId']
                        self.entry_price = current_price
                        self.trades_count += 1
                        logger.info(f"Trade executed: {action_type}, ID: {result['orderId']}")
                    else:
                        logger.error("Trade execution failed")
                        
            elif current_position and action == 3:  # CLOSE
                profit = float(current_position['unrealizedProfit'])
                logger.info(f"Attempting to close position, current P/L: {profit}")
                
                result = await data_fetcher.close_position(current_position['id'])
                if result:
                    Trade.objects.create(
                        user=self.ai_user,
                        symbol=symbol,
                        trade_type='sell' if self.position == 'long' else 'buy',
                        price=current_price,
                        volume=1.0,
                        position_id=self.position_id
                    )

                    reward = profit
                    self.total_profit += reward
                    self.position = None
                    self.position_id = None
                    logger.info(f"Position closed, Profit: {profit}")
                else:
                    logger.error("Position closing failed")
                    
            if reward != 0:  # Trade completed
                self.trades_count += 1
                if self.trades_count % self.save_threshold == 0:
                    save_model = True
                    
            logger.debug(f"Step complete - Position: {self.position}, Trades: {self.trades_count}")
            return reward, done, save_model
            
        except Exception as e:
            logger.exception("Error in trading step")
            return 0, False, False