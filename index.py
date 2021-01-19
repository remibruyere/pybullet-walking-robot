import time
import matplotlib.pyplot as plt

from agent import Agent
from environment import Environment

import tensorflow as tf
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

"""
    Mouvement possible par tour :
        - bouger une/les 12 articulations sur une infinité d'angle entre 1 et 3 axes
    
    Réseau de neuronne en entrée :
        - entrée : 
            - position du corps par rapport au sol - 3
            * position du corps par rapport à la ligne d'arrivée - 2
            - position / angle de toutes les articulations 
                - 4 (revolute (position x y z + force)) + 64 (spherical (positon x y z + angle x' y' z')))
        - sortie : 
            - tuple avec toutes les articulations (angles à ajouter et forces) 
                - 4 (revolute (force)) + 64 (spherical (angle x' y' z' + force)))
    
    Récompenses:
        - Réduction de la distance entre le milieu du corps et la ligne d'arrivée: {OUI: +5, NON: -2}
        pas ça - Tête reste au dessus des 2/3 de la taille du corps (rester debout): {OUI: +2, NON: -5}
    
    Récompenses avancées (optionels):
        - Coût d'un mouvement pris en compte (plus on bouge, plus on reçoit des récompenses négatives)
"""

MAX_EPISODES = 100
LEARNING_RATE = 0.01
DISCOUNT_RATE = 0.95

if __name__ == "__main__":
    environment = Environment()

    agent = Agent(environment=environment)

    score_history = []
    best_score_history = []

    for j in range(1, MAX_EPISODES):
        environment.reset_all_simulation()
        agent.reset()
        best_score = None
        # agent noise reset
        while not agent.done and agent.score > -400:
            agent.environment.client.stepSimulation()
            # agent.test()
            best_action = agent.best_action()
            # print(best_action)
            agent.do(best_action)
            agent.update_policy()
            if best_score is None or best_score < agent.score:
                best_score = agent.score
            # print("score", agent.score)
            time.sleep(1. / 240.)

        score_history.append(agent.score)
        best_score_history.append(best_score)

        if j % 20 == 0:
            plt.close()
            plt.plot(score_history)
            plt.plot(best_score_history)
            plt.show()
            # save models
