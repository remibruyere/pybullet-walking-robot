import os
import tensorflow as tf


class ActorNetwork(object):
    def __init__(self, input_dim, action_dim, learning_rate=0.01, name="actor", output_dir="tmp/ddpg"):
        self.input_dim = input_dim
        self.input_size = len(self.input_dim)
        self.action_dim = action_dim
        self.action_size = len(self.action_dim)
        self.learning_rate = learning_rate
        self.name = name
        self.output_dir = output_dir
        self.checkpoint_file = os.path.join(self.output_dir, name + '_ddpg')
        self.model = self._build_network()

    def _build_network(self):
        init_w = tf.random_normal_initializer(0., 0.01)
        init_b = tf.constant_initializer(0.01)
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(self.input_size, input_dim=self.input_dim, activation=tf.keras.activations.tanh,
                                  kernel_initializer=init_w, bias_initializer=init_b),
            tf.keras.layers.Dense(200, activation=tf.keras.activations.tanh,
                                  kernel_initializer=init_w, bias_initializer=init_b),
            tf.keras.layers.Dense(self.action_size, activation=tf.nn.softmax,
                                  kernel_initializer=tf.keras.initializers.he_uniform)
        ])
        model.summary()
        model.compile(loss=tf.keras.losses.categorical_crossentropy,
                      optimizer=tf.keras.optimizers.Adam(lr=self.learning_rate))
        return model

    def get_action(self, state):
        return self.model.predict(state, batch_size=1)

    def fit(self, state, advantages):
        self.model.fit(state, advantages, epochs=1, verbose=0)

    def save_checkpoint(self):
        print('----- ActorNetwork : Saving checkpoint -----')
        self.model.save_weights(self.output_dir + "/checkpoints/actor")

    def load_checkpoint(self):
        print('----- ActorNetwork : Load checkpoint -----')
        self.model = self._build_network()
        self.model.load_weights(self.output_dir + "/checkpoints/actor")

    def save_best(self):
        print('----- ActorNetwork : Saving best checkpoint -----')
        self.model.save_weights(self.output_dir + "/best/actor")

    def load_best(self):
        print('----- ActorNetwork : Load checkpoint -----')
        self.model = self._build_network()
        self.model.load_weights(self.output_dir + "/best/actor")
