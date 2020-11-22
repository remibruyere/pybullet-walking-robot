import math
import server.client_py_bullet as cpb
import pybullet_data

from object.floor import Floor
from object.human_body import HumanBody
from object.soccerball import Soccerball
from utils.Coordinate import Coordinate


class Environment(object):
    def __init__(self):
        self.client = cpb.ClientPyBullet(connection_mode=cpb.p.GUI)
        self.client.setAdditionalSearchPath(pybullet_data.getDataPath())
        self.client.setGravity(0, 0, -9.8)
        self.goal_coord = Coordinate(10, 0, 0)
        self.floor: Floor = self.add_floor()
        self.soccerball: Soccerball = self.add_soccerball()
        self.human: HumanBody = self.add_human()

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

    def get_height_human_from_floor(self):
        (human_root_position, human_root_orientation) = self.human.get_position_orientation()
        floor_root_position = self.floor.get_position()
        return human_root_position[2] - floor_root_position[2]

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
        # hauteur corps par rapport au sol
        # < 1.410 = plus bas que le maximum debout
        # TODO: implement reward
        pass

    def apply(self, action):
        self.human.apply_motor_power(information=action)
        self.client.stepSimulation()
        return self.get_state(), self.get_reward()

    def is_human_on_goal(self):
        (human_root_position, _) = self.human.get_position_orientation()
        human_coord = Coordinate(human_root_position[0], human_root_position[1], human_root_position[2])
        distance_from_goal = human_coord.abs_distance_from(self.goal_coord)
        return distance_from_goal[0] < 0.2 and distance_from_goal[1] < 0.2

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
        height = round(self.human.get_position_orientation()[0][2] - 1.410, 4)
        print(self.human.get_joins_information())
