import asyncio
from trading_environment import ForexTradingEnvironment, load_historical_data
from metaapi_cloud_sdk import MetaApi
from datetime import datetime, timedelta
from tf_agents.environments import tf_py_environment, gym_wrapper
from typing import Tuple
from config import Config
import tensorflow as tf
from tf_agents.agents.dqn import dqn_agent
from tf_agents.networks import q_network
from tf_agents.utils import common
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.trajectories import trajectory
from rich.console import Console
from rich.progress import track
from rich.table import Table
from rich.live import Live
import numpy as np
console = Console()
class TradingAgent:
    def __init__(self, train_env, config: Config):
        self.train_env = train_env
        self.config = config
        self.q_net = self._build_q_network()
        self.agent = self._build_agent()
        self.replay_buffer = self._build_replay_buffer()
    def _build_q_network(self):
        # Get input/output specs
        input_tensor_spec = self.train_env.observation_spec()
        output_tensor_spec = self.train_env.action_spec()
        # Define preprocessing layers
        preprocessing_layers = tf.keras.Sequential([
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(64, activation='relu'),
        ])
        return q_network.QNetwork(
            input_tensor_spec,
            output_tensor_spec,
            preprocessing_layers=preprocessing_layers,
            fc_layer_params=None,  # No additional layers needed
            activation_fn=tf.keras.activations.relu
        )
    def _build_agent(self):
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.0001)
        agent = dqn_agent.DqnAgent(
            self.train_env.time_step_spec(),
            self.train_env.action_spec(),
            q_network=self.q_net,
            optimizer=optimizer,
            td_errors_loss_fn=common.element_wise_squared_loss,
            gamma=0.99,
            epsilon_greedy=0.2,
            target_update_period=100,
            train_step_counter=tf.Variable(0)
        )
        agent.initialize()
        return agent
    def _build_replay_buffer(self):
        return tf_uniform_replay_buffer.TFUniformReplayBuffer(
            self.agent.collect_data_spec,
            batch_size=self.train_env.batch_size,
            max_length=self.config.BUFFER_SIZE
        )
    def collect_data(self, steps: int):
        console.print("\n[bold blue]Collecting initial trading data...[/bold blue]")
        time_step = self.train_env.reset()
        policy_state = self.agent.collect_policy.get_initial_state(self.train_env.batch_size)
        
        for step in track(range(steps), description="Collecting experience"):
            action_step = self.agent.collect_policy.action(time_step, policy_state)
            next_time_step = self.train_env.step(action_step.action)
            traj = trajectory.from_transition(time_step, action_step, next_time_step)
            self.replay_buffer.add_batch(traj)
            time_step = next_time_step
            policy_state = action_step.state
    async def train(self) -> Tuple[float, ...]:
        console.print("\n[bold blue]Starting training...[/bold blue]")
        
        # Collect initial data
        self.collect_data(steps=1000)
        
        # Prepare training dataset
        dataset = self.replay_buffer.as_dataset(
            num_parallel_calls=3,
            sample_batch_size=32,
            num_steps=2
        ).prefetch(3)
        iterator = iter(dataset)
        # Initialize metrics
        losses = []
        running_reward = 0
        best_reward = float('-inf')
        trades_made = 0
        # Create stats table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Episode")
        table.add_column("Loss")
        table.add_column("Reward")
        table.add_column("Trades")
        table.add_column("Best Reward")
        with Live(table, refresh_per_second=4):
            for episode in range(self.config.TRAINING_EPISODES):
                experience, _ = next(iterator)
                loss = self.agent.train(experience).loss
                losses.append(loss)
                
                # Update metrics
                reward = float(experience.reward.numpy().mean())
                running_reward = 0.95 * running_reward + 0.05 * reward
                best_reward = max(best_reward, running_reward)
                trades_made += 1
                if episode % 10 == 0:
                    table.add_row(
                        str(episode),
                        f"{loss:.2f}",
                        f"{running_reward:.2f}",
                        str(trades_made),
                        f"{best_reward:.2f}"
                    )
        # Print final metrics
        console.print("\n[bold green]Training Complete![/bold green]")
        console.print(f"Final Loss: {losses[-1]:.2f}")
        console.print(f"Average Loss: {np.mean(losses):.2f}")
        console.print(f"Best Reward: {best_reward:.2f}")
        console.print(f"Total Trades: {trades_made}")
        
        return self.agent, losses
async def train_agent(TOKEN, ACCOUNT_ID, SYMBOL):
    # Initialize MetaApi client inside the async function
    meta_api = MetaApi(TOKEN)
    # Define time range for historical data
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    # Load historical data asynchronously
    data = await load_historical_data(meta_api, ACCOUNT_ID, SYMBOL, start_time, end_time)
    # Create and wrap the Gym environment with the data
    gym_env = ForexTradingEnvironment(data)
    wrapped_env = gym_wrapper.GymWrapper(gym_env)
    train_env = tf_py_environment.TFPyEnvironment(wrapped_env)
    # Load configuration
    config = Config()
    # Initialize TradingAgent
    trading_agent = TradingAgent(train_env, config)
    # Train the agent
    agent, losses = await trading_agent.train()
    # Return the trained agent and environment if needed
    return agent, train_env