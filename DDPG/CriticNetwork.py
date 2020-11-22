import os
import tensorflow as tf


class CriticNetwork(object):
    def __init__(self, input_dim, value_size=1, learning_rate=0.01, name="critic", output_dir="tmp/ddpg"):
        self.input_dim = input_dim
        self.input_size = len(self.input_dim)
        self.value_size = value_size
        self.learning_rate = learning_rate
        self.name = name
        self.output_dir = output_dir
        self.checkpoint_file = os.path.join(self.output_dir, name + '_ddpg')
        self.model = self._build_network()

    def _build_network(self):
        init_w = tf.random_normal_initializer(0., 0.001)
        init_b = tf.constant_initializer(0.01)
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(self.input_size, input_dim=self.input_dim, activation=tf.keras.activations.tanh,
                                  kernel_initializer=init_w, bias_initializer=init_b),
            tf.keras.layers.Dense(200, activation=tf.keras.activations.tanh,
                                  kernel_initializer=init_w, bias_initializer=init_b),
            tf.keras.layers.Dense(self.value_size, activation=tf.keras.activations.linear,
                                  kernel_initializer=tf.keras.initializers.he_uniform)
        ])
        model.summary()
        model.compile(loss=tf.keras.losses.mean_squared_error,
                      optimizer=tf.keras.optimizers.Adam(lr=self.learning_rate))
        return model

    def predict(self, state, action):
        return self.model.predict(state + action)

    def fit(self, state, action, target):
        self.model.fit(state + action, target, epochs=1, verbose=0)

    def save_checkpoint(self):
        print('----- CriticNetwork : Saving checkpoint -----')
        self.model.save_weights(self.output_dir + "/checkpoints/critic")

    def load_checkpoint(self):
        print('----- CriticNetwork : Load checkpoint -----')
        self.model = self._build_network()
        self.model.load_weights(self.output_dir + "/checkpoints/critic")

    def save_best(self):
        print('----- CriticNetwork : Saving best checkpoint -----')
        self.model.save_weights(self.output_dir + "/best/critic")

    def load_best(self):
        print('----- CriticNetwork : Load checkpoint -----')
        self.model = self._build_network()
        self.model.load_weights(self.output_dir + "/best/critic")