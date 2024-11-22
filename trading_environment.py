import gym
import pandas as pd
import numpy as np
import asyncio
from datetime import datetime, timedelta
from metaapi_cloud_sdk import MetaApi
from gym import spaces
from typing import Tuple, Dict, Any
from config import Config
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts
import logging
from rich.console import Console
from rich.progress import track

console = Console()
logging.basicConfig(level=logging.DEBUG)

class ForexTradingEnvironment(py_environment.PyEnvironment):
    def __init__(self, data: pd.DataFrame, config: Config):
        super().__init__()
        self.data = data
        self.config = config
        self.current_index = 0
        self.position = 0  # 0: flat, 1: long, -1: short
        self.balance = config.INITIAL_BALANCE
        self.max_balance = config.INITIAL_BALANCE
        self.trades = []

        # Define action and observation specs for TF-Agents
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=2, name='action'
        )
        self._observation_spec = array_spec.ArraySpec(
            shape=(10,), dtype=np.float32, name='observation'
        )

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self) -> ts.TimeStep:
        self.current_index = 0
        self.position = 0
        self.balance = self.config.INITIAL_BALANCE
        return ts.restart(self._get_observation())

    def _step(self, action: np.ndarray) -> ts.TimeStep:
        if self.current_index >= len(self.data) - 1:
            return ts.termination(self._get_observation(), self.balance)

        reward = self._execute_action(action)
        self.current_index += 1
        
        if self.current_index >= len(self.data) - 1:
            return ts.termination(self._get_observation(), reward)
        return ts.transition(self._get_observation(), reward)

    def _execute_action(self, action: int) -> float:
        reward = 0.0
        current_price = self.data.iloc[self.current_index]['close']
        previous_price = self.data.iloc[self.current_index - 1]['close']
        timestamp = self.data.iloc[self.current_index]['time']

        # Risk management - max position size
        max_position_size = self.balance * self.config.MAX_POSITION_SIZE

        # Position changes with improved reward structure
        if action == 1 and self.position != 1:  # Buy
            size = min(self.balance * 0.95, max_position_size)
            self.position = 1
            reward -= self.config.TRANSACTION_COST
            self.trades.append({'type': 'buy', 'price': current_price, 'size': size})
            
        elif action == 2 and self.position != -1:  # Sell
            size = min(self.balance * 0.95, max_position_size)
            self.position = -1
            reward -= self.config.TRANSACTION_COST
            self.trades.append({'type': 'sell', 'price': current_price, 'size': size})
            
        elif action == 0 and self.position != 0:  # Close
            self.position = 0
            reward -= self.config.TRANSACTION_COST
            self.trades.append({'type': 'close', 'price': current_price})

        # Calculate returns with position sizing
        price_change = (current_price - previous_price) / previous_price
        position_reward = price_change * self.position * self.balance
        
        # Enhanced reward structure
        reward += position_reward
        
        # Penalize excessive trading
        if len(self.trades) > 50:
            reward *= 0.95
            
        # Reward for new equity highs
        old_balance = self.balance
        self.balance += position_reward
        if self.balance > self.max_balance:
            self.max_balance = self.balance
            reward += self.config.HIGH_WATER_MARK_REWARD
            
        # Penalize drawdowns
        drawdown = (self.max_balance - self.balance) / self.max_balance
        if drawdown > self.config.MAX_DRAWDOWN:
            reward -= self.config.DRAWDOWN_PENALTY
            self.position = 0  # Force position close

        return reward

    def _get_observation(self) -> np.ndarray:
        if self.current_index >= len(self.data):
            return np.zeros(self._observation_spec.shape, dtype=np.float32)

        # Calculate technical indicators
        window = 20
        prices = self.data['close'].values
        current_price = prices[self.current_index]
        
        # Moving averages
        ma20 = np.mean(prices[max(0, self.current_index-window):self.current_index+1])
        ma50 = np.mean(prices[max(0, self.current_index-50):self.current_index+1])
        
        # Relative price positions
        price_to_ma20 = current_price / ma20 - 1
        price_to_ma50 = current_price / ma50 - 1

        row = self.data.iloc[self.current_index]
        
        return np.array([
            row['close'],
            row['volume'],
            row['returns'],
            row['volatility'],
            price_to_ma20,  # Price relative to MA20
            price_to_ma50,  # Price relative to MA50
            self.position,
            self.balance / self.config.INITIAL_BALANCE,
            self.max_balance / self.config.INITIAL_BALANCE,  # High water mark
            len(self.trades) / 100.0  # Trade count normalized
        ], dtype=np.float32)

    def render(self, mode='human'):
        pass

async def load_historical_data(meta_api, account_id, symbol, start_time, end_time):
    # Get the account
    account = await meta_api.metatrader_account_api.get_account(account_id)
    
    # Wait until the account is deployed and connected
    if account.state != 'DEPLOYED':
        await account.deploy()
    if account.connection_status != 'CONNECTED':
        await account.wait_connected()
    
    # Get the connection instance
    connection = meta_api.connect(account.id)
    await connection.wait_synchronized()
    
    # Fetch historical price data
    bars = await connection.get_historical_candles(
        symbol, '1H', start_time.isoformat(), end_time.isoformat()
    )
    
    # Convert the data into a pandas DataFrame
    data = pd.DataFrame([
        {
            'time': bar.time,
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'volume': bar.tick_volume
        } for bar in bars
    ])
    
    return data

async def main():
    # Initialize MetaApi client
    TOKEN = config.TOKEN
    ACCOUNT_ID = config.ACCOUNT_ID  # Replace with your MetaTrader account ID
    SYMBOL = config.SYMBOL  # Replace with your trading symbol
    meta_api = MetaApi(TOKEN)

    # Define time range for historical data
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)

    # Load historical data asynchronously
    data = await load_historical_data(meta_api, ACCOUNT_ID, SYMBOL, start_time, end_time)

    # Initialize the Forex trading environment with the data
    env = ForexTradingEnvironment(data, Config())

    # Rest of your code...
    # For example, wrap the environment and train your agent
    from tf_agents.environments import tf_py_environment, gym_wrapper

    wrapped_env = gym_wrapper.GymWrapper(env)
    train_env = tf_py_environment.TFPyEnvironment(wrapped_env)

    # Proceed with training your agent as before

if __name__ == '__main__':
    asyncio.run(main())

class TradingAgent:
    async def train(self) -> Tuple[float, ...]:
        console.print("\n[bold blue]Starting training...[/bold blue]")
        
        self.collect_data(steps=1000)
        dataset = self.replay_buffer.as_dataset(
            num_parallel_calls=3,
            sample_batch_size=32,
            num_steps=2
        ).prefetch(3)
        iterator = iter(dataset)

        losses = []
        for episode in track(range(self.config.TRAINING_EPISODES), 
                           description="Training episodes"):
            experience, _ = next(iterator)
            loss = self.agent.train(experience).loss
            losses.append(loss)
            
            if episode % 100 == 0:
                console.print(f"Episode {episode}: Loss = {loss:.2f}")
                
        # Print final metrics
        console.print("\n[bold green]Training Complete![/bold green]")
        console.print(f"Final Loss: {losses[-1]:.2f}")
        console.print(f"Average Loss: {np.mean(losses):.2f}")
        console.print(f"Min Loss: {min(losses):.2f}")
        console.print(f"Max Loss: {max(losses):.2f}")
            
        return self.agent, losses
