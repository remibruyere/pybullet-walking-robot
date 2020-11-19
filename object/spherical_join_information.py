class SphericalJoinInformation(object):
    def __init__(self, join_id: int, position: (float, float, float, float), join_torque: float):
        print(join_id, position, join_torque)
        self.join_id: int = join_id
        self.position: (float, float, float, float) = position
        self.join_torque: float = join_torque

    def add_to_position(self, position_to_add: (float, float, float)):
        print("to add", position_to_add)
        self.position = (self.position[0] + position_to_add[0],
                         self.position[1] + position_to_add[1],
                         self.position[2] + position_to_add[2],
                         self.position[3])

    def set_torque(self, torque: float):
        self.join_torque = torque

    def to_tuple(self):
        return self.position[0], self.position[1], self.position[2], self.join_torque

    def __repr__(self):
        return f'{self.join_id}, ({self.position[0]}, {self.position[1]}, {self.position[2]}), {self.join_torque}'
