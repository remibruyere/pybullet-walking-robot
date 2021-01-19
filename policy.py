import numpy as np

from DDPG.ActorNetwork import ActorNetwork
from DDPG.CriticNetwork import CriticNetwork

DEFAULT_LEARNING_RATE = 3e-4
DEFAULT_DISCOUNT_FACTOR = 0.95


class Policy:
    def __init__(self, actor_input_dim, actor_action_dim, critic_input_dim, actor_learning_rate=DEFAULT_LEARNING_RATE,
                 critic_learning_rate=DEFAULT_LEARNING_RATE, discount_factor=DEFAULT_DISCOUNT_FACTOR):
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
        return tuple(best_actor_action)

    def update(self, previous_state, action, reward, new_state, done):
        target = np.zeros((1, self.value_size))

        next_action = self.best_action(new_state)

        value = self.critic.predict(state=self.state_to_dataset(previous_state + action))[0]
        next_value = self.critic.predict(state=self.state_to_dataset(new_state + next_action))[0]

        # print(value, next_value)

        if done:
            advantages = np.full(self.actor_action_size, reward - value)
            target[0][0] = reward
        else:
            advantages = np.full((1, self.actor_action_size), reward + self.discount_factor * next_value - value)
            target[0][0] = reward + self.discount_factor * next_value

        self.actor.fit(state=self.state_to_dataset(previous_state), advantages=advantages)
        self.critic.fit(state=self.state_to_dataset(previous_state + action), target=target)
