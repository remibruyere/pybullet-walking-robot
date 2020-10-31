import math
import time
import pybullet_data
import server.client_py_bullet as cpb
from object.floor import Floor
from object.human_body import HumanBody

if __name__ == "__main__":
    client = cpb.ClientPyBullet(connection_mode=cpb.p.GUI)
    client.setAdditionalSearchPath(pybullet_data.getDataPath())
    client.setGravity(0, 0, -9.8)

    planeId = Floor(client)

    humanStartPos = [0, 0, 1.411]
    humanStartOrientation = client.getQuaternionFromEuler([math.pi / 2, 0, 0])
    human = HumanBody(client, humanStartPos, humanStartOrientation, 0.4)
    human.print_joints()

    human.initialise_motor_controls()
    human.initialise_motor_power()

    for i in range(10000):
        client.stepSimulation()
        # human.apply_motor_power()
        time.sleep(1. / 240.)

    cubePos, cubeOrn = client.getBasePositionAndOrientation(human.body)
    print(cubePos, cubeOrn)
    del client
