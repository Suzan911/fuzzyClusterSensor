"""
For running algorithm
"""
import math
import os
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
    for node in nodeList:
        node.setDelay(0)
        node.setState('active')
        if np.random.rand() <= node.getT():
            node.setType('CCH')
            # Exploit : In first round, every node have same amount of energy how we decide which one to be CCH
            # Solution: Define starting node that be implant at initial energy +- 0.01
            node.setDelay((field.getInitEnergy() - node.getEnergy()) / field.getInitEnergy() * 10) # delay
            count += 1
    # We wouldn't update nodes list because it already stored in object
    # field.updateNodes(nodeList)
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
    CCH_nodeList = sorted(field.getNodes('CCH'), key=lambda x: x.getDelay(), reverse=False)
    for node in CCH_nodeList:
        if node.getType() == 'CCH':
            # Consume Energy to sending a packet
            node.consume_transmit(radius)
            for nearbyNode in field.getNearbyNodes(node, radius, 'CCH'):
                # Consume Energy to receiving a packet
                nearbyNode.consume_receive()
                if nearbyNode.getEnergy() > node.getEnergy():
                    node.setType('CM')
                    break
                else:
                    nearbyNode.setType('CM')
            if node.getType() == 'CCH':
                node.setType('CH')
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
        # Consume Energy to sending a packet
        node.consume_transmit(radius)
        for nearbyNode in field.getNearbyNodes(node, alpha_radius, 'CM'):
            nearbyNode.consume_receive()
            if not nearbyNode.hasPointerNode():
                node.setPointerNode(nearbyNode)
                nearbyNode.setPointerNode(node)
            elif nearbyNode.getPointerNode().getDistanceFromNode(nearbyNode) > node.getDistanceFromNode(nearbyNode):
                nearbyNode.getPointerNode().removePointerNode(nearbyNode)
                node.setPointerNode(nearbyNode)
                nearbyNode.setPointerNode(node)

    cluster_association_phase(field)
    
    # In case; CM can't find any CH node nearby, so we need to brute force find CH
    # Find CH node in length of diagonal of area radius
    '''
    left_CM_node = list(filter(lambda x: not x.hasPointerNode(), field.getNodes('CM')))
    print("# CM node which can't associate with CH node in phase 3 =", len(left_CM_node))
    for node in left_CM_node:
        diagonal_length = (field.getSize()**2 + field.getSize()**2)**0.5
        for CH_node in field.getNearbyNodes(node, diagonal_length, 'CH'):
            if not node.hasPointerNode():
                node.setPointerNode(CH_node)
                CH_node.setPointerNode(node)
            elif node.getPointerNode().getDistanceFromNode(node) > node.getDistanceFromNode(CH_node):
                node.getPointerNode().removePointerNode(node)
                node.setPointerNode(CH_node)
                CH_node.setPointerNode(node)
    ''' # Ignore


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

    for member in field.getNodes('CM'):
        CH_pointer = member.getPointerNode()
        if CH_pointer:
            member.consume_transmit(member.getDistanceFromNode(CH_pointer))
            CH_pointer.consume_receive()

    # Find the size and average energy for each Cluster Header
    for node in field.getNodes('CH'):
        node.updateSize()
        node.computeAverageEnergy()

    print("# Node left in field (assume that we finish):", len(field.getNodes()))
    # Plot graph to simulate environments
    for node in field.getNodes('CH'):
        for member in node.getPointerNode():
            plt.plot([node.getX(), member.getX()], [node.getY(), member.getY()], color='r', alpha=0.7, linewidth=0.8)

    cluster_confirmation_phase(field)


def cluster_confirmation_phase(field):
    """
    Phase 5
    Cluster Confirmation Phase

    All Cluster node will confirm the duty that they would be in a round
    and so it's should start process by sending data to BaseStation
    """
    nodeList, count = field.getNodes(), 0
    for node in field.getNodes('CH'):
        # Energy consumptions at CH node
        # Create packet and sending to all CM which pointer to itself
        members = node.getPointerNode()
        for member in members:
            node.consume_transmit(node.getDistanceFromNode(member))
            member.consume_receive()
            # Cluster member adjust T-value (Fuzzy Algorithm)
            adjustment_T_value(field, node)

        # Cluster Header
        size = node.getSize()
        member_list = node.getPointerNode()
        residual_energy = node.getResidualEnergy()
        avg_CM_energy = node.getAverageCM_energy()
        avg_energy = node.getAverageAll_energy()
        # Cluster Header adjust T-value (Fuzzy Algorithm)
        adjustment_T_value(field, node)

        node.consume_Eproc(len(member_list))

        if node.getEnergy() <= 0:
            field.deleteNode(node)
            del node


def adjustment_T_value(field, node):
    """
    T-Value adjustment

    """
    # This is crisp adjustment
    radius = field.getRadius()
    if node.getSize() > radius:
        node.setT(node.getT() * 1.01)
    elif node.getSize() < radius:
        node.setT(node.getT() * 0.99)

    # To-do Fuzzy here
    # ...


# This is main
if __name__ == "__main__":
    start_loop = int(input('Start loop: '))
    final_loop = int(input('Final loop: '))
    field_radius = int(input('Init Radius: '))
    start_time = _time.time()
    for tc in range(start_loop, final_loop + 1):
        print('Testcase', tc)

        if not os.path.isdir("sample_case_proc/%04d" % tc):
            os.mkdir("sample_case_proc/%04d" % tc)

        field = Field(100, 0.0125, radius=field_radius, start_energy=3, t=0.2)
        left_node = [int(field.getDensity() * int(field.getSize())**2)]

        while len(field.getNodes()) > 0:
            print('\nRound:', len(left_node) + 1)
            CCH_election_phase(field, 20)
            CH_competition_phase(field, field_radius)
            cluster_announcement_phase(field, field_radius)
            field.printField(pic_id=0, r=len(left_node), showplot=0)
            left_node.append(len(field.getNodes()))
            field.resetNode()

        print()
        del field
        '''
        # Save graph
        plt.plot(list(range(len(left_node))), left_node)
        plt.xlabel('Round')
        plt.ylabel('Node')
        plt.title("Node left per round")
        # plt.show()
        plt.savefig('sample_case_proc/%04d' % tc, dpi=300)
        plt.clf()
        # Save File
        try:
            path_o = "sample_case_proc/%04d.txt" % (tc)
            print(path_o)
            f_o = open(os.path.join(path_o), "w+")
            f_o.writelines("\n".join(list(map(str, left_node))))
            f_o.close()

            print("Save I/O Complete")
        except:
            print("Save I/O Error")

        del field
        '''
        print("------- END OF Testcase %d -------" % tc)
    print("---------- END OF EXECUTION ----------")
    print("-- Using %s seconds --" % (_time.time() - start_time))

