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
        self.join_dict_revolute = {}
        self.join_dict_spherical = {}
        self.ordered_joints = []
        self.motor_name_revolute = []
        self.motor_power_revolute = []
        self.motors_revolute = []
        self.motor_name_spherical = []
        self.motor_power_spherical = []
        self.motors_spherical = []

    def load_urdf(self):
        """Load URDF model from human xml file to create the body"""
        self.body = self.client.loadURDF("object/human.xml", self.base_position, self.base_orientation, 0, 0,
                                         self.client.URDF_MAINTAIN_LINK_ORDER + self.client.URDF_USE_SELF_COLLISION,
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
            if info[2] == self.client.JOINT_REVOLUTE:
                join_name = info[1].decode("ascii")
                self.join_dict_revolute[join_name] = j
                lower, upper = (info[8], info[9])
                self.ordered_joints.append((j, lower, upper))
                self.client.setJointMotorControl2(self.body, j, controlMode=self.client.VELOCITY_CONTROL, force=0)
            elif info[2] == self.client.JOINT_SPHERICAL:
                join_name = info[1].decode("ascii")
                self.join_dict_spherical[join_name] = j
                lower, upper = (info[8], info[9])
                self.ordered_joints.append((j, lower, upper))
                self.client.setJointMotorControlMultiDof(self.body, j, controlMode=self.client.POSITION_CONTROL,
                                                         targetPosition=[0, 0, 0], targetVelocity=[0, 0, 0],
                                                         force=[100])

    def initialise_motor_power(self):
        self.motor_name_revolute += ["right_knee", "left_knee"]
        self.motor_power_revolute += [200, 200]
        self.motor_name_revolute += ["right_elbow", "left_elbow"]
        self.motor_power_revolute += [75, 75]
        self.motors_revolute = [self.join_dict_revolute[n] for n in self.motor_name_revolute]

        self.motor_name_spherical += ["right_shoulder", "left_shoulder"]
        self.motor_power_spherical += [10, 10]
        self.motors_spherical = [self.join_dict_spherical[n] for n in self.motor_name_spherical]

    def apply_motor_power(self):
        # forces = [0.] * len(self.motors_revolute)
        # for m in range(len(self.motors_revolute)):
        #     limit = 15
        #     ac = np.clip(10, -limit, limit)
        #     forces[m] = self.motor_power_revolute[m] * ac * 0.082
        # self.client.setJointMotorControlArray(self.body, self.motors_revolute, controlMode=self.client.TORQUE_CONTROL,
        #                                       forces=forces)
        forces = [0.] * len(self.motors_spherical)
        for m in range(len(self.motors_spherical)):
            limit = 15
            ac = np.clip(10, -limit, limit)
            forces[m] = self.motor_power_spherical[m] * ac * 0.082
        print(forces, self.motors_spherical)
        kps = [100] * 2
        kds = [100] * 2
        joinState = self.client.getJointStateMultiDof(self.body, 6)[0]
        joinState2 = self.client.getJointStateMultiDof(self.body, 12)[0]
        print(joinState)
        # (Vers l'exterieur, rotation de l'epaule, vers l'avant, un poid ?)
        joinState = (joinState[0] - 0.0001, joinState[1], joinState[2] + 0.0001, joinState[3])
        joinState2 = (joinState2[0] + 0.0001, joinState2[1], joinState2[2] + 0.0001, joinState2[3])
        self.client.setJointMotorControlMultiDofArray(self.body, [6, 12],
                                                      targetPositions=[joinState, joinState2],
                                                      targetVelocities=[[0, 0, 0], [0, 0, 0]],
                                                      controlMode=self.client.POSITION_CONTROL,
                                                      positionGains=kps,
                                                      velocityGains=kds,
                                                      forces=[[1000, 1000, 1000], [1000, 1000, 1000]])
