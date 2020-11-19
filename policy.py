import numpy as np
from sklearn.neural_network import MLPRegressor

DEFAULT_LEARNING_RATE = 1
DEFAULT_DISCOUNT_FACTOR = 0.1


class Policy:
    def __init__(self, learning_rate=DEFAULT_LEARNING_RATE, discount_factor=DEFAULT_DISCOUNT_FACTOR):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

        self.mlp = MLPRegressor(hidden_layer_sizes=(8,),
                                activation='tanh',
                                solver='sgd',
                                learning_rate_init=self.learning_rate,
                                max_iter=1,
                                warm_start=True)
        # self.mlp.fit((), ())  # TODO complete with input and output shape
        # self.q_vector = None

    def __repr__(self):
        return self.q_vector


"""
    def state_to_dataset(self, state):
        return np.array([[state[0] / self.maxX, state[1] / self.maxY]])

    def best_action(self, state):
        self.q_vector = self.mlp.predict(self.state_to_dataset(state))[0]  # Vérifier que state soit au bon format
        action = self.actions[np.argmax(self.q_vector)]
        return action

    def update(self, previous_state, state, last_action, reward):
        # Q(st, at) = Q(st, at) + learning_rate * (reward + discount_factor * max(Q(state)) - Q(st, at))
        maxQ = np.amax(self.q_vector)
        last_action = ACTIONS.index(last_action)
        print(self.q_vector, maxQ, self.q_vector[last_action])
        self.q_vector[last_action] += reward + self.discount_factor * maxQ

        inputs = self.state_to_dataset(previous_state)
        outputs = np.array([self.q_vector])
        self.mlp.fit(inputs, outputs)
"""
