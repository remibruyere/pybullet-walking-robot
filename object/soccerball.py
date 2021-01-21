from server.client_py_bullet import ClientPyBullet
from utils.Coordinate import Coordinate


class Soccerball(object):
    """Class to create a soccerball"""

    body = None

    def __init__(self, client: ClientPyBullet, base_position: Coordinate, scaling=1.0):
        if client is None:
            raise ValueError("client need to be defined")
        self.client = client
        self.base_position = base_position
        self.base_scaling = scaling
        self.load_urdf()

    def load_urdf(self):
        """Load URDF model from soccerball urdf file to create the body"""
        self.body = self.client.loadURDF("soccerball.urdf",
                                         [self.base_position.x, self.base_position.y, self.base_position.z],
                                         globalScaling=self.base_scaling)

    def get_position(self):
        """Get (X, Z, Y) position"""
        return self.client.getBasePositionAndOrientation(self.body)[0]
