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
from api_service import bot_state, start_api_server
import threading

# Logovani
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

tf.get_logger().setLevel('ERROR')

async def initialize_data(data_fetcher, symbol):
    """ Získaní historických dat pro inicializaci prostředí (10 svíček) """
    logger.info("Loading initial candles...")
    price_history = []
    
    # Získání 10 svíček (bohužel jsou identické :( ) -> 100 svíček
    for _ in range(100):
        candle = await data_fetcher.get_current_candle(symbol=symbol)
        if candle and 'time' in candle:
            candle['time'] = pd.to_datetime(candle['time'])
            price_history.append(candle)
            logger.debug(f"Initial candle loaded: {candle}")
        await asyncio.sleep(1)
        
    logger.info(f"Loaded {len(price_history)} initial candles")
    return price_history

async def main():

    """
    Krom AI také obsahuje websocket server pro komunikaci s frontendem, slouží pouze
    jako debugovací nástroj pro zobrazení stavu modelu a stav indikátorů.
    """

    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    logger.info("=== Trading Bot Starting ===")
    data_fetcher = RestDataFetcher()
    env = TradingEnv(window_size=100) # Prostředí pro obchodování
    model = DQLModel(state_size=10, action_size=4, load_saved=True) # Model AI
    symbol = 'EURUSD' # Symbol měnového páru (kvůli jednoduchosti pevně nastaveno)
    
    logger.info(f"Model configuration: Window Size={env.window_size}, State Size={model.state_size}")
    logger.info(f"Current epsilon value: {model.epsilon}")
    
    price_history = await initialize_data(data_fetcher, symbol)
    logger.info(f"Initial price history loaded: {len(price_history)} candles")
    
    while True:
        try:
            await asyncio.sleep(60)  # Cyklus trvá 60 sekund
            logger.debug("=== New Trading Cycle ===")
            
            # získání nové svíčky
            candle = await data_fetcher.get_current_candle(symbol=symbol)
            if candle:
                logger.debug(f"New candle: {candle}")
                price_history.append(candle) # přidání nové svíčky do historie
                logger.debug(f"Price history length: {len(price_history)}")
                
                if len(price_history) >= 100: # Pokud je historie delší než 10 svíček, tak se první smaže, čili se zrak AI defakto posune o jednu minutu -> 100 svíček
                    price_history.pop(0)
                
                if len(price_history) >= 100: # Toto má být 10, trošku jsem zapomněl změnit -> 100 svíček
                    data = pd.DataFrame(price_history)
                    logger.debug(f"Data shape: {data.shape}")
                    logger.debug(f"Latest prices: Close={data['close'].iloc[-1]}, Open={data['open'].iloc[-1]}")
                    
                    state = env.get_state(data) # Získání stavu prostředí a AI
                    
                    if state is not None: # Hlavně pro debugování
                        logger.debug(f"State shape: {state.shape}, dtype: {state.dtype}")
                        logger.debug(f"State values: min={state.min()}, max={state.max()}, mean={state.mean()}")
                        
                        state = np.expand_dims(state, axis=0) # Rozšíření dimenze pro AI model
                        action_values = model.model.predict(state, verbose=0) # Predikce
                        action = model.act(state) # Provedení akce
                        
                        logger.info(f"Q-values: {action_values[0]}")
                        logger.info(f"Selected action: {action}")
                        logger.info(f"Random action: {model.epsilon > np.random.rand()}")
                        
                        current_price = data['close'].iloc[-1] # Aktuální cena
                        logger.debug(f"Current price: {current_price}")
                        
                        # Kontrola pozice
                        positions = await data_fetcher.get_positions()
                        logger.info(f"Current positions: {positions}")
                        
                        # Provedení kroku v prostředí
                        reward, done, save_model = await env.step(
                            action, 
                            current_price, 
                            data_fetcher, 
                            symbol
                        )

                        
                        bot_state["model_state"].update({
                            "epsilon": model.epsilon,
                            "total_steps": model.total_steps
                        }) # Data pro websocket server

                        bot_state["trading_stats"].update({
                            "total_profit": env.total_profit,
                            "trades_count": env.trades_count,
                            "current_position": env.position
                        }) # Data pro websocket server

                        bot_state["indicators"].update({
                            "SMA": env.sma,
                            "RSI": env.rsi,
                            "MACD": env.macd
                        }) # Data pro websocket server

                        if action_values is not None:
                            bot_state["last_prediction"] = action_values[0].tolist()


                        logger.info(f"Step result - Reward: {reward}, Done: {done}")
                        logger.info(f"Environment state - Position: {env.position}, Entry price: {env.entry_price}")
                        logger.info(f"Total profit: {env.total_profit}, Trades made: {env.trades_count}")
                        
                        # Trénování modelu, pokud byla provedena akce, která není hold
                        if reward != 0:
                            next_state = env.get_state(data)
                            if next_state is not None:
                                next_state = np.expand_dims(next_state, axis=0)
                                logger.debug("Training model...")
                                model.train(state, action, reward, next_state, done) # Trénování modelu
                                logger.info(f"New epsilon value: {model.epsilon}")
                        
                        # Uložení modelu
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