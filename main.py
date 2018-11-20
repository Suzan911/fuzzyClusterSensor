"""
For running algorithm
"""
import math
import os
import shutil
import xlwt
import time as time
import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt
import matplotlib.markers as mark
#from xlutils.copy import copy as xl_copy
from itertools import product
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
    nodeList = field.getNodes()
    initEnergy = field.getInitEnergy()
    #count = 0
    for node in nodeList:
        if np.random.rand() <= node.getT():
            node.setType('CCH')
            # Exploit : In first round, every node have same amount of energy how we decide which one to be CCH
            # Solution: Define starting node that be implant at initial energy +- 0.01
            node.setDelay((initEnergy - node.getEnergy()) / initEnergy * 10) # delay
            #count += 1
    # We wouldn't update nodes list because it already stored in object
    # field.updateNodes(nodeList)
    #print("# Amount of Candidate Claster Header (CCH) in Phase 1 =", count)


def CH_competition_phase(field, radius):
    """
    Phase 2
    CH Competition Phase
    
    Compate Candidate Claster Header (CCH) which node much more energy than, then sleep the other nodes around

    Args:
        field  (Field): Field
        radius (float): Radius around CCH nodes
    """
    CCH_nodeList = sorted(field.getNodes('CCH'), key=lambda x: x.getDelay(), reverse=False)
    #count = 0
    # print("T value for each CCH")

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
            #count += 1
    #print("# Amount of Claster Header in Phase 2 =", count)


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
        # Consume Energy for sending a packet
        node.consume_transmit(alpha_radius)
        for nearbyNode in field.getNearbyNodes(node, alpha_radius, 'CM'):
            # Consume Energy for receive a packet
            nearbyNode.consume_receive()
            if not nearbyNode.hasPointerNode():
                node.setPointerNode(nearbyNode)
                nearbyNode.setPointerNode(node)
            elif nearbyNode.getPointerNode().getDistanceFromNode(nearbyNode) > node.getDistanceFromNode(nearbyNode):
                nearbyNode.getPointerNode().removePointerNode(nearbyNode)
                node.setPointerNode(nearbyNode)
                nearbyNode.setPointerNode(node)
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
    cluster_association_phase(field)


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
        for member in node.getPointerNode():
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
        '''
        size = node.getSize()
        member_list = node.getPointerNode()
        residual_energy = node.getResidualEnergy()
        avg_CM_energy = node.getAverageCM_energy()
        avg_energy = node.getAverageAll_energy()
        '''
        # Cluster Header adjust T-value (Fuzzy Algorithm)
        numT.append(adjustment_T_value(field, node))

        if node.getEnergy() <= 0:
            field.deleteNode(node)
            del node
    if len(field.getNodes()) == 1:
        for node in field.getNodes('CH'):
            del node
    
    '''
    Plot graph
    
    #print("# Node left in field (assume that we finish):", len(field.getNodes()))
    # Plot graph to simulate environments
    for node in field.getNodes('CH'):
        for member in node.getPointerNode():
            plt.plot([node.getX(), member.getX()], [node.getY(), member.getY()], color='r', alpha=0.7, linewidth=0.8)
    '''

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
        count = count + i if weight and count >= 0 else i if weight else count
        start_mid_t += 0.0625
    return T_value / count


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
        node.setT(max(0.01, min(1, new_T)))
    else:
        new_T = node.getT() - 0.01*(value_G - 0.5)/0.5
        node.setT(max(0.01, min(1, new_T)))

    #print(a, new_T, a - new_T ,value_G)
    #print()
    #print(Fuzzy(node.getEnergy(), node.getAverageAll_energy(), node.getSize(), radius)*0.01)

# This is main
def running(tc, t_init, size):
    #----------------------
    # Initial value
    # Change these value if you want new property
    #----------------------
    t_init = t_init / 100
    density = 0.0125
    # size = 10
    #----------------------

    standy_loop = 1#int(input('Standy loop: '))
    field_radius = size#int(input('Init Radius: '))
    t_init_for_file = int(t_init * 100)

    # Check if file already generate
    if not os.path.exists("sample_case_proc/R%02d/T%02d/%04d" % (size, t_init_for_file, tc)):
        os.makedirs("sample_case_proc/R%02d/T%02d/%04d" % (size, t_init_for_file, tc))
    else:
        if os.path.exists("sample_case_proc/R%02d/T%02d/%04d/data.xls" % (size, t_init_for_file, tc)):
            return
        else:
            shutil.rmtree("sample_case_proc/R%02d/T%02d/%04d" % (size, t_init_for_file, tc))
            os.makedirs("sample_case_proc/R%02d/T%02d/%04d" % (size, t_init_for_file, tc))
        
    start_time = time.time()
    book = xlwt.Workbook(encoding="utf-8")
    print("Processing in testcase {} which set initial radius at {}, density at {} and T value at {}.\nRunning on processer {}\n".format(tc, field_radius, density, t_init, mp.current_process()))

    sheet1 = book.add_sheet("%04d" % tc)
    sheet1.write(0, 0, "Round")
    sheet1.write(0, 1, "AverageAll_energy") 
    sheet1.write(0, 2, "Size")
    sheet1.write(0, 3, "T")
    sheet1.write(0, 4, "No Pointer node")

    field = Field(100, density, radius=field_radius, start_energy=3, t=t_init)
    left_node = [int(field.getDensity() * int(field.getSize())**2)]
    t_avg_per_round = []
    e_avg_per_round = []
    r_avg_per_round = []
    ignore_node = []
    while len(field.getNodes()) >= (field.getDensity() * field.getSize()**2):
        CCH_election_phase(field, t_init)
        CH_competition_phase(field, field_radius)
        cluster_announcement_phase(field, field_radius)
        ignore_node = len(list(filter(lambda x: not x.hasPointerNode(), field.getNodes('CM'))))
        #field.printField(testcase=tc, showplot=0, rnd=rnd)
        
        # Data storage
        rnd = field.getRound()
        nodes = field.getNodes()
        CH_nodes = field.getNodes('CH')
        left_node.append(len(field.getNodes()))
        E_avg = (np.sum([n.getAverageAll_energy() for n in CH_nodes]) / len(CH_nodes)) if len(CH_nodes) else 0
        Size_avg = (np.sum([n.getSize() for n in CH_nodes]) / len(CH_nodes)) if len(CH_nodes) else 0
        T_avg = (np.sum([n.getT() for n in nodes]) / len(nodes)) if len(nodes) else 0

        e_avg_per_round.append(E_avg)
        r_avg_per_round.append(Size_avg)
        t_avg_per_round.append(T_avg)
        sheet1.write(rnd, 0, (len(left_node)-1))
        sheet1.write(rnd, 1, E_avg)
        sheet1.write(rnd, 2, Size_avg)
        sheet1.write(rnd, 3, T_avg)
        sheet1.write(rnd, 4, ignore_node)
        for _ in range(standy_loop):
            standyPhase(field)
        field.nextRound()
        field.resetNode()
    
    # Save graph
    '''
    plt.plot(list(range(len(left_node))), left_node)
    plt.xlabel('Round')
    plt.ylabel('Node')
    plt.title("Node left per round")
    # plt.show()
    plt.savefig("sample_case_proc/T%04d/%04d" % (t_init, testcase), dpi=300)
    plt.clf()

    plt.plot(list(range(len(CCH_nodeCount))), CCH_nodeCount)
    plt.xlabel('Round')
    plt.ylabel('Amount of CCH Node')
    plt.title("CCH node per round")
    # plt.show()
    plt.savefig("sample_case_proc/T%04d/%04d" % (t_init, testcase), dpi=300)
    plt.clf()
    '''

    plt.plot(list(range(len(t_avg_per_round))), t_avg_per_round)
    plt.xlabel('Round')
    plt.ylabel('T')
    plt.title("T Average per round")
    # plt.show()
    plt.savefig("sample_case_proc/R%02d/T%02d/%04d/t_avg" % (size, t_init_for_file, tc), dpi=300)
    plt.clf()

    plt.plot(list(range(len(e_avg_per_round))), e_avg_per_round)
    plt.xlabel('Round')
    plt.ylabel('Energy')
    plt.title("Energy Average per round")
    # plt.show()
    plt.savefig("sample_case_proc/R%02d/T%02d/%04d/energy_avg" % (size, t_init_for_file, tc), dpi=300)
    plt.clf()

    plt.plot(list(range(len(r_avg_per_round))), r_avg_per_round)
    plt.xlabel('Round')
    plt.ylabel('Size Cluster')
    plt.title("Size Cluster Average per round")
    # plt.show()
    plt.savefig("sample_case_proc/R%02d/T%02d/%04d/size_avg" % (size, t_init_for_file, tc), dpi=300)
    plt.clf()

    plt.plot(list(range(len(r_avg_per_round))), r_avg_per_round)
    plt.xlabel('Round')
    plt.ylabel('Size Cluster')
    plt.title("Size Cluster Average per round")
    # plt.show()
    plt.savefig("sample_case_proc/R%02d/T%02d/%04d/size_avg" % (size, t_init_for_file, tc), dpi=300)
    plt.clf()
    
    del field

    time_used = time.time() - start_time
    sheet1.write(0, 5, "Time used: %f" % time_used)
    book.save("sample_case_proc/R%02d/T%02d/%04d/data.xls" % (size, t_init_for_file, tc))
    print("Processing at testcase {} which set initial radius at {}, density at {} and T value at {}\nfinished within time {}s.\nRunning on processer {}\n".format(tc, field_radius, density, t_init, time_used, mp.current_process()))

def main():
    if __name__ == "__main__":
        pool = mp.Pool(4)
        # Running thought T value for each 100 testcase
        pool.starmap(running, product(range(1, 101), range(10, 81, 5), range(10, 41, 5))) # product(testcase, t-initial, size)

main()
