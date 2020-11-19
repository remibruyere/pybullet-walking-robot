from typing import List

import numpy as np

from object.revolute_join_information import RevoluteJoinInformation
from object.spherical_join_information import SphericalJoinInformation
from server.client_py_bullet import ClientPyBullet


class HumanBody(object):
    """Class to create a robot"""

    body = None
    DEFAULT_MOTOR_FORCE = 1

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

    def get_position_orientation(self):
        return self.client.getBasePositionAndOrientation(self.body)

    def initialise_motor_controls(self):
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

    def initialise_motor_power(self):
        self.motor_name_revolute += ["right_knee", "left_knee"]
        self.motor_power_revolute += [200, 200]
        self.motor_name_revolute += ["right_elbow", "left_elbow"]
        self.motor_power_revolute += [75, 75]
        self.motors_revolute = [self.join_dict_revolute[n] for n in self.motor_name_revolute]

        self.motor_name_spherical += ["chest"]
        self.motor_power_spherical += [10]
        self.motor_name_spherical += ["neck"]
        self.motor_power_spherical += [10]
        self.motor_name_spherical += ["right_hip", "left_hip"]
        self.motor_power_spherical += [10, 10]
        self.motor_name_spherical += ["right_ankle", "left_ankle"]
        self.motor_power_spherical += [10, 10]
        self.motor_name_spherical += ["right_shoulder", "left_shoulder"]
        self.motor_power_spherical += [10, 10]
        self.motors_spherical = [self.join_dict_spherical[n] for n in self.motor_name_spherical]

    # Revolute join

    def get_force_right_knee(self):
        limit = 15
        ac = np.clip(10, -limit, limit)
        return self.motor_power_revolute[0] * ac * 0.082

    def get_force_left_knee(self):
        limit = 15
        ac = np.clip(10, -limit, limit)
        return self.motor_power_revolute[1] * ac * 0.082

    def get_force_right_elbow(self):
        limit = 15
        ac = np.clip(10, -limit, limit)
        return self.motor_power_revolute[2] * ac * 0.082

    def get_force_left_elbow(self):
        limit = 15
        ac = np.clip(10, -limit, limit)
        return self.motor_power_revolute[3] * ac * 0.082

    # Spherical join

    def get_new_state_spherical_join(self, join_id: int, position_to_add: (float, float, float), torque_to_add: float):
        join_state = self.client.getJointStateMultiDof(self.body, 1)
        join_information = SphericalJoinInformation(join_id=join_id, position=join_state[0], join_torque=join_state[3])
        join_information.add_to_position(position_to_add=position_to_add)
        join_information.set_torque(torque_to_add)
        print("before", join_state)
        print("after", join_information)
        return join_information

    # def get_new_position_chest(self, position_to_add: (float, float, float)):
    #     """Move chest
    #     - position_to_add = (tilt chest to the sides, chest rotation, chest forward / backward)
    #     """
    #     join_state = self.client.getJointStateMultiDof(self.body, 1)
    #     join_information = SphericalJoinInformation(join_id=1, position=join_state[0], join_torque=join_state[3])
    #     join_information.add_to_position(position_to_add=position_to_add)
    #     return join_information
    #     # return 1, (join_state[0] + position_to_add[0],  # Inclinaison sur les côtés
    #     #            join_state[1] + position_to_add[1],  # Rotation du torse
    #     #            join_state[2] + position_to_add[2],  # Torse vers l'avant / arrière
    #     #            join_state[3])  # Un poids ?
    #
    # def get_new_position_neck(self, position_to_add: (float, float, float)):
    #     """Move neck
    #     - position_to_add = neck forward / backward
    #     """
    #     join_state = self.client.getJointStateMultiDof(self.body, 2)
    #     join_information = SphericalJoinInformation(join_id=2, position=join_state[0], join_torque=join_state[3])
    #     join_information.add_to_position(position_to_add=position_to_add)
    #     return join_information
    #     # join_state = self.client.getJointStateMultiDof(self.body, 2)[0]
    #     # return 2, (join_state[0],  # Inclinaison du cou sur les côtés -> inutile
    #     #            join_state[1],  # Rotation de la tête -> inutile
    #     #            join_state[2] + position_to_add,  # Cou vers l'avant / arrière
    #     #            join_state[3])  # Un poids ?
    #
    # def get_new_position_hip_right(self, position_to_add: (float, float, float)):
    #     """Move hip
    #     - position_to_add = (tilt leg to the sides, leg forward / backward)
    #     """
    #     join_state = self.client.getJointStateMultiDof(self.body, 3)
    #     join_information = SphericalJoinInformation(join_id=3, position=join_state[0], join_torque=join_state[3])
    #     join_information.add_to_position(position_to_add=position_to_add)
    #     return join_information
    #     # join_state = self.client.getJointStateMultiDof(self.body, 3)[0]
    #     # return 3, (join_state[0] + position_to_add[0],  # Jambe vers l'exterieur
    #     #            join_state[1],  # Rotation de l'axe de la jambe -> inutile
    #     #            join_state[2] + position_to_add[1],  # Jambe vers l'avant / arrière
    #     #            join_state[3])  # Un poids ?
    #
    # def get_new_position_hip_left(self, position_to_add: (float, float, float)):
    #     """Move hip
    #     - position_to_add = (tilt leg to the sides, leg forward / backward)
    #     """
    #     join_state = self.client.getJointStateMultiDof(self.body, 9)
    #     join_information = SphericalJoinInformation(join_id=9, position=join_state[0], join_torque=join_state[3])
    #     join_information.add_to_position(position_to_add=position_to_add)
    #     return join_information
    #     # join_state = self.client.getJointStateMultiDof(self.body, 9)[0]
    #     # return 9, (join_state[0] + position_to_add[0],  # Jambe vers l'exterieur
    #     #            join_state[1],  # Rotation de l'axe de la jambe -> inutile
    #     #            join_state[2] + position_to_add[1],  # Jambe vers l'avant / arrière
    #     #            join_state[3])  # Un poids ?
    #
    # def get_new_position_ankle_right(self, position_to_add: (float, float, float)):
    #     """Move ankle
    #     - position_to_add = ankle forward / backward
    #     """
    #     join_state = self.client.getJointStateMultiDof(self.body, 5)
    #     join_information = SphericalJoinInformation(join_id=5, position=join_state[0], join_torque=join_state[3])
    #     join_information.add_to_position(position_to_add=position_to_add)
    #     return join_information
    #     # join_state = self.client.getJointStateMultiDof(self.body, 5)[0]
    #     # return 5, (join_state[0],  # Pied vers l'exterieur -> inutile
    #     #            join_state[1],  # Rotation du pied -> inutile
    #     #            join_state[2] + position_to_add,  # Pied vers l'avant / arrière
    #     #            join_state[3])  # Un poids ?
    #
    # def get_new_position_ankle_left(self, position_to_add: (float, float, float)):
    #     """Move ankle
    #     - position_to_add = ankle forward / backward
    #     """
    #     join_state = self.client.getJointStateMultiDof(self.body, 11)
    #     join_information = SphericalJoinInformation(join_id=11, position=join_state[0], join_torque=join_state[3])
    #     join_information.add_to_position(position_to_add=position_to_add)
    #     return join_information
    #     # join_state = self.client.getJointStateMultiDof(self.body, 11)[0]
    #     # return 11, (join_state[0],  # Pied vers l'exterieur -> inutile
    #     #             join_state[1],  # Rotation du pied -> inutile
    #     #             join_state[2] + position_to_add,  # Pied vers l'avant / arrière
    #     #             join_state[3])  # Un poids ?
    #
    # def get_new_position_shoulder_right(self, position_to_add: (float, float, float)):
    #     """Move shoulder
    #     - position_to_add = (tilt arms to the sides, arms forward / backward)
    #     """
    #     join_state = self.client.getJointStateMultiDof(self.body, 6)
    #     join_information = SphericalJoinInformation(join_id=6, position=join_state[0], join_torque=join_state[3])
    #     join_information.add_to_position(position_to_add=position_to_add)
    #     return join_information
    #     # join_state = self.client.getJointStateMultiDof(self.body, 6)[0]
    #     # return 6, (join_state[0] + position_to_add[0],  # Bras vers l'exterieur
    #     #            join_state[1],  # rotation de l'epaule -> inutile
    #     #            join_state[2] + position_to_add[1],  # Bras vers l'avant / arrière
    #     #            join_state[3])  # Un poids ?
    #
    # def get_new_position_shoulder_left(self, position_to_add: (float, float, float)):
    #     """Move shoulder
    #     - position_to_add = (tilt arms to the sides, arms forward / backward)
    #     """
    #     join_state = self.client.getJointStateMultiDof(self.body, 12)
    #     join_information = SphericalJoinInformation(join_id=12, position=join_state[0], join_torque=join_state[3])
    #     join_information.add_to_position(position_to_add=position_to_add)
    #     return join_information
    #     # join_state = self.client.getJointStateMultiDof(self.body, 12)[0]
    #     # return 12, (join_state[0] + position_to_add[0],  # Bras vers l'exterieur
    #     #             join_state[1],  # Rotation de l'epaule -> inutile
    #     #             join_state[2] + position_to_add[1],  # Bras vers l'avant / arrière
    #     #             join_state[3])  # Un poids ?

    def parse_information_to_join_information(self, information: tuple):
        return (
            [RevoluteJoinInformation(info[0], info[1]) for info in information[0]],
            [SphericalJoinInformation(info[0], info[1], info[2]) for info in information[1]]
        )

    def apply_motor_power(self, information: tuple):
        revolute_join_information, spherical_join_information = self.parse_information_to_join_information(information)
        # self.apply_power_revolute_join(joins_information=revolute_join_information)
        # print(spherical_join_information[0])
        self.apply_power_spherical_join(joins_information=spherical_join_information)
        # forces = [0.] * len(self.motors_revolute)
        # for m in range(len(self.motors_revolute)):
        #     limit = 15
        #     ac = np.clip(10, -limit, limit)
        #     forces[m] = self.motor_power_revolute[m] * ac * 0.082
        # self.client.setJointMotorControlArray(self.body, self.motors_revolute, controlMode=self.client.TORQUE_CONTROL,
        #                                       forces=forces)

        # forces = [0.] * len(self.motors_spherical)
        # for m in range(len(self.motors_spherical)):
        #     limit = 15
        #     ac = np.clip(10, -limit, limit)
        #     forces[m] = self.motor_power_spherical[m] * ac * 0.082

        # moves: [SphericalJoinInformation] = [
        #     self.get_new_position_chest((0.0001, 0.0001, 0.0001)),
        #     self.get_new_position_neck((0, 0, 0.0001)),
        #     self.get_new_position_hip_right((0.0001, 0, 0.0001)),
        #     self.get_new_position_hip_left((0.0001, 0, 0.0001)),
        #     self.get_new_position_ankle_right((0, 0, 0.0001)),
        #     self.get_new_position_ankle_left((0, 0, 0.0001)),
        #     self.get_new_position_shoulder_right((-0.0001, 0, 0.0001)),
        #     self.get_new_position_shoulder_left((0.0001, 0, 0.0001))
        # ]
        # join_indices = [move.join_id for move in moves]
        # target_positions = [move.position for move in moves]
        # target_velocities = [[0, 0, 0]] * len(target_positions)
        # kps = [1000] * len(target_positions)
        # kds = [1000] * len(target_positions)
        # forces = [[1000, 1000, 1000]] * len(target_positions)
        # # print(self.body, join_indices,
        # #       target_positions,
        # #       target_velocities,
        # #       self.client.POSITION_CONTROL,
        # #       kps,
        # #       kds,
        # #       forces)
        # self.client.setJointMotorControlMultiDofArray(self.body, join_indices,
        #                                               targetPositions=target_positions,
        #                                               targetVelocities=target_velocities,
        #                                               controlMode=self.client.POSITION_CONTROL,
        #                                               positionGains=kps,
        #                                               velocityGains=kds,
        #                                               forces=forces)

    def apply_power_revolute_join(self, joins_information: List[RevoluteJoinInformation]):
        def get_join_id(join_info):
            return join_info.join_id

        joins_information.sort(key=get_join_id)
        forces = [information.join_torque for information in joins_information]
        self.client.setJointMotorControlArray(self.body, self.motors_revolute, controlMode=self.client.TORQUE_CONTROL,
                                              forces=forces)

    def apply_power_spherical_join(self, joins_information: List[SphericalJoinInformation]):
        def get_join_id(join_info):
            return join_info.join_id

        joins_information.sort(key=get_join_id)
        moves: [SphericalJoinInformation] = [self.get_new_state_spherical_join(join_id=information.join_id,
                                                                               position_to_add=information.position,
                                                                               torque_to_add=information.join_torque)
                                             for information in joins_information]
        join_indices = [move.join_id for move in moves]
        target_positions = [move.position for move in moves]
        target_velocities = [[0, 0, 0]] * len(target_positions)
        kps = [1000] * len(target_positions)
        kds = [1000] * len(target_positions)
        forces = [[1000, 1000, 1000]] * len(target_positions)
        print(self.body, join_indices,
              target_positions,
              target_velocities,
              self.client.POSITION_CONTROL,
              kps,
              kds,
              forces)
        self.client.setJointMotorControlMultiDofArray(self.body, join_indices,
                                                      targetPositions=target_positions,
                                                      targetVelocities=target_velocities,
                                                      controlMode=self.client.POSITION_CONTROL,
                                                      positionGains=kps,
                                                      velocityGains=kds,
                                                      forces=forces)
