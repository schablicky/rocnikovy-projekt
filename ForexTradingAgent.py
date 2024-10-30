import tensorflow as tf
from tf_agents.agents.dqn import dqn_agent
from tf_agents.environments import tf_py_environment
from tf_agents.networks import q_network
from tf_agents.policies import random_tf_policy
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.trajectories import trajectory
from tf_agents.utils import common

# Load environment
train_env = tf_py_environment.TFPyEnvironment(ForexTradingEnvironment(meta_api, symbol, start_time, end_time))

# Q-Network (approximator)
q_net = q_network.QNetwork(
    train_env.observation_spec(),
    train_env.action_spec(),
    fc_layer_params=(100, 50),
    activation_fn=tf.keras.activations.relu
)

# Agent
agent = dqn_agent.DqnAgent(
    train_env.time_step_spec(),
    train_env.action_spec(),
    q_network=q_net,
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    td_errors_loss_fn=common.element_wise_squared_loss,
    gamma=0.99,
    epsilon_greedy=0.1
)

# Replay Buffer
replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
    agent.collect_data_spec,
    batch_size=32,
    max_length=10000
)

# Data Collection
def collect_data(env, policy, buffer, steps):
    time_step = env.reset()
    policy_state = policy.get_initial_state(batch_size=1)
    for _ in range(steps):
        action_step = policy.action(time_step, policy_state)
        next_time_step = env.step(action_step.action)
        traj = trajectory.from_transition(time_step, action_step, next_time_step)
        buffer.add_batch(traj)
        time_step = next_time_step
        policy_state = action_step.state

# Train Agent
collect_data(train_env, agent.collect_policy, replay_buffer, 1000)

dataset = replay_buffer.as_dataset(num_epochs=1, batch_size=32)
iterator = iter(dataset)

for _ in range(1000):
    experience, _ = next(iterator)
    loss = agent.train(experience)
    print(f'Step: {_+1}, Loss: {loss}')