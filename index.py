import time
import matplotlib.pyplot as plt
import numpy as np

from agent import Agent
from environment import Environment

import tensorflow as tf
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

MAX_EPISODES = 10000

if __name__ == "__main__":
    environment = Environment()

    agent = Agent(environment=environment)

    max_best_score = 0
    score_history = []
    best_score_history = []
    average_best_score_history = []

    for j in range(1, MAX_EPISODES):
        environment.reset_all_simulation()
        agent.reset()
        best_score = None
        while not agent.done and agent.score > -2000:
            # agent.environment.client.stepSimulation()
            # agent.test()
            best_action = agent.best_action()
            agent.do(best_action)
            agent.update_policy()
            if best_score is None or best_score < agent.score:
                best_score = agent.score
            print("score", agent.score)
            time.sleep(1. / 240.)

        score_history.append(agent.score)
        best_score_history.append(best_score)
        average_best_score_history.append(np.mean(best_score_history))

        if max_best_score < best_score:
            # agent.policy.save_best()
            max_best_score = best_score

        if j % 20 == 19:
            plt.close()
            plt.plot(score_history)
            plt.plot(best_score_history)
            plt.plot(average_best_score_history)
            plt.show()
            # agent.policy.save_checkpoint()
