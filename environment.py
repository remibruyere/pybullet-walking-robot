import math
import server.client_py_bullet as cpb
import pybullet_data

from object.floor import Floor
from object.human_body import HumanBody


class Environment(object):
    def __init__(self):
        self.client = cpb.ClientPyBullet(connection_mode=cpb.p.GUI)
        self.client.setAdditionalSearchPath(pybullet_data.getDataPath())
        self.client.setGravity(0, 0, -9.8)
        self.floor = self.add_floor()
        self.human = self.add_human()

    def add_floor(self):
        return Floor(self.client)

    def add_human(self):
        human_start_pos = [0, 0, 1.411]
        human_start_orientation = self.client.getQuaternionFromEuler([math.pi / 2, 0, 0])
        human = HumanBody(self.client, human_start_pos, human_start_orientation, 0.4)
        human.print_joints()

        human.initialise_motor_controls()
        human.initialise_motor_power()
        return human

    def get_height_human_from_floor(self):
        (human_root_position, human_root_orientation) = self.human.get_position_orientation()
        floor_root_position = self.floor.get_position()
        return human_root_position[2] - floor_root_position[2]

    def apply(self, state):
        return
