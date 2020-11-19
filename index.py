import math
import time

from agent import Agent
from environment import Environment
from object.floor import Floor
from object.human_body import HumanBody

"""
    Mouvement possible par tour :
        - bouger une/les 12 articulations sur une infinité d'angle entre 1 et 3 axes
    
    Réseau de neuronne en entrée :
        - entrée : 
            - position du corps par rapport au sol - 3
            * position du corps par rapport à la ligne d'arrivée - 2
            - position / angle de toutes les articulations 
                - 4 (revolute (position x y z + force)) + 90 (spherical (positon x y z + angle x' y' z')))
        - sortie : 
            - tuple avec toutes les articulations (angles à ajouter et forces) 
                - 2 (revolute (force)) + 90 (spherical (angle x' y' z' + forces x y z)))
    
    Récompenses:
        - Réduction de la distance entre le milieu du corps et la ligne d'arrivée: {OUI: +5, NON: -2}
        pas ça - Tête reste au dessus des 2/3 de la taille du corps (rester debout): {OUI: +2, NON: -5}
    
    Récompenses avancées (optionels):
        - Coût d'un mouvement pris en compte (plus on bouge, plus on reçoit des récompenses négatives)
"""

if __name__ == "__main__":
    environment = Environment()

    agent = Agent(environment=environment)

    for i in range(10000):
        environment.client.stepSimulation()
        agent.do()
        print(agent.get_position_and_rotation())
        time.sleep(1. / 240.)
