"""
For running algorithm
"""
import math
import time as _time
import numpy as np
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
        if np.random.rand() <= t / 100:
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
            elif nearbyNode[0].getPointerNode().getDistanceFromNode(nearbyNode[0]) > node[0].getDistanceFromNode(nearbyNode[0]):
                nearbyNode[0].getPointerNode().removePointerNode(nearbyNode[0])
                node[0].setPointerNode(nearbyNode[0])
                nearbyNode[0].setPointerNode(node[0])

    # In case; CM can't find any CH node nearby, so we need to brute force it
    # Find CH node in length of diagonal of area radius
    left_CM_node = list(filter(lambda x: not x[0].hasPointerNode(), field.getNodes('CM')))
    print("# CM node which can't associate with CH node in phase 3 :", len(left_CM_node))
    for node in left_CM_node:
        diagonal_length = (field.getSize()**2 + field.getSize()**2)**0.5
        for CH_node in field.getNearbyNodes(node[0], diagonal_length, 'CH'):
            if not node[0].hasPointerNode():
                node[0].setPointerNode(CH_node[0])
                CH_node[0].setPointerNode(node[0])
            elif node[0].getPointerNode().getDistanceFromNode(node[0]) > node[0].getDistanceFromNode(CH_node[0]):
                node[0].getPointerNode().removePointerNode(node[0])
                node[0].setPointerNode(CH_node[0])
                CH_node[0].setPointerNode(node[0])

def cluster_association_phase(field):
    """
    Phase 4
    Cluster Association Phase

    Cluster Members (CM) has to join or associate with the closest Cluster Header (CH)
    and send the packet which contains the residual energy value of that CM to the selected CH

    Cluster Header find the size of themselves by find the maximum distance between it and other CM
    and calculate average of residual energy of CM that associate with itself
    
    Args:
        field (Field): Field
    """
    CH_nodeList = field.getNodes('CH')

    # Find the size for each Cluster Header
    for node in field.getNodes('CH'):
        #print(node[0].getPosition())
        #print(node[0].updateSize())
        node[0].updateSize()

    print("# Node left in field (assume that we finish):", len(field.getNodes()))
    # Plot graph to simulate environments
    for node in field.getNodes('CH'):
        for member in node[0].getPointerNode():
            plt.plot([node[0].getX(), member.getX()], [node[0].getY(), member.getY()], color='r', alpha=0.7, linewidth=0.8)

    # Assume that we finish all phase and all node will consume energy
    nodeList, count = field.getNodes(), 0
    for i in range(len(nodeList)):
        nodeList[i][1] = 0 # delay
    
    for node in field.getNodes():
        node = node[0]
        if node.getType() == 'CH':
            # Energy consumptions at CH node
            size = len(node.getPointerNode())
            consume_energy = node.consume_receive() * size + \
                             node.consume_Eproc(len(node.getPointerNode())) + \
                             node.consume_transmit(node.getDistanceFromNode(field.getBaseStation()))
        elif node.getType() == 'CM':
            # Energy consumptions at CM node
            if node.getPointerNode():
                distance = node.getDistanceFromNode(node.getPointerNode())
            else:
                distance = node.getDistanceFromNode(field.getBaseStation())
            consume_energy = node.consume_transmit(distance)
        node.setEnergy(node.getEnergy() - consume_energy)
        if node.getEnergy() <= 0:
            field.deleteNode(node)
            del node

def cluster_confirmation_phase(field):
    """
    Phase 5
    Cluster Confirmation Phase

    Not started yet. Just note that is to-do list
    """
    pass

# This is main
if __name__ == "__main__":
    start_time = _time.time()
    start_loop = int(input('Start loop: '))
    final_loop = int(input('Final loop: '))
    for tc in range(start_loop, final_loop + 1):
        print('Testcase', tc)
        field = Field(100, 0.0125)
        left_node = []
        try:
            while len(field.getNodes()) > 0:
                print('\nRound:', len(left_node) + 1)
                CCH_election_phase(field, 20)
                CH_competition_phase(field, 10)
                cluster_announcement_phase(field, 10)
                cluster_association_phase(field)
                #field.printField(pic_id=0, showplot=1)
                left_node.append(len(field.getNodes()))
                field.resetNode()
        except:
            print("Something error --")
        print()
        plt.plot([0] + list(range(1, len(left_node) + 1)), [int(field.getDensity() * int(field.getSize())**2)] + left_node)
        plt.xlabel('Round')
        plt.ylabel('Node')
        plt.title("Node left per round")
        #plt.show()
        plt.savefig('sample_case_proc/%04d' % tc, dpi=300)
        plt.clf()
        del field
        print("------- END OF Testcase %d -------" % time)
    print("---------- END OF EXECUTION ----------")
    print("-- Using %s seconds --" % (_time.time() - start_time))
