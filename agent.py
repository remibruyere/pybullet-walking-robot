from environment import Environment
from policy import Policy


class Agent(object):
    def __init__(self, environment: Environment):
        self.environment = environment
        self.state = self.environment.get_state()
        self.previous_state = self.state
        self.score = 0
        self.reward = 0
        self.last_action = None
        self.policy = Policy(actor_input_dim=self.environment.get_shape_state(),
                             actor_action_dim=self.get_shape_action(),
                             critic_input_dim=self.environment.get_shape_state() + self.get_shape_action())

    def reset(self):
        self.state = self.environment.get_state()
        self.previous_state = self.state
        self.score = 0
        self.reward = 0
        self.last_action = None

    def best_action(self):
        return self.policy.best_action(state=self.state)

    def do(self, action):
        self.previous_state = self.state
        self.state, self.reward = self.environment.apply(action=action)
        self.score += self.reward
        return self.environment.is_human_on_goal()

    def get_position_and_rotation(self):
        return self.environment.client.getBasePositionAndOrientation(self.environment.human.body)

    def update_policy(self, done):
        self.policy.update(state=self.previous_state, action=self.last_action, reward=self.reward,
                           next_state=self.state, done=done)

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
