import math
import server.client_py_bullet as cpb
import pybullet_data

from object.floor import Floor
from object.human_body import HumanBody
from object.soccerball import Soccerball
from utils.Coordinate import Coordinate

REWARD_STAYING_ALIVE = 0.3

REWARD_HUMAN_CLOSER_GOAL_POSITIVE = 5
REWARD_HUMAN_STAYING_UP_POSITIVE = 1

REWARD_HUMAN_CLOSER_GOAL_NEGATIVE = -10
REWARD_HUMAN_STAYING_UP_NEGATIVE = -40
REWARD_HUMAN_JUMP_TO_MUCH_NEGATIVE = -50


class Environment(object):
    def __init__(self):
        self.client = cpb.ClientPyBullet(connection_mode=cpb.p.GUI)
        self.client.setAdditionalSearchPath(pybullet_data.getDataPath())
        self.client.setGravity(0, 0, -9.8)
        self.goal_coord = Coordinate(10, 0, 0)
        self.floor: Floor = self.add_floor()
        self.soccerball: Soccerball = self.add_soccerball()
        self.human: HumanBody = self.add_human()
        self.memory = {"distance_human_goal": self.get_distance_human_goal()}

    def add_floor(self):
        return Floor(self.client)

    def add_soccerball(self):
        return Soccerball(self.client, Coordinate(self.goal_coord.x, self.goal_coord.y, 0.15), 0.3)

    def add_human(self):
        human_start_pos = Coordinate(0, 0, 1.411)
        human_start_orientation = self.client.getQuaternionFromEuler([math.pi / 2, 0, 0])
        human = HumanBody(self.client, human_start_pos, human_start_orientation, 0.4)
        human.print_joints()

        human.initialise_motor_controls()
        human.initialise_motor_power()
        return human

    def reset_all_simulation(self):
        self.client.removeBody(self.human.body)
        self.client.removeBody(self.soccerball.body)
        self.client.removeBody(self.floor.body)
        self.floor = self.add_floor()
        self.soccerball = self.add_soccerball()
        self.human = self.add_human()
        self.memory = {"distance_human_goal": self.get_distance_human_goal()}

    def update_memory(self):
        self.memory = {"distance_human_goal": self.get_distance_human_goal()}

    def get_height_human_from_floor(self):
        (human_root_position, human_root_orientation) = self.human.get_position_orientation()
        floor_root_position = self.floor.get_position()
        return human_root_position[2] - floor_root_position[2]

    def get_distance_human_goal(self):
        (human_root_position, _) = self.human.get_position_orientation()
        human_coord = Coordinate(human_root_position[0], human_root_position[1], human_root_position[2])
        distance_from_goal = human_coord.abs_distance_from(self.goal_coord)
        return distance_from_goal

    def get_state(self):
        height_floor_human = round(self.human.get_position_orientation()[0][2], 4)
        joins_information = self.human.get_joins_information()
        joins_information["revolute"] = [(info[0], info[3]) for info in joins_information["revolute"]]
        joins_information["spherical"] = [info[0] + info[3] for info in joins_information["spherical"]]

        result = (height_floor_human,)
        for infos in joins_information.values():
            for info in infos:
                result += info

        return result

    def get_reward(self):
        # reward to stay alive
        reward = 1
        # body distance from goal
        new_distance_human_goal = self.get_distance_human_goal()
        if new_distance_human_goal < self.memory["distance_human_goal"]:
            reward += REWARD_HUMAN_CLOSER_GOAL_POSITIVE
        else:
            reward += REWARD_HUMAN_CLOSER_GOAL_NEGATIVE
        # body height from the ground
        # (<0.94 = lower than 2/3 of the maximum standing value (1.410))
        height_human_floor = self.get_height_human_from_floor()
        if height_human_floor >= 0.94:
            reward += REWARD_HUMAN_STAYING_UP_POSITIVE
        elif height_human_floor > 2:
            reward += REWARD_HUMAN_JUMP_TO_MUCH_NEGATIVE
        else:
            reward += REWARD_HUMAN_STAYING_UP_NEGATIVE
        return reward

    def is_human_on_goal(self):
        distance_from_goal = self.memory["distance_human_goal"]
        return distance_from_goal[0] < 0.2 and distance_from_goal[1] < 0.2

    def apply(self, action):
        self.human.apply_motor_power(information=action)
        self.client.stepSimulation()
        new_state = self.get_state()
        reward = self.get_reward()
        self.update_memory()
        done = self.is_human_on_goal()
        return new_state, reward, done

    @staticmethod
    def get_shape_state():
        return (
            # position du corps par rapport au sol
            0,
            # 4 jointures revolute avec position + force
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            # 8 jointures spherical avec position + force
            0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0,
        )

    def test(self):
        # height = round(self.human.get_position_orientation()[0][2] - 1.410, 4)
        # print(self.human.get_joins_information())
        self.human.apply_motor_power(information=(
            (
                (4, 0),
                (7, 0),
                (10, 0),
                (13, 0)
            ),  # revolute
            (
                (1, (0, 0, 0), 0),
                (2, (0, 0, 0), 0),
                (3, (0, 0, 0), 0),
                (9, (0, 0, 0), 0),
                (5, (0, 0, 0), 0),
                (11, (0, 0, 0), 0),
                (6, (0, 0, 0), 0),
                (12, (0, 0, 0), 0)
            )
        ))
