from environment import Environment
from policy import Policy


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

    @staticmethod
    def raw_action_to_usable_action(action):
        return (
            (
                (4, action[0]), (7, action[1]), (10, action[2]), (13, action[3])
            ),  # revolute
            (
                (1, (action[4], action[5], action[6]), action[7]),
                (2, (0, 0, action[8]), action[9]),
                (3, (action[10], 0, action[11]), action[12]),
                (9, (action[13], 0, action[14]), action[15]),
                (5, (0, 0, action[16]), action[17]),
                (11, (0, 0, action[18]), action[19]),
                (6, (action[20], 0, action[21]), action[22]),
                (12, (action[23], 0, action[24]), action[25])
            )  # spherical
        )

    def best_action(self):
        self.best_action_raw = self.policy.best_action(state=self.state)
        return self.raw_action_to_usable_action(self.best_action_raw)

    def do(self, action):
        self.previous_state = self.state
        self.state, self.reward, self.done = self.environment.apply(action=action)
        self.score += self.reward

    def get_position_and_rotation(self):
        return self.environment.client.getBasePositionAndOrientation(self.environment.human.body)

    def update_policy(self):
        self.policy.update(previous_state=self.previous_state, action=self.best_action_raw, reward=self.reward,
                           new_state=self.state, done=self.done)

    @staticmethod
    def get_shape_action():
        return (
            # 4 jointures revolute avec force
            0,
            0,
            0,
            0,
            # 8 jointures spherical avec angle + force
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
        )

    def test(self):
        self.environment.test()
