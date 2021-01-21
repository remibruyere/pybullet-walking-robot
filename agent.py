from environment import Environment
from policy import Policy

NOISE_REDUCE = 0.99


class Agent(object):
    def __init__(self, environment: Environment):
        self.environment = environment
        self.state = self.environment.get_state()
        self.previous_state = self.state
        self.score = 0
        self.reward = 0
        self.best_action_raw = None
        self.done = False
        self.policy = Policy(actor_input_dim=self.environment.get_shape_state(),
                             actor_action_dim=self.get_shape_action(),
                             critic_input_dim=self.environment.get_shape_state() + self.get_shape_action())

    def reset(self):
        self.state = self.environment.get_state()
        self.previous_state = self.state
        self.score = 0
        self.reward = 0
        self.best_action_raw = None
        self.done = False
        self.policy.reduce_noise(NOISE_REDUCE)

    @staticmethod
    def raw_action_to_usable_action(action):
        """Parse action from actor model prediction to usable action"""
        return (
            (
                (4, action[0]), (7, action[1]), (10, action[2]), (13, action[3])
            ),  # revolute
            (
                (1, (action[4], action[5], action[6]), action[7]),
                (2, (action[8], action[9], action[10]), action[11]),
                (3, (action[12], action[13], action[14]), action[15]),
                (9, (action[16], action[17], action[18]), action[19]),
                (5, (action[20], action[21], action[22]), action[23]),
                (11, (action[24], action[25], action[26]), action[27]),
                (6, (action[28], action[29], action[30]), action[31]),
                (12, (action[32], action[33], action[34]), action[35])
            )  # spherical
        )

    def best_action(self):
        """Get current best action to do"""
        self.best_action_raw = self.policy.best_action(state=self.state)
        return self.raw_action_to_usable_action(self.best_action_raw)

    def do(self, action):
        """Apply action to the environment and get new state, reward and done or not"""
        self.previous_state = self.state
        self.state, self.reward, self.done = self.environment.apply(action=action)
        self.score += self.reward

    def update_policy(self):
        """Add action done to replay buffer and update policy with replay buffer"""
        self.policy.memory.push(self.state, self.best_action_raw, self.reward, self.previous_state, self.done)
        return self.policy.update()

    @staticmethod
    def get_shape_action():
        """Get empty tuple that represent action shape"""
        return (
            # 4 revolute join with torque
            0,
            0,
            0,
            0,
            # 8 spherical join with position and torque
            0, 0, 0, 0,  # 1 x y z t
            0, 0, 0, 0,  # 2 x y z t
            0, 0, 0, 0,  # 3 x y z t
            0, 0, 0, 0,  # 5 x z t
            0, 0, 0, 0,  # 6 x y z t
            0, 0, 0, 0,  # 9 x y z t
            0, 0, 0, 0,  # 11 x z t
            0, 0, 0, 0,  # 12 x y z t
        )

    def test(self):
        self.environment.test()
