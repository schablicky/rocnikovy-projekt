import os
import asyncio
import pandas as pd
from metaapi_cloud_sdk import MetaApi
import metaapi_cloud_sdk
from datetime import datetime, timedelta
from config import Config
from data_loader import HistoricalDataLoader
from trading_environment import ForexTradingEnvironment
from agent import TradingAgent
from tf_agents.environments import tf_py_environment

async def main():
    config = Config()
    
    try:
        # Load historical data
        loader = HistoricalDataLoader(config.TOKEN, config.ACCOUNT_ID)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=config.LOOKBACK_DAYS)
        data = await loader.load_data(config.SYMBOL, start_time, end_time)

        # Create and wrap environment
        env = ForexTradingEnvironment(data, config)
        # Directly wrap with TFPyEnvironment
        train_env = tf_py_environment.TFPyEnvironment(env)

        # Initialize and train agent
        trading_agent = TradingAgent(train_env, config)
        agent, losses = await trading_agent.train()

        print(f"Training completed. Final loss: {losses[-1]}")
        
        return agent, train_env

    except Exception as e:
        print(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())