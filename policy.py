import numpy as np

from DDPG.ActorNetwork import ActorNetwork
from DDPG.CriticNetwork import CriticNetwork

DEFAULT_LEARNING_RATE = 0.01
DEFAULT_DISCOUNT_FACTOR = 0.95


class Policy:
    def __init__(self, actor_input_dim, actor_action_dim, critic_input_dim, actor_learning_rate=DEFAULT_LEARNING_RATE,
                 critic_learning_rate=DEFAULT_LEARNING_RATE, discount_factor=DEFAULT_DISCOUNT_FACTOR):
        self.actor_learning_rate = actor_learning_rate
        self.critic_learning_rate = critic_learning_rate
        self.discount_factor = discount_factor
        self.actor_input_dim = actor_input_dim
        self.actor_action_dim = actor_action_dim
        self.actor_action_size = len(actor_action_dim)
        self.critic_input_dim = critic_input_dim
        self.value_size = 1
        # self.actor = ActorNetwork(input_dim=actor_input_dim, action_dim=actor_action_dim,
        #                           learning_rate=self.actor_learning_rate)
        # self.critic = CriticNetwork(input_dim=critic_input_dim, value_size=self.value_size,
        #                             learning_rate=self.critic_learning_rate)
        self.best_actor_action = ()

    def __repr__(self):
        return self.best_actor_action

    def best_action(self, state):
        self.best_actor_action = self.actor.get_action(state=state)
        # self.best_action = (
        #     0,
        #     0,
        #     0,
        #     0,
        #     0.0001, 0.0001, 0.0001, 1000,
        #     0.0001, 1000,
        #     -0.0001, 0.0001, 1000,
        #     0.0001, 0.0001, 1000,
        #     0.0001, 1000,
        #     0.0001, 1000,
        #     -0.0001, 0.0001, 1000,
        #     0.0001, 0.0001, 1000
        # )  # fit
        action = (
            (
                (4, self.best_actor_action[0]), (7, self.best_actor_action[1]), (10, self.best_actor_action[2]),
                (13, self.best_actor_action[3])
            ),  # revolute
            (
                (1, (self.best_actor_action[4], self.best_actor_action[5], self.best_actor_action[6]),
                 self.best_actor_action[7]),
                (2, (0, 0, self.best_actor_action[8]), self.best_actor_action[9]),
                (3, (self.best_actor_action[10], 0, self.best_actor_action[11]), self.best_actor_action[12]),
                (9, (self.best_actor_action[13], 0, self.best_actor_action[14]), self.best_actor_action[15]),
                (5, (0, 0, self.best_actor_action[16]), self.best_actor_action[17]),
                (11, (0, 0, self.best_actor_action[18]), self.best_actor_action[19]),
                (6, (self.best_actor_action[20], 0, self.best_actor_action[21]), self.best_actor_action[22]),
                (12, (self.best_actor_action[23], 0, self.best_actor_action[24]), self.best_actor_action[25])
            )  # spherical
        )
        return action

    def update(self, state, action, reward, next_state, done):
        target = np.zeros((1, self.value_size))
        advantages = np.zeros((1, self.actor_action_size))

        next_action = self.best_action(next_state)

        value = self.critic.predict(state=state, action=action)
        next_value = self.critic.predict(state=next_state, action=next_action)

        if done:
            advantages[0][action] = reward - value
            target[0][0] = reward
        else:
            advantages[0][action] = reward + self.discount_factor * next_value - value
            target[0][0] = reward + self.discount_factor * next_value

        self.actor.fit(state=state, advantages=advantages)
        self.critic.fit(state=state, action=action, target=target)
