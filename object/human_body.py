import numpy as np

from server.client_py_bullet import ClientPyBullet


class HumanBody(object):
    """Class to create a robot"""

    body = None

    def __init__(self, client: ClientPyBullet, base_position=None, base_orientation=None, scaling=1.0):
        if client is None:
            raise ValueError("client need to be defined")
        self.base_position = base_position
        self.base_orientation = base_orientation
        self.base_scaling = scaling
        self.client = client
        self.load_urdf()
        self.join_dict = {}
        self.ordered_joints = []
        self.motor_names = []
        self.motor_power = []
        self.motors = []

    def load_urdf(self):
        """Load URDF model from human xml file to create the body"""
        self.body = self.client.loadURDF("object/human.xml", self.base_position, self.base_orientation, 0, 0, 0,
                                         self.base_scaling)

    def print_joints(self):
        number_joins = self.client.getNumJoints(self.body)
        print("Number of joins = ", number_joins)
        print("Type of join:")
        print("- revolute", self.client.JOINT_REVOLUTE)
        print("- prismatic", self.client.JOINT_PRISMATIC)
        print("- spherical", self.client.JOINT_SPHERICAL)
        print("- planar", self.client.JOINT_PLANAR)
        print("- fixed", self.client.JOINT_FIXED)
        for i in range(number_joins):
            print(self.client.getJointInfo(self.body, i))

    def initialise_motor_controls(self):
        for j in range(self.client.getNumJoints(self.body)):
            info = self.client.getJointInfo(self.body, j)
            if info[2] != self.client.JOINT_REVOLUTE:
                continue
            join_name = info[1].decode("ascii")
            self.join_dict[join_name] = j
            lower, upper = (info[8], info[9])
            self.ordered_joints.append((j, lower, upper))

            self.client.setJointMotorControl2(self.body, j, controlMode=self.client.VELOCITY_CONTROL, force=0)

    def initialise_motor_power(self):
        self.motor_names += ["right_knee", "left_knee"]
        self.motor_power += [200, 200]
        self.motor_names += ["right_elbow", "left_elbow"]
        self.motor_power += [75, 75]
        self.motors = [self.join_dict[n] for n in self.motor_names]

    def apply_motor_power(self):
        forces = [0.] * len(self.motors)
        for m in range(len(self.motors)):
            limit = 15
            ac = np.clip(10, -limit, limit)
            forces[m] = self.motor_power[m] * ac * 0.082
        self.client.setJointMotorControlArray(self.body, self.motors, controlMode=self.client.TORQUE_CONTROL,
                                              forces=forces)
