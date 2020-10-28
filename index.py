import math
import time

import numpy as np
import pybullet_data
import server.client_py_bullet as cpb
from object.human_body import HumanBody
import pybullet as p

if __name__ == "__main__":
    client = cpb.ClientPyBullet(connection_mode=cpb.p.GUI)
    client.setAdditionalSearchPath(pybullet_data.getDataPath())
    client.setGravity(0, 0, -9.8)

    planeId = client.loadURDF("plane.urdf")

    ordered_joints = []
    ordered_joint_indices = []

    cubeStartPos = [0, 0, 1.411]
    cubeStartOrientation = client.getQuaternionFromEuler([math.pi / 2, 0, 0])
    human = HumanBody(client, cubeStartPos, cubeStartOrientation, 0.4)
    print(client.getNumJoints(human.body))
    for i in range(0, client.getNumJoints(human.body)):
        print(client.getJointInfo(human.body, i))

    jdict = {}
    for j in range(p.getNumJoints(human.body)):
        info = p.getJointInfo(human.body, j)
        link_name = info[12].decode("ascii")
        if link_name == "left_foot":
            left_foot = j
        if link_name == "right_foot":
            right_foot = j
        ordered_joint_indices.append(j)

        if info[2] != p.JOINT_REVOLUTE:
            continue
        jname = info[1].decode("ascii")
        jdict[jname] = j
        lower, upper = (info[8], info[9])
        ordered_joints.append((j, lower, upper))

        p.setJointMotorControl2(human.body, j, controlMode=p.VELOCITY_CONTROL, force=0)

    motor_names = []
    motor_power = []
    motor_names += ["right_knee", "left_knee"]
    motor_power += [200, 200]
    motor_names += ["right_elbow", "left_elbow"]
    motor_power += [75, 75]
    motors = [jdict[n] for n in motor_names]

    for i in range(10000):
        client.stepSimulation()
        forces = [0.] * len(motors)
        for m in range(len(motors)):
            limit = 15
            ac = np.clip(10, -limit, limit)
            # print(ac)
            forces[m] = motor_power[m] * ac * 0.082
        print(forces)
        p.setJointMotorControlArray(human.body, motors, controlMode=p.TORQUE_CONTROL, forces=forces)
        time.sleep(1. / 240.)
    cubePos, cubeOrn = client.getBasePositionAndOrientation(human.body)
    print(cubePos, cubeOrn)
    del client
