from typing import List

from utils.revolute_join_information import RevoluteJoinInformation
from utils.spherical_join_information import SphericalJoinInformation
from server.client_py_bullet import ClientPyBullet
from utils.Coordinate import Coordinate


class HumanBody(object):
    """Class to create a robot"""

    body = None
    DEFAULT_MOTOR_FORCE = 1

    def __init__(self, client: ClientPyBullet, base_position: Coordinate, base_orientation=None, scaling=1.0):
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
        self.motor_limit_spherical = {}

    def load_urdf(self) -> None:
        """Load URDF model from human xml file to create the body"""
        self.body = self.client.loadURDF("object/human.xml",
                                         [self.base_position.x, self.base_position.y, self.base_position.z],
                                         self.base_orientation, 0, 0,
                                         self.client.URDF_MAINTAIN_LINK_ORDER + self.client.URDF_USE_SELF_COLLISION,
                                         self.base_scaling)

    def get_joins_information(self):
        information = {
            "revolute": list(self.client.getJointStates(self.body, self.join_dict_revolute.values())),
            "spherical": list(self.client.getJointStatesMultiDof(self.body, self.join_dict_spherical.values()))
        }
        return information

    def print_joints(self) -> None:
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

    def get_position_orientation(self):
        return self.client.getBasePositionAndOrientation(self.body)

    def initialise_motor_controls(self) -> None:
        """Store motor information"""
        for j in range(self.client.getNumJoints(self.body)):
            info = self.client.getJointInfo(self.body, j)
            if info[2] == self.client.JOINT_REVOLUTE:
                join_name = info[1].decode("ascii")
                self.join_dict_revolute[join_name] = j
                lower, upper = (info[8], info[9])
                self.ordered_joints.append((j, lower, upper))
                self.client.setJointMotorControl2(self.body, j, controlMode=self.client.TORQUE_CONTROL,
                                                  force=self.DEFAULT_MOTOR_FORCE)
            elif info[2] == self.client.JOINT_SPHERICAL:
                join_name = info[1].decode("ascii")
                self.join_dict_spherical[join_name] = j
                lower, upper = (info[8], info[9])
                self.ordered_joints.append((j, lower, upper))
                self.client.setJointMotorControlMultiDof(self.body, j, controlMode=self.client.TORQUE_CONTROL,
                                                         force=[self.DEFAULT_MOTOR_FORCE, self.DEFAULT_MOTOR_FORCE,
                                                                self.DEFAULT_MOTOR_FORCE])

    def initialise_motor_power(self) -> None:
        """Create array to store motor name and attached value of torque"""
        self.motor_name_revolute += ["right_knee", "right_elbow"]
        self.motor_power_revolute += [250, 150]
        self.motor_name_revolute += ["left_knee", "left_elbow"]
        self.motor_power_revolute += [250, 150]
        self.motors_revolute = [self.join_dict_revolute[n] for n in self.motor_name_revolute]

        self.motor_name_spherical += ["chest"]
        self.motor_power_spherical += [(200, 70)]  # (fix torque, variable torque)
        self.motor_name_spherical += ["neck"]
        self.motor_power_spherical += [(60, 10)]
        self.motor_name_spherical += ["right_hip"]
        self.motor_power_spherical += [(40, 40)]
        self.motor_name_spherical += ["right_ankle"]
        self.motor_power_spherical += [(60, 80)]
        self.motor_name_spherical += ["right_shoulder"]
        self.motor_power_spherical += [(30, 10)]
        self.motor_name_spherical += ["left_hip"]
        self.motor_power_spherical += [(40, 40)]
        self.motor_name_spherical += ["left_ankle"]
        self.motor_power_spherical += [(60, 80)]
        self.motor_name_spherical += ["left_shoulder"]
        self.motor_power_spherical += [(30, 10)]
        self.motors_spherical = [self.join_dict_spherical[n] for n in self.motor_name_spherical]

    def initialise_spherical_motor_axis_limit(self) -> None:
        self.motor_limit_spherical = {
            1: [-0.15, 0.15, -0.4, 0.4, -0.4, 0.4],
            2: [-0.45, 0.45, -0.2, 0.2, -0.3, 0.3],
            3: [-0.45, 0.05, -0.05, 0.05, -0.2, 0.95],
            9: [-0.05, 0.45, -0.05, 0.05, -0.2, 0.95],
            5: [-0.05, 0.05, -0.05, 0.05, -0.10, 0.05],
            11: [-0.05, 0.05, -0.05, 0.05, -0.10, 0.05],
            6: [-1, 0, -0.1, 0.1, -0.2, 0.95],
            12: [0, 1, -0.1, 0.1, -0.2, 0.95]
        }

    def apply_motor_power(self, information: tuple) -> None:
        """Apply information from environment to revolute and spherical join"""
        revolute_join_information, spherical_join_information = self.parse_information_to_join_information(information)
        self.apply_power_revolute_join(joins_information=revolute_join_information)
        self.apply_power_spherical_join(joins_information=spherical_join_information)

    @staticmethod
    def parse_information_to_join_information(information: tuple) -> (
            [RevoluteJoinInformation], [SphericalJoinInformation]):
        """Cast information from environment to usable information"""
        return (
            [RevoluteJoinInformation(info[0], info[1]) for info in information[0]],
            [SphericalJoinInformation(info[0], info[1], info[2], limit=None) for info in information[1]]
        )

    def get_new_state_spherical_join(self, join_id: int, position_to_add: (float, float, float),
                                     torque: float) -> SphericalJoinInformation:
        """
        Get SphericalJoinInformation with new postion and torque of the join
        :param join_id: Id of the join
        :param position_to_add: tuple that represent (tilt left / right, rotation, forward / backward)
        :param torque: torque of the join
        :return:
        """
        join_state = self.client.getJointStateMultiDof(self.body, join_id)
        join_information = SphericalJoinInformation(join_id=join_id, position=join_state[0], join_torque=join_state[3],
                                                    limit=self.motor_limit_spherical.get(join_id))
        join_information.change_position(position_to_set=position_to_add)
        join_information.set_torque(torque)
        return join_information

    def apply_power_revolute_join(self, joins_information: List[RevoluteJoinInformation]) -> None:
        """Apply revolute join information to pyBullet environment"""
        def get_join_id(join_info: RevoluteJoinInformation) -> int:
            return join_info.join_id

        joins_information.sort(key=get_join_id)
        forces = [a * b for a, b in
                  zip([information.join_torque for information in joins_information], self.motor_power_revolute)]
        self.client.setJointMotorControlArray(self.body, self.motors_revolute, controlMode=self.client.TORQUE_CONTROL,
                                              forces=forces)

    def apply_power_spherical_join(self, joins_information: List[SphericalJoinInformation]) -> None:
        """Apply spherical join information to pyBullet environment"""
        def get_join_id(join_info: SphericalJoinInformation) -> int:
            return join_info.join_id

        joins_information.sort(key=get_join_id)
        new_spherical_state = [self.get_new_state_spherical_join(join_id=information.join_id,
                                                                 position_to_add=information.position,
                                                                 torque=information.join_torque)
                               for information in joins_information]
        join_indices = [spherical_state.join_id for spherical_state in new_spherical_state]
        target_positions = [spherical_state.position for spherical_state in new_spherical_state]
        target_velocities = [[0, 0, 0]] * len(target_positions)
        kps = [1000] * len(target_positions)
        kds = [10] * len(target_positions)
        forces = [[spherical_state.join_torque * base_torque[1] + base_torque[0]] * 3 for spherical_state, base_torque
                  in zip(new_spherical_state, self.motor_power_spherical)]
        self.client.setJointMotorControlMultiDofArray(self.body, join_indices,
                                                      targetPositions=target_positions,
                                                      targetVelocities=target_velocities,
                                                      controlMode=self.client.POSITION_CONTROL,
                                                      positionGains=kps,
                                                      velocityGains=kds,
                                                      forces=forces)
