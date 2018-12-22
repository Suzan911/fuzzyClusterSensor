"""
Algorithm for each phase
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
    candidate_count = 0
    for node in nodeList:
        if np.random.rand() <= node.getT():
            node.setType('CCH')
            node.setDelay((initEnergy - node.getEnergy()) / initEnergy * 10) # delay
            candidate_count += 1
        else:
            node.setType('CM')
            node.setState('sleep')
    # We wouldn't update nodes list because it already stored in object
    # field.updateNodes(nodeList)
    return candidate_count


def CH_competition_phase(field, radius, debug=0):
    """
    Phase 2
    CH Competition Phase
    
    Compate Candidate Claster Header (CCH) which node much more energy than,
    then sleep the other nodes around

    Args:
        field  (Field): Field
        radius (float): Radius around CCH nodes
        debug   (bool): Toggle debug mode
    """
    CCH_nodeList = sorted(field.getNodes('CCH'), key=lambda x: x.getDelay(), reverse=False)
    if debug:
        nodetype = {node: node.getType() for node in field.getNodes()}
        received_list = {node: 0 for node in field.getNodes()}
    # Iterate thought remaining CCH node every iteraton
    # So we can graruntee that so we can get only CCH which doesn't sleep during this phase
    while len(CCH_nodeList):
        node = CCH_nodeList.pop(0)
        if node.getState() != 'sleep':
            node.setType('CH')
            # Consume Energy for sended a packet
            node.consume_transmit(200, radius)
            if debug:
                received_list[node] += 1
            for nearbyNode in field.getNearbyNodes(node, radius, 'CCH', debug=0):
                # Consume Energy for received a packet
                nearbyNode.consume_receive(200)
                nearbyNode.setType('CM')
                nearbyNode.setState('sleep')
                if debug:
                    received_list[nearbyNode] += 1
                CCH_nodeList.remove(nearbyNode)
    if debug:
        return nodetype, received_list


def cluster_announcement_phase(field, radius, debug=0):
    """
    Phase 3
    Cluster Announcement Phase

    Cluster Header (CH) announce around themselves for announce Cluster Members to pointer at them

    Args:
        field  (Field): Field
        radius (float): Radius around CH nodes
        debug   (bool): Toggle debug mode
    """
    alpha_radius = math.sqrt(2 * math.log(10)) * radius
    CH_nodeList = field.getNodes('CH')
    if debug:
        received_list = {node: 0 for node in field.getNodes()}
    for node in CH_nodeList:
        # Consume Energy for sending a packet to CM with in radius]
        start_e = node.getEnergy()
        node.consume_transmit(200, alpha_radius)
        if debug:
            received_list[node] += 1
        for nearbyNode in field.getNearbyNodes(node, alpha_radius, 'CM', debug=0):
            # Consume Energy for receive a packet from CH
            nearbyNode.consume_receive(200)
            if not nearbyNode.hasPointerNode():
                node.setPointerNode(nearbyNode)
                nearbyNode.setPointerNode(node)
            elif node.getDistanceFromNode(nearbyNode) < nearbyNode.getPointerNode().getDistanceFromNode(nearbyNode):
                nearbyNode.getPointerNode().removePointerNode(nearbyNode)
                node.setPointerNode(nearbyNode)
                nearbyNode.setPointerNode(node)
            if debug:
                received_list[nearbyNode] += 1

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
    ''' # Ignored
    if debug:
        return received_list


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
            member.consume_transmit(200, member.getDistanceFromNode(node))
            node.consume_receive(200)
            node.append_packet_energy(member.getEnergy())
        # Find the size and average energy for each Cluster Header
        node.updateSize()
        node.computeAverageEnergy()


def cluster_confirmation_phase(field, is_fuzzy=False, plot_graph=False):
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
        node.consume_transmit(200, node.getSize())
        for member in node.getPointerNode():
            member.consume_receive(200)
            member.updateSize()
            # Cluster member adjust T-value (Fuzzy Algorithm)
            if is_fuzzy:
                adjustment_T_value(field, member)
        # Cluster Header adjust T-value (Fuzzy Algorithm)
        if is_fuzzy:
            adjustment_T_value(field, node)

        if node.getEnergy() <= 0:
            field.deleteNode(node)
            del node
    if len(field.getNodes()) == 1:
        for node in field.getNodes('CH'):
            del node
    '''
    Plot graph
    Plot graph to simulate environments
    '''
    if plot_graph:
        for node in field.getNodes('CH'):
            for member in node.getPointerNode():
                plt.plot([node.getX(), member.getX()], [node.getY(), member.getY()], color='r', alpha=0.7, linewidth=0.8)

def standyPhase(field):
    """
    Standy Phase
    
    All Cluster Header aggregate data from Cluster Member
    and send it to a BaseStation
    """
    for node in field.getNodes('CH'):
        for member in node.getPointerNode():
            member.consume_transmit(4000, member.getDistanceFromNode(node))
            node.consume_receive(4000)
        node.consume_Eproc(len(node.getPointerNode()) + 1)
        node.consume_transmit(4000, node.getDistanceFromNode(field.getBaseStation()))


def Fuzzy(node_energy, avg_energy, cluster_size, init_radius):
    """
    Fuzzy algorithms
    """
    energy = node_energy / avg_energy
    High = max(0, min(1,(1-(1.1 - energy)/0.1))) if energy >= 1 else 0
    MidHigh = max(0, min(1,(1.1 - energy)/0.1)) if energy >= 1 else 0
    MidLow = max(0, min(1,(energy - 0.9)/0.1)) if energy <= 1 else 0
    Low = max(0, min(1,((1-(energy - 0.9)/0.1)))) if energy <= 1 else 0

    size = cluster_size / init_radius
    Large = max(0, min(1, (1-(1.1 - size)/0.1))) if size >= 1 else 0
    MidLarge = max(0, min(1, (1.1 - size)/0.1)) if size >= 1 else 0
    MidSmall = max(0, min(1, (size - 0.9)/0.1)) if size <= 1 else 0
    Small = max(0, min(1, (1-((size - 0.9))/0.1))) if size <= 1 else 0

    rules = [min(High, Large), min(High, MidLarge), min(MidHigh, Large), min(MidHigh, MidLarge), 
             min(MidLow, Large), min(MidLow, MidLarge), min(Low, Large), min(Low, MidLarge),
             min(High, MidSmall), min(MidHigh, MidSmall), min(MidLow, MidSmall), min(Low, MidSmall),
             min(High, Small), min(MidHigh, Small), min(MidLow, Small), min(Low, Small)]
    
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
    if value_G <= 0.5:
        new_T = node.getT() + 0.01*(0.5 - value_G)/0.5
        node.setT(max(0.01, min(1, new_T)))
    else:
        new_T = node.getT() - 0.01*(value_G - 0.5)/0.5
        node.setT(max(0.01, min(1, new_T)))
    return new_T
