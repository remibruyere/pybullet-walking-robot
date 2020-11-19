from environment import Environment
from policy import Policy


class Agent(object):
    def __init__(self, environment: Environment):
        self.environment = environment
        self.policy = Policy()
        self.reset()

    def reset(self):
        self.state = None  # TODO : get state start
        self.previous_state = self.state
        self.score = 0

    def best_action(self):
        return self.policy.best_action(self.state)

    def do(self):
        information = (
            (
                # (4, 0), (7, 0), (10, 0), (13, 0)
            ),  # revolute
            (
                # (1, (0.0001, 0.0001, 0.0001), 1000),
                # (2, (0, 0, 0.0001), 1000),
                # (3, (0.0001, 0, 0.0001), 1000),
                # (9, (0.0001, 0, 0.0001), 1000),
                # (5, (0, 0, 0.0001), 1000),
                # (11, (0, 0, 0.0001), 1000),
                # (6, (-0.0001, 0, 0.0001), 1000),
                (12, (0.0001, 0, 0.0001), 1000),
            )  # spherical
        )
        self.environment.human.apply_motor_power(information=information)
        self.environment.apply(None)
        # self.previous_state = self.state
        # self.state, self.reward = self.environment.apply(self.state)
        # self.score += self.reward

    def get_position_and_rotation(self):
        return self.environment.client.getBasePositionAndOrientation(self.environment.human.body)
