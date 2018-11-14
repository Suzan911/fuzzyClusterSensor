"""
For running algorithm
"""
import math
import os
import shutil
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
        if np.random.rand() <= node.getT():
            node.setType('CCH')
            # Exploit : In first round, every node have same amount of energy how we decide which one to be CCH
            # Solution: Define starting node that be implant at initial energy +- 0.01
            node.setDelay((field.getInitEnergy() - node.getEnergy()) / field.getInitEnergy() * 10) # delay
            count += 1
    # We wouldn't update nodes list because it already stored in object
    # field.updateNodes(nodeList)
    print("# Amount of Candidate Claster Header (CCH) in Phase 1 =", count)


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
    # print("T value for each CCH")
    # print([node.getT() for node in CCH_nodeList])

    # Iterate thought remaining CCH node every iteraton
    # So we can graruntee that so we can get only CCH which doesn't sleep during this phase  
    while len(CCH_nodeList):
        node = CCH_nodeList.pop(0)
        # Consume Energy for sended a packet
        node.consume_transmit(radius)
        for nearbyNode in field.getNearbyNodes(node, radius, 'CCH'):
            # Consume Energy for received a packet
            nearbyNode.consume_receive()
            if nearbyNode.getEnergy() > node.getEnergy():
                node.setType('CM')
                break
            else:
                nearbyNode.setType('CM')
                CCH_nodeList.remove(nearbyNode)
        if node.getType() == 'CCH':
            node.setType('CH')
            count += 1
    print("# Amount of Claster Header in Phase 2 =", count)


def cluster_announcement_phase(field, radius):
    """
    Phase 3
    Cluster Announcement Phase

    Cluster Header (CH) announce around themselves for announce Cluster Members to pointer at them

    Args:
        field  (Field): Field
        radius (float): Radius around CH nodes
    """
    alpha_radius = math.sqrt(2 * math.log(10)) * radius
    CH_nodeList = field.getNodes('CH')
    for node in CH_nodeList:
        # Consume Energy to sending a packet
        node.consume_transmit(alpha_radius)
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
    ''' # Ignore for now


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

    for node in CH_nodeList:
        members = node.getPointerNode()
        for member in members:
            member.consume_transmit(member.getDistanceFromNode(node))
            node.consume_receive()
            node.append_packet_energy(member.getEnergy())
        # Find the size and average energy for each Cluster Header
        node.updateSize()
        node.computeAverageEnergy()

    cluster_confirmation_phase(field)


def cluster_confirmation_phase(field):
    """
    Phase 5
    Cluster Confirmation Phase

    All Cluster node will confirm the duty that they would be in a round
    and so it's should start process by sending data to BaseStation
    """
    nodeList, count = field.getNodes(), 0
    numT = []
    for node in field.getNodes('CH'):
        # Energy consumptions at CH node
        # Create packet and sending to all CM which pointer to itself
        members = node.getPointerNode()
        node.consume_transmit(node.getSize())
        for member in members:
            member.consume_receive()
            member.updateSize()
            # Cluster member adjust T-value (Fuzzy Algorithm)
            new_t = adjustment_T_value(field, member)

        # Cluster Header
        size = node.getSize()
        member_list = node.getPointerNode()
        residual_energy = node.getResidualEnergy()
        avg_CM_energy = node.getAverageCM_energy()
        avg_energy = node.getAverageAll_energy()
        # Cluster Header adjust T-value (Fuzzy Algorithm)
        numT.append(adjustment_T_value(field, node))

        if node.getEnergy() <= 0:
            field.deleteNode(node)
            del node
    if len(field.getNodes()) == 1:
        for node in field.getNodes('CH'):
            del node
    
    print("# Node left in field (assume that we finish):", len(field.getNodes()))
    # Plot graph to simulate environments
    for node in field.getNodes('CH'):
        for member in node.getPointerNode():
            plt.plot([node.getX(), member.getX()], [node.getY(), member.getY()], color='r', alpha=0.7, linewidth=0.8)


def standyPhase(field):
    """
    Standy Phase
    """
    for node in field.getNodes('CH'):
        for member in node.getPointerNode():
            member.consume_transmit(member.getDistanceFromNode(node))
            node.consume_receive()
        node.consume_Eproc(len(node.getPointerNode()) + 1)
        node.consume_transmit(node.getDistanceFromNode(field.getBaseStation()))


def Fuzzy(node_energy, avg_energy, cluster_size, init_radius):
    """
    Fuzzy algorithms
    """
    energy = node_energy / avg_energy
    High = max(0, min(1,(1-(1.1 - energy)/0.1))) if energy >= 1 else 0
    MidHigh = max(0, min(1,(1.1 - energy)/0.1)) if energy >= 1 else 0
    MidLow = max(0, min(1,(energy - 0.9)/0.1)) if energy <= 1 else 0
    Low = max(0, min(1,((1-(energy - 0.9)/0.1)))) if energy <= 1 else 0
    #print(energy, High, MidHigh, MidLow, Low)

    #print((1-((Cluster_size - 0.9))/0.1) ,(Cluster_size - 0.9)/0.1, Cluster_size, deployed_Cluster)
    size = cluster_size / init_radius
    Large = max(0, min(1, (1-(1.1 - size)/0.1))) if size >= 1 else 0
    MidLarge = max(0, min(1, (1.1 - size)/0.1)) if size >= 1 else 0
    MidSmall = max(0, min(1, (size - 0.9)/0.1)) if size <= 1 else 0
    Small = max(0, min(1, (1-((size - 0.9))/0.1))) if size <= 1 else 0
    #print(size, Large, MidLarge, MidSmall, Small)

    rules = [min(High, Large), min(High, MidLarge), min(MidHigh, Large), min(MidHigh, MidLarge), 
             min(MidLow, Large), min(MidLow, MidLarge), min(Low, Large), min(Low, MidLarge),
             min(High, MidSmall), min(MidHigh, MidSmall), min(MidLow, MidSmall), min(Low, MidSmall),
             min(High, Small), min(MidHigh, Small), min(MidLow, Small), min(Low, Small)]
    #print(rules)
    
    start_mid_t, T_value, count = 0.03125, 0, -1
    for i in rules:
        weight = i * start_mid_t
        T_value += weight
        count = count + start_mid_t if weight and count >= 0 else start_mid_t if weight else count
        start_mid_t += 0.0625
    # print(rules, T_value / count, count)
    #print(T_value / count)
    #print()
    return T_value / count
    #return T_value / count


def adjustment_T_value(field, node):
    """
    T-Value adjustment
    """
    # Fuzzy algorithms
    radius = field.getRadius()
    value_G = Fuzzy(node.getEnergy(), node.getAverageAll_energy(), node.getSize(), radius)
    a = (node.getT())
    if value_G <= 0.5:
        new_T = node.getT() + 0.01*(0.5 - value_G)/0.5
        node.setT(new_T)
    else:
        new_T = node.getT() - 0.01*(value_G - 0.5)/0.5
        node.setT(new_T)
    
    if node.getT() > 1:
        node.setT(1)
    elif node.getT() <= 0.01:
        node.setT(0.01)
    
    #print(a, new_T, a - new_T ,value_G)
    #print()
    #print(Fuzzy(node.getEnergy(), node.getAverageAll_energy(), node.getSize(), radius)*0.01)

# This is main
if __name__ == "__main__":
    start_loop = int(input('Start loop: '))
    final_loop = int(input('Final loop: '))
    standy_loop = int(input('Standy loop: '))
    field_radius = int(input('Init Radius: '))
    start_time = _time.time()
    for tc in range(start_loop, final_loop + 1):
        print('Testcase', tc)

        if not os.path.isdir("sample_case_proc/%04d" % tc):
            os.mkdir("sample_case_proc/%04d" % tc)
        else:
            shutil.rmtree("sample_case_proc/%04d" % tc)
            os.mkdir("sample_case_proc/%04d" % tc)

        field = Field(100, 0.0125, radius=field_radius, start_energy=3, t=0.2)
        left_node = [int(field.getDensity() * int(field.getSize())**2)]
        CCH_nodeCount = [0]
        t_avg_per_round = []
        e_avg_per_round = []
        r_avg_per_round = []
        while len(field.getNodes()) > 0: #(field.getDensity() * field.getSize()**2):
            print('\nRound:', len(left_node))
            CCH_election_phase(field, 20)
            CCH_nodeCount.append(len(field.getNodes('CCH')))
            CH_competition_phase(field, field_radius)
            cluster_announcement_phase(field, field_radius)
            field.printField(pic_id=tc, r=len(left_node), showplot=0)
            
            # Data storage
            nodes = field.getNodes()
            CH_nodes = field.getNodes('CH')
            left_node.append(len(field.getNodes()))
            e_avg_per_round.append(sum([n.getAverageAll_energy() for n in CH_nodes]) / len(CH_nodes) if len(CH_nodes) else 0)
            r_avg_per_round.append(sum([n.getSize() for n in CH_nodes]) / len(CH_nodes) if len(CH_nodes) else 0)
            t_avg_per_round.append(sum([n.getT() for n in nodes]) / len(nodes) if len(nodes) else 0)
            for _ in range(standy_loop):
                standyPhase(field)
            field.resetNode()
        #print("-- First node died at round", len(left_node))
        print("-- End of simulation")
        
        # Save graph
        plt.plot(list(range(len(left_node))), left_node)
        plt.xlabel('Round')
        plt.ylabel('Node')
        plt.title("Node left per round")
        # plt.show()
        plt.savefig('sample_case_proc/%04d/%04dx_LEFT' % (tc, tc), dpi=300)
        plt.clf()

        plt.plot(list(range(len(CCH_nodeCount))), CCH_nodeCount)
        plt.xlabel('Round')
        plt.ylabel('Amount of CCH Node')
        plt.title("CCH node per round")
        # plt.show()
        plt.savefig('sample_case_proc/%04d/%04dx_CCH' % (tc, tc), dpi=300)
        plt.clf()

        plt.plot(list(range(len(t_avg_per_round))), t_avg_per_round)
        plt.xlabel('Round')
        plt.ylabel('T')
        plt.title("T Average per round")
        # plt.show()
        plt.savefig('sample_case_proc/%04d/%04dx_T_AVG' % (tc, tc), dpi=300)
        plt.clf()

        plt.plot(list(range(len(e_avg_per_round))), e_avg_per_round)
        plt.xlabel('Round')
        plt.ylabel('Energy')
        plt.title("Energy Average per round")
        # plt.show()
        plt.savefig('sample_case_proc/%04d/%04dx_E_AVG' % (tc, tc), dpi=300)
        plt.clf()

        plt.plot(list(range(len(r_avg_per_round))), r_avg_per_round)
        plt.xlabel('Round')
        plt.ylabel('Size Cluster')
        plt.title("Size Cluster Average per round")
        # plt.show()
        plt.savefig('sample_case_proc/%04d/%04dx_R_AVG' % (tc, tc), dpi=300)
        plt.clf()
        
        # Save File
        try:
            path_o = "sample_case_proc/%04d/%04dx_T_AVG.txt" % (tc, tc)
            print(path_o)
            f_o = open(os.path.join(path_o), "w+")
            f_o.writelines("\n".join(list(map(str, t_avg_per_round))))
            f_o.close()

            print("Save I/O Complete")
        except:
            print("Save I/O Error")
        
        del field
        
        print("------- END OF Testcase %d -------" % tc)
    print("---------- END OF EXECUTION ----------")
    print("-- Using %s seconds --" % (_time.time() - start_time))

