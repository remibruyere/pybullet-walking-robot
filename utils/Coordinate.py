class Coordinate(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def distance_from(self, other_coord):
        return self.x - other_coord.x, self.y - other_coord.y, self.z - other_coord.z

    def abs_distance_from(self, other_coord) -> tuple:
        return abs(self.x - other_coord.x), abs(self.y - other_coord.y), abs(self.z - other_coord.z)
