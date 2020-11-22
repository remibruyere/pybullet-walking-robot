class RevoluteJoinInformation(object):
    def __init__(self, join_id: int, join_torque: float):
        self.join_id: int = join_id
        self.join_torque = join_torque

    def set_join_torque(self, torque: float) -> None:
        self.join_torque = torque

    def to_tuple(self) -> float:
        return self.join_torque

    def __repr__(self) -> str:
        return f'{self.join_id}, {self.join_torque}'
