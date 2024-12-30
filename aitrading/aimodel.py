import asyncio
import requests
from datetime import datetime, timedelta
from market_data_service import fetch_and_save_market_data
from trade_service import execute_trade, close_trade
from config import Config
import numpy as np
import tensorflow as tf
import tf_agents
from tf_agents.environments import tf_py_environment, py_environment
from tf_agents.networks import q_network
from tf_agents.agents.dqn import dqn_agent
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.trajectories import trajectory
from tf_agents.utils import common

class TradingEnvironment(py_environment.PyEnvironment):
    def __init__(self, market_data_service, symbol, initial_balance=10000):
        super().__init__()
        self._action_spec = tf.TensorSpec(shape=(), dtype=tf.int32, name='action')
        self._observation_spec = tf.TensorSpec(shape=(5,), dtype=tf.float32, name='observation')
        self.market_data_service = market_data_service
        self.symbol = symbol
        self.balance = initial_balance
        self.position = 0  # 0: no position, 1: buy, -1: sell
        self.current_price = None
        self.prev_price = None
        self.reward = 0.0

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    async def _update_price(self):
        data = await self.market_data_service()
        self.prev_price = self.current_price
        self.current_price = data['close']

    def _reset(self):
        self.balance = 10000
        self.position = 0
        self.current_price = None
        self.prev_price = None
        asyncio.run(self._update_price())
        return tf_agents.trajectories.time_step.restart(self._get_observation())

    def _step(self, action):
        asyncio.run(self._update_price())

        if self.current_price is None or self.prev_price is None:
            raise ValueError("Price data is not initialized.")

        if action == 1:  # Buy
            self.position = 1
        elif action == 2:  # Sell
            self.position = -1
        elif action == 0 and self.position != 0:  # Close
            self.reward = (self.current_price - self.prev_price) * self.position * 1000
            self.balance += self.reward
            self.position = 0

        observation = self._get_observation()
        return tf_agents.trajectories.time_step.transition(observation, reward=self.reward, discount=1.0)

    def _get_observation(self):
        return np.array([
            self.balance,
            self.position,
            self.current_price or 0.0,
            self.prev_price or 0.0,
            self.reward
        ], dtype=np.float32)

class RestAPITradingAgent:
    def __init__(self, config: Config):
        self.config = config
        self.market_data_service = fetch_and_save_market_data()
        self.trade_service_execute = execute_trade()
        self.trade_service_close = close_trade()
        self.auth_token = config.TOKEN
        self.account_id = config.ACCOUNT_ID
        self.symbol = config.SYMBOL

        self.env = tf_py_environment.TFPyEnvironment(TradingEnvironment(self.market_data_service, self.symbol))
        self.q_net = q_network.QNetwork(self.env.observation_spec(), self.env.action_spec(), fc_layer_params=(100,))
        self.agent = dqn_agent.DqnAgent(
            self.env.time_step_spec(),
            self.env.action_spec(),
            q_network=self.q_net,
            optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
            td_errors_loss_fn=common.element_wise_squared_loss,
            train_step_counter=tf.Variable(0)
        )
        self.agent.initialize()

        self.replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
            self.agent.collect_data_spec,
            batch_size=self.env.batch_size,
            max_length=10000
        )

    async def collect_data(self, steps):
        time_step = self.env.reset()
        policy_state = self.agent.collect_policy.get_initial_state(self.env.batch_size)

        for _ in range(steps):
            action_step = self.agent.collect_policy.action(time_step, policy_state)
            next_time_step = self.env.step(action_step.action)
            traj = trajectory.from_transition(time_step, action_step, next_time_step)
            self.replay_buffer.add_batch(traj)
            time_step = next_time_step

    async def train_agent(self, iterations):
        dataset = self.replay_buffer.as_dataset(
            num_parallel_calls=3, sample_batch_size=64, num_steps=2
        ).prefetch(3)
        iterator = iter(dataset)

        for _ in range(iterations):
            experience, _ = next(iterator)
            self.agent.train(experience)

    async def trade_and_evaluate(self):
        initial_balance = self.env.pyenv.envs[0].balance
        print(f"Initial Balance: {initial_balance}")

        await self.collect_data(steps=100)
        await self.train_agent(iterations=200)

        time_step = self.env.reset()
        policy_state = self.agent.policy.get_initial_state(self.env.batch_size)

        for _ in range(10):
            action_step = self.agent.policy.action(time_step, policy_state)
            time_step = self.env.step(action_step.action)

        final_balance = self.env.pyenv.envs[0].balance
        print(f"Final Balance: {final_balance}")
        profit_loss = final_balance - initial_balance
        print(f"Profit/Loss: {profit_loss}")

if __name__ == "__main__":
    config = Config()
    agent = RestAPITradingAgent(config)

    asyncio.run(agent.trade_and_evaluate())
