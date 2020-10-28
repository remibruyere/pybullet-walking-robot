from server.client_py_bullet import ClientPyBullet


class HumanBody(object):
    """Class to create a robot"""

    body = None

    def __init__(self, client: ClientPyBullet, base_position=None, base_orientation=None, scaling=1.0):
        self.base_position = base_position
        self.base_orientation = base_orientation
        self.base_scaling = scaling
        self.load_urdf(client)

    def load_urdf(self, client: ClientPyBullet):
        """Load URDF model from human xml file to create the body"""
        self.body = client.loadURDF("object/human.xml", self.base_position, self.base_orientation, 0, 0, 0,
                                    self.base_scaling)
