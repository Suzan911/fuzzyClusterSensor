"""
For running algorithm
"""
import math
import random as rand
import matplotlib.pyplot as plt
import matplotlib.markers as mark
from Field import Field
from Node import Node

def CCH_election_phase(field, t):
    """
    Phase 1
    CCH Election Phase

    Random select node to be a Candidate Claster Header (CCH)

    Args:
        field (Field): Field
        t     (float): Probability to promote node to be a Candidate Claster Header (CCH)
    """
    nodeList, count = field.getNodes(), 0
    for i in range(len(nodeList)):
        if rand.random() <= t / 100:
            nodeList[i][0].setType('CCH')
            # Exploit : In first round, every node have same amount of energy how we decide which one to be CCH
            # Solution: Define starting node that be implant at initial energy +- 0.01
            nodeList[i][1] = (field.getInitEnergy() - nodeList[i][0].getEnergy()) / field.getInitEnergy() * 10 # delay
            count += 1
    # We wouldn't update nodes list because it stored it in object
    #field.updateNodes(nodeList)
    print("# Amount of Candidate Claster Header in Phase 1 =", count)

def CH_competition_phase(field, radius):
    """
    Phase 2
    CH Competition Phase
    
    Compate Candidate Claster Header (CCH) which node much more energy than, then sleep the other nodes around

    Args:
        field  (Field): Field
        radius (float): Radius around CCH nodes
    """
    CCH_nodeList, count = field.getNodes('CCH'), 0
    CCH_nodeList = sorted(field.getNodes('CCH'), key=lambda x: x[1], reverse=False)
    for node in CCH_nodeList:
        if node[0].getType() == 'CCH':
            for nearbyNode in field.getNearbyNodes(node[0], radius, 'CCH'):
                if nearbyNode[0] > node[0]:
                    node[0].setType('CM')
                    break
                else:
                    nearbyNode[0].setType('CM')
            if node[0].getType() == 'CCH':
                node[0].setType('CH')
                count += 1
    print("# Amount of Claster Header in Phase 2 =", count)


def cluster_announcement_phase(field, radius):
    """
    Phase 3
    Cluster Announcement Phase

    Cluster Header (CH) announce around themselves for make Cluster Members to pointer at them

    Args:
        field  (Field): Field
        radius (float): Radius around CH nodes
    """
    alpha_radius = math.sqrt(2 * math.log(10)) * radius
    CH_nodeList = field.getNodes('CH')
    for node in CH_nodeList:
        for nearbyNode in field.getNearbyNodes(node[0], alpha_radius, 'CM'):
            if not nearbyNode[0].hasPointerNode():
                node[0].setPointerNode(nearbyNode[0])
                nearbyNode[0].setPointerNode(node[0])
            elif nearbyNode[0].getPointerNode()[0].getDistanceFromNode(nearbyNode[0]) > node[0].getDistanceFromNode(nearbyNode[0]):
                nearbyNode[0].getPointerNode()[0].removePointerNode(nearbyNode[0])
                node[0].setPointerNode(nearbyNode[0])
                nearbyNode[0].setPointerNode(node[0])

    # In case; CM can't find any CH node nearby, so we need to brute force it
    # Find CH node in length of diagonal of area radius
    left_CM_node = list(filter(lambda x: not x[0].hasPointerNode(), field.getNodes('CM')))
    print("# CM node left in phase 3 :", len(left_CM_node))
    for node in left_CM_node:
        diagonal_length = (field.getSize()**2 + field.getSize()**2)**0.5
        for CH_node in field.getNearbyNodes(node[0], diagonal_length, 'CH'):
            if not node[0].hasPointerNode():
                node[0].setPointerNode(CH_node[0])
                CH_node[0].setPointerNode(node[0])
            elif node[0].getPointerNode()[0].getDistanceFromNode(node[0]) > node[0].getDistanceFromNode(CH_node[0]):
                node[0].getPointerNode()[0].removePointerNode(node[0])
                node[0].setPointerNode(CH_node[0])
                CH_node[0].setPointerNode(node[0])

    for node in CH_nodeList:
        for member in node[0].getPointerNode():
            plt.plot([node[0].getX(), member.getX()], [node[0].getY(), member.getY()], 'r,-')

def cluster_association_phase(field):
    """
    Phase 4
    Cluster Association Phase
    """
    pass

def cluster_confirmation_phase(field):
    """
    Phase 5
    Cluster Confirmation Phase
    """
    pass

# This is main
if __name__ == "__main__":
    field = Field(100, 0.0125)
    CCH_election_phase(field, 20)
    CH_competition_phase(field, 10)
    cluster_announcement_phase(field, 10)
    field.printField()

