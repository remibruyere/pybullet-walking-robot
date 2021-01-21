import math
import server.client_py_bullet as cpb
import pybullet_data

from object.floor import Floor
from object.human_body import HumanBody
from object.soccerball import Soccerball
from utils.Coordinate import Coordinate

REWARD_STAYING_ALIVE = 1

REWARD_HUMAN_CLOSER_GOAL_POSITIVE = 40
REWARD_HUMAN_CLOSER_GOAL_NEGATIVE = -80

REWARD_HUMAN_AHEAD_LASER_WALL = 5
REWARD_HUMAN_BEHIND_LASER_WALL = -400

REWARD_HUMAN_STAYING_UP_POSITIVE = 3
REWARD_HUMAN_STAYING_UP_NEGATIVE = -40

REWARD_HUMAN_JUMP_TO_MUCH_NEGATIVE = -50

REWARD_Z_DERIVATION_CONST = 20


class Environment(object):
    def __init__(self):
        self.client = cpb.ClientPyBullet(connection_mode=cpb.p.GUI)
        self.client.setAdditionalSearchPath(pybullet_data.getDataPath())
        self.client.setGravity(0, 0, -9.8)
        self.goal_coord = Coordinate(10, 0, 0)
        self.floor: Floor = self.add_floor()
        self.soccerball: Soccerball = self.add_soccerball()
        self.human: HumanBody = self.add_human()
        self.laser_wall = -0.4
        self.memory = {"distance_human_goal": self.get_distance_human_goal()}

    def add_floor(self):
        return Floor(self.client)

    def add_soccerball(self):
        return Soccerball(self.client, Coordinate(self.goal_coord.x, self.goal_coord.y, 0.15), 0.3)

    def add_human(self):
        human_start_pos = Coordinate(0, 0, 1.411)
        human_start_orientation = self.client.getQuaternionFromEuler([math.pi / 2, 0, 0])
        human = HumanBody(self.client, human_start_pos, human_start_orientation, 0.4)

        human.initialise_motor_controls()
        human.initialise_motor_power()
        human.initialise_spherical_motor_axis_limit()
        return human

    def reset_all_simulation(self):
        self.client.removeBody(self.human.body)
        self.human = self.add_human()
        self.memory = {"distance_human_goal": self.get_distance_human_goal()}
        self.laser_wall = -0.4

    def update_memory(self):
        new_distance = self.get_distance_human_goal()
        if new_distance[0] > self.memory["distance_human_goal"][0]:
            self.memory = {"distance_human_goal": new_distance}

    def get_height_human_from_floor(self):
        (human_root_position, human_root_orientation) = self.human.get_position_orientation()
        floor_root_position = self.floor.get_position()
        return human_root_position[2] - floor_root_position[2]

    def get_distance_human_goal(self):
        human_root_position = self.human.get_position_orientation()[0]
        human_coord = Coordinate(human_root_position[0], human_root_position[2], human_root_position[1])
        distance_from_goal = human_coord.abs_distance_from(self.goal_coord)
        return distance_from_goal

    def get_distance_human_laser(self):
        human_root_position = self.human.get_position_orientation()[0]
        return self.laser_wall - human_root_position[0]

    def get_state(self):
        joins_information = self.human.get_joins_information()
        joins_information["revolute"] = [(info[0], info[3]) for info in joins_information["revolute"]]
        joins_information["spherical"] = [info[0] + info[3] for info in joins_information["spherical"]]
        human_position_orientation = self.human.get_position_orientation()

        result = []
        for infos in joins_information.values():
            for info in infos:
                for value in info:
                    result.append(value)
        for human_info in human_position_orientation:
            for value in human_info:
                result.append(value)
        for distance_goal in self.get_distance_human_goal():
            result.append(distance_goal)
        result.append(self.get_distance_human_laser())

        return tuple(result)

    def get_reward(self):
        reward = REWARD_STAYING_ALIVE

        reward += self.get_distance_goal_reward()
        reward += self.get_laser_reward()
        reward += self.get_human_stand_up_reward()
        reward += self.z_derivation_reward()

        return reward

    def get_distance_goal_reward(self):
        if self.get_distance_human_goal()[0] < self.memory["distance_human_goal"][0]:
            return REWARD_HUMAN_CLOSER_GOAL_POSITIVE + \
                   (REWARD_HUMAN_CLOSER_GOAL_POSITIVE * (self.goal_coord.x - self.get_distance_human_goal()[0])) * 0.1
        else:
            return REWARD_HUMAN_CLOSER_GOAL_NEGATIVE + \
                   (REWARD_HUMAN_CLOSER_GOAL_NEGATIVE * self.get_distance_human_goal()[0]) * 0.1

    def get_laser_reward(self):
        if self.laser_wall < self.human.get_position_orientation()[0][0]:
            return REWARD_HUMAN_AHEAD_LASER_WALL + \
                   (REWARD_HUMAN_AHEAD_LASER_WALL * self.get_distance_human_laser()) * 0.1
        else:
            return REWARD_HUMAN_BEHIND_LASER_WALL + \
                   (REWARD_HUMAN_BEHIND_LASER_WALL * self.get_distance_human_laser()) * 0.1

    def z_derivation_reward(self):
        return REWARD_Z_DERIVATION_CONST * self.human.get_position_orientation()[0][1]

    def get_human_stand_up_reward(self):
        # (<0.94 = lower than 2/3 of the maximum standing value (1.410))
        height_human_floor = self.get_height_human_from_floor()
        if 0.94 <= height_human_floor < 1.8:
            return REWARD_HUMAN_STAYING_UP_POSITIVE
        elif height_human_floor >= 1.8:
            return REWARD_HUMAN_JUMP_TO_MUCH_NEGATIVE
        else:
            return REWARD_HUMAN_STAYING_UP_NEGATIVE

    def is_human_on_goal(self):
        distance_from_goal = self.memory["distance_human_goal"]
        return distance_from_goal[0] < 0.5 and distance_from_goal[1] < 0.5

    def apply(self, action):
        self.human.apply_motor_power(information=action)
        self.client.stepSimulation()
        new_state = self.get_state()
        reward = self.get_reward()
        self.update_memory()
        self.laser_wall += 0.01
        done = self.is_human_on_goal()
        return new_state, reward, done

    @staticmethod
    def get_shape_state():
        return (
            # position du corps dans l'espace
            0, 0, 0,
            # distance du robot par rapport à l'arrivée
            0, 0, 0,
            # distance du robot par rapport au laser
            0,
            # orientation du corps dans l'espace
            0, 0, 0, 0,
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
                (4, 0),  # -1 et 0
                (7, 0),  # 0 et 1
                (10, 0),  # -1 et 0
                (13, 0)  # 0 et 1
            ),  # revolute
            (
                (1, (0, 0, 0), 0),
                (2, (0, 0, 0), 0),
                (3, (0, 0, 0), 0),
                (9, (0, 0, 0), 0),
                (5, (0, 0.05, 0), 0),
                (11, (0, 0, 0), 0),
                (6, (0, 0, 0), 0),
                (12, (0, 0, 0), 0)
            )
        ))
