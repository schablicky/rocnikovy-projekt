import asyncio
import logging
import sys
import numpy as np
import pandas as pd
import tensorflow as tf
from datetime import datetime
from data_fetcher import RestDataFetcher
from trading_env import TradingEnv
from dql_model import DQLModel

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Set TensorFlow logging level
tf.get_logger().setLevel('ERROR')

async def initialize_data(data_fetcher, symbol):
    """Load initial candles"""
    logger.info("Loading initial candles...")
    price_history = []
    
    # Get 10 initial candles
    for _ in range(10):
        candle = await data_fetcher.get_current_candle(symbol=symbol)
        if candle and 'time' in candle:
            candle['time'] = pd.to_datetime(candle['time'])
            price_history.append(candle)
            logger.debug(f"Initial candle loaded: {candle}")
        await asyncio.sleep(1)  # Rate limiting
        
    logger.info(f"Loaded {len(price_history)} initial candles")
    return price_history

async def main():
    logger.info("=== Trading Bot Starting ===")
    data_fetcher = RestDataFetcher()
    env = TradingEnv(window_size=10)  # Increased window size
    model = DQLModel(state_size=10, action_size=4, load_saved=True)  # Match window size
    symbol = 'EURUSD'
    
    logger.info(f"Model configuration: Window Size={env.window_size}, State Size={model.state_size}")
    logger.info(f"Current epsilon value: {model.epsilon}")
    
    price_history = await initialize_data(data_fetcher, symbol)
    logger.info(f"Initial price history loaded: {len(price_history)} candles")
    
    while True:
        try:
            await asyncio.sleep(60)  # Wait for next minute
            logger.debug("=== New Trading Cycle ===")
            
            # Get current market data and position status
            candle = await data_fetcher.get_current_candle(symbol=symbol)
            if candle:
                logger.debug(f"New candle: {candle}")
                price_history.append(candle)
                logger.debug(f"Price history length: {len(price_history)}")
                
                if len(price_history) >= 10:  # Changed from > 2
                    price_history.pop(0)
                
                if len(price_history) >= 2:
                    data = pd.DataFrame(price_history)
                    logger.debug(f"Data shape: {data.shape}")
                    logger.debug(f"Latest prices: Close={data['close'].iloc[-1]}, Open={data['open'].iloc[-1]}")
                    
                    state = env.get_state(data)
                    
                    if state is not None:
                        logger.debug(f"State shape: {state.shape}, dtype: {state.dtype}")
                        logger.debug(f"State values: min={state.min()}, max={state.max()}, mean={state.mean()}")
                        
                        state = np.expand_dims(state, axis=0)
                        action_values = model.model.predict(state, verbose=0)
                        action = model.act(state)
                        
                        logger.info(f"Q-values: {action_values[0]}")
                        logger.info(f"Selected action: {action}")
                        logger.info(f"Random action: {model.epsilon > np.random.rand()}")
                        
                        current_price = data['close'].iloc[-1]
                        logger.debug(f"Current price: {current_price}")
                        
                        # Position check
                        positions = await data_fetcher.get_positions()
                        logger.info(f"Current positions: {positions}")
                        
                        reward, done, save_model = await env.step(
                            action, 
                            current_price, 
                            data_fetcher, 
                            symbol
                        )
                        logger.info(f"Step result - Reward: {reward}, Done: {done}")
                        logger.info(f"Environment state - Position: {env.position}, Entry price: {env.entry_price}")
                        logger.info(f"Total profit: {env.total_profit}, Trades made: {env.trades_count}")
                        
                        # Train only on actual trade results
                        if reward != 0:
                            next_state = env.get_state(data)
                            if next_state is not None:
                                next_state = np.expand_dims(next_state, axis=0)
                                logger.debug("Training model...")
                                model.train(state, action, reward, next_state, done)
                                logger.info(f"New epsilon value: {model.epsilon}")
                        
                        if save_model:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            model.save_model(timestamp)
                            logger.info(f"Model saved after {env.trades_count} trades")
                    else:
                        logger.warning("Invalid state generated")
            
        except Exception as e:
            logger.exception(f"Error in main loop: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)