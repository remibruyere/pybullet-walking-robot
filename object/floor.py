from server.client_py_bullet import ClientPyBullet


class Floor(object):
    """Class to create a floor"""

    body = None

    def __init__(self, client: ClientPyBullet):
        if client is None:
            raise ValueError("client need to be defined")
        self.client = client
        self.load_urdf()

    def load_urdf(self):
        """Load URDF model from plane urdf file to create the body"""
        self.body = self.client.loadURDF("plane.urdf")

    def get_position(self):
        return self.client.getBasePositionAndOrientation(self.body)[0]
