import numpy as np


class SphericalJoinInformation(object):
    def __init__(self, join_id: int, position: (float, float, float, float), join_torque: float,
                 limit: (float, float, float, float, float, float)):
        self.join_id: int = join_id
        self.position: (float, float, float, float) = position
        self.join_torque: float = join_torque
        self.limit: (float, float, float, float, float, float) = limit

    def change_position(self, position_to_set: (float, float, float)) -> None:
        self.position = (self.position[0] + (position_to_set[0] * 0.001),
                         self.position[1] + (position_to_set[1] * 0.001),
                         self.position[2] + (position_to_set[2] * 0.001),
                         self.position[3])
        self.apply_position_limit()

    def apply_position_limit(self) -> None:
        self.position = (np.clip(self.position[0], self.limit[0], self.limit[1]),
                         np.clip(self.position[1], self.limit[2], self.limit[3]),
                         np.clip(self.position[2], self.limit[4], self.limit[5]),
                         self.position[3])

    def set_torque(self, torque: float) -> None:
        self.join_torque = torque

    def to_tuple(self) -> tuple:
        return self.position[0], self.position[1], self.position[2], self.join_torque

    def __repr__(self) -> str:
        return f'{self.join_id}, ({self.position[0]}, {self.position[1]}, {self.position[2]}), {self.join_torque}'
