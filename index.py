import time
import pybullet_data
import server.client_py_bullet as cpb

if __name__ == "__main__":
    client = cpb.ClientPyBullet(connection_mode=cpb.p.GUI)
    client.setAdditionalSearchPath(pybullet_data.getDataPath())
    client.setGravity(0, 0, -10)

    planeId = client.loadURDF("plane.urdf")
    cubeStartPos = [0, 0, 1]
    cubeStartOrientation = client.getQuaternionFromEuler([0, 0, 0])
    boxId = client.loadURDF("r2d2.urdf", cubeStartPos, cubeStartOrientation)
    for i in range(10000):
        client.stepSimulation()
        time.sleep(1. / 240.)
        cubePos, cubeOrn = client.getBasePositionAndOrientation(boxId)
        print(cubePos, cubeOrn)
    del client
