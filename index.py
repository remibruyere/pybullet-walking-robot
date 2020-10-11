import time
import pybullet_data
import server.client_py_bullet as cpb

if __name__ == "__main__":
    client = cpb.ClientPyBullet(connection_mode=cpb.p.GUI)
    client.setAdditionalSearchPath(pybullet_data.getDataPath())
    client.setGravity(0, 0, -9.8)
    client.setTimeStep(1e-3)

    # planeId = client.loadURDF("plane.urdf")
    # cubeStartPos = [0, 0, 1.13]
    # cubeStartOrientation = client.getQuaternionFromEuler([0., 0, 0])
    # botId = client.loadURDF("biped/biped2d_pybullet.urdf", cubeStartPos, cubeStartOrientation)
    #
    # # disable the default velocity motors
    # # and set some position control with small force to emulate joint friction/return to a rest pose
    # jointFrictionForce = 1
    # for joint in range(client.getNumJoints(botId)):
    #     client.setJointMotorControl2(botId, joint, client.POSITION_CONTROL, force=jointFrictionForce)
    #
    # # for i in range(10000):
    # #     p.setJointMotorControl2(botId, 1, p.TORQUE_CONTROL, force=1098.0)
    # #     p.stepSimulation()
    # # import ipdb
    # # ipdb.set_trace()
    # import time
    #
    # client.setRealTimeSimulation(1)
    # while (1):
    #     client.stepSimulation()
    #     client.setJointMotorControl2(botId, 1, client.TORQUE_CONTROL, force=1098.0)
    #     # client.setGravity(0, 0, -9.8)
    #     time.sleep(1 / 240.)
    # time.sleep(1000)

    planeId = client.loadURDF("plane.urdf")
    cubeStartPos = [0, 0, 0]
    cubeStartOrientation = client.getQuaternionFromEuler([0, 0, 0])
    boxId = client.loadURDF("biped/biped2d_pybullet.urdf", cubeStartPos, cubeStartOrientation)
    for i in range(10000):
        client.stepSimulation()
        client.setGravity(0, 0, -9.8)
        time.sleep(1. / 240.)
        cubePos, cubeOrn = client.getBasePositionAndOrientation(boxId)
        print(cubePos, cubeOrn)
    del client
