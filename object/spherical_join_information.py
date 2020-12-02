import math


class SphericalJoinInformation(object):
    def __init__(self, join_id: int, position: (float, float, float, float), join_torque: float):
        self.join_id: int = join_id
        self.position: (float, float, float, float) = position
        self.join_torque: float = join_torque

    def add_to_position(self, position_to_add: (float, float, float)) -> None:
        self.position = (self.position[0] + (position_to_add[0] * 0.001),
                         self.position[1] + (position_to_add[1] * 0.001),
                         self.position[2] + (position_to_add[2] * 0.001),
                         self.position[3])

    def set_torque(self, torque: float) -> None:
        self.join_torque = torque

    def to_tuple(self) -> tuple:
        return self.position[0], self.position[1], self.position[2], self.join_torque

    def __repr__(self) -> str:
        return f'{self.join_id}, ({self.position[0]}, {self.position[1]}, {self.position[2]}), {self.join_torque}'
