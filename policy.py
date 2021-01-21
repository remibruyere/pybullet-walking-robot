import numpy as np
import tensorflow as tf

from DDPG.actor_network import ActorNetwork
from DDPG.critic_network import CriticNetwork
from DDPG.replay_buffer import ReplayBuffer
from utils.OrnsteinUhlenbeckActionNoise import OrnsteinUhlenbeckActionNoise

ACTOR_LEARNING_RATE = 1e-4
CRITIC_LEARNING_RATE = 1e-3
DEFAULT_DISCOUNT_FACTOR = 0.99


class Policy:
    def __init__(self, actor_input_dim, actor_action_dim, critic_input_dim, actor_learning_rate=ACTOR_LEARNING_RATE,
                 critic_learning_rate=CRITIC_LEARNING_RATE, discount_factor=DEFAULT_DISCOUNT_FACTOR,
                 max_memory_size=50000):
        self.actor_learning_rate = actor_learning_rate
        self.critic_learning_rate = critic_learning_rate
        self.discount_factor = discount_factor
        self.actor_input_dim = actor_input_dim
        self.actor_action_dim = actor_action_dim
        self.actor_action_size = len(self.actor_action_dim)
        self.critic_input_dim = critic_input_dim
        self.value_size = 1
        self.actor = ActorNetwork(input_dim=self.actor_input_dim, action_dim=self.actor_action_dim,
                                  learning_rate=self.actor_learning_rate)
        self.critic = CriticNetwork(input_dim=self.critic_input_dim, value_size=self.value_size,
                                    learning_rate=self.critic_learning_rate)
        self.actor_noise = OrnsteinUhlenbeckActionNoise(mu=np.array(actor_action_dim))
        self.memory = ReplayBuffer(max_memory_size)
        self.msle = tf.keras.losses.MeanSquaredLogarithmicError(reduction=tf.keras.losses.Reduction.SUM)

    def save_checkpoint(self):
        self.actor.save_checkpoint()
        self.critic.save_checkpoint()

    def load_checkpoint(self):
        self.actor.load_checkpoint()
        self.critic.load_checkpoint()

    def save_best(self):
        self.actor.save_best()
        self.critic.save_best()

    def load_best(self):
        self.actor.load_best()
        self.critic.load_best()

    @staticmethod
    def state_to_dataset(state):
        return np.array([state])

    def best_action(self, state):
        best_actor_action = self.actor.get_action(state=self.state_to_dataset(state))[0]
        best_actor_action = np.clip(best_actor_action + self.actor_noise(), -1, 1)
        return tuple(best_actor_action)

    def reduce_noise(self, gamma):
        self.actor_noise.update_dt(gamma)

    def _construct_training_set(self, replay):
        # Select states and new states from replay
        states = np.array([a + b for (a, b) in zip(replay[0], replay[1])])
        new_states = np.array([a + b for (a, b) in zip(replay[3], replay[1])])

        # Predict the expected utility of current state and new state
        q = self.critic.predict_on_batch(states)
        q_new = self.critic.predict_on_batch(new_states)

        replay_size = len(replay[0])
        x = np.empty((replay_size, len(self.actor_input_dim)))
        y = np.empty((replay_size, len(self.actor_action_dim)))

        # Construct training set
        for i in range(replay_size):
            state_r, reward_r, done_r = replay[0][i], replay[2][i], replay[4][i]
            if done_r:
                target = reward_r
            else:
                target = reward_r + self.discount_factor * q[i][0]
            x[i] = state_r
            y[i] = target

        return x, y, states

    def update(self, batch_size=64, number_update=5):
        losses = []
        for i in range(number_update):
            if len(self.memory) < batch_size:
                break

            replay_buffer = self.memory.sample(batch_size=batch_size)

            x, y, states_critic = self._construct_training_set(replay=replay_buffer)

            loss = self.actor.train_on_batch(x, y)
            self.critic.train_on_batch(states_critic, y)
            losses.append(loss)

        return losses
