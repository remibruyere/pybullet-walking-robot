import pybullet as p
import functools
import inspect


class ClientPyBullet(object):
    """A wrapper of pybullet to manage client."""

    def __init__(self, connection_mode=None):
        """Create a new client and connect it to the simulation.
        Case:
            - if there is a actual server : connect to it directly
            - if there is no server : create a new graphical server
        """
        self._connection_mode = connection_mode
        if self._connection_mode is None:
            self._client = p.connect(p.SHARED_MEMORY)
            if self._client >= 0:
                return
            else:
                self._connection_mode = p.DIRECT
        self._client = p.connect(self._connection_mode)
        p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
        p.resetDebugVisualizerCamera(cameraDistance=5.0, cameraYaw=30.0, cameraPitch=-30.0,
                                     cameraTargetPosition=[6, 0, 0])

    def __del__(self):
        """Clean up connection if not already done."""
        if self._client >= 0:
            try:
                p.disconnect(self._client)
                self._client = -1
            except p.error:
                pass

    def __getattr__(self, name):
        """Inject the client id into all Bullet's functions."""
        attribute = getattr(p, name)
        if inspect.isbuiltin(attribute):
            attribute = functools.partial(attribute, physicsClientId=self._client)
        if name == "disconnect":
            self._client = -1
        return attribute
