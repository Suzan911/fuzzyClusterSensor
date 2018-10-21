"""
For declare field class
"""
import random as rand
import matplotlib.pyplot as plt
import matplotlib.markers as mark
from Node import Node

class Field:
    """
    Object Field
    """
    def __init__(self, size=1, density=0, start_energy=3, r=0):
        """
        Initial variable for new field
        Args:
            size (int): Size of field in meter
            density (float): Density of node per m^2
            start_energy (float): Initial energy for new nodes (J_
            r (int): Round                                      # Currently not used
        """
        self._size = size
        self._density = density
        self._round = r
        self._start_energy = start_energy
        self.nodeList = []
        self.nodeCH = []

        self.createNode(-50, 50, 'BS')
        for _ in range(int(self._density * self._size**2)):
            self.createNode(rand.random() * size, rand.random() * size)

    def getSize(self):
        """
        Get size of field
        Return
            Size of field (int)
        """
        return self._size
    
    def createNode(self, x, y, nodetype='CM'):
        """
        Create new nodes
        and store it in list which have 3 element
        First element: Node
        Second element: Delay
        Args:
            x      (float): Position x of new node
            y      (float): Position y of new node
            nodetype (str): Node type
        """
        self.nodeList.append([Node(x, y, energy=self._start_energy + 0.01 * rand.random() * (1 if rand.random() < 0.5 else - 1), nodetype=nodetype), 0])

    def getNodes(self, nodetype='none'):
        """
        Get all or (nodetype) nodes in field
        Args:
            nodetype (str): Node type (init='none')
        Return
            List of nodes in field
        """
        nodeList = self.nodeList[1:]
        if nodetype != 'none':
            return list(filter(lambda x: x[0].getType() == nodetype, nodeList))
        return nodeList

    def getNearbyNodes(self, node, radius, nodetype='none'):
        """
        Get nearby node which in radius of input node
        Args:
            node (Node): Node
            radius (float): Range radius of node
            nodetype (str): Node type (init='none')
        Return:
            List of nearby nodes
        """
        nearbyNodes = list(filter(lambda x: node.getDistanceFromNode(x[0]) <= radius and node != x[0], self.getNodes(nodetype)))
        return nearbyNodes


    def updateNodes(self, nodeList):
        """
        Update field node
        Args:
            nodeList (*Node): List of nodes
        """
        self.nodeList = nodeList

    def getInitEnergy(self):
        """
        Get initial energy
        Return
            Initial energy
        """
        return self._start_energy

    def nextRound(self):
        """
        Goto next round
        """
        self._round += 1

    def random_claster_header(self, prob):
        """
        Random select node to be a Claster header
        Args:
            prob (float): Probability to promote node to be a Claster header
        """
        self.nodeCH.clear()
        nodeList = self.getNodes()
        count = 0
        for index in range(len(nodeList)):
            rand_num = rand.random()
            if rand_num < prob / 100:
                node = nodeList[index][0]
                node.setType('CH')
                self.nodeCH.append(node)
                count += 1
        self.nodeList = nodeList
        print("# Amount of Claster Header from 1st re-clustering = ", count)

    def printField(self):
        """
        Plot field
        """
        x_cm, y_cm, x_ch, y_ch, i = [], [], [], [], 0
        for node in self.getNodes():
            #print(i, node[0].getX(), node[0].getY(), node[0].getType())
            if node[0].getType() == 'CH':
                x_ch.append(node[0].getX())
                y_ch.append(node[0].getY())
            elif node[0].getType() != 'BS':
                x_cm.append(node[0].getX())
                y_cm.append(node[0].getY())
        plt.scatter([-50], [50], label='BS', marker=mark.MarkerStyle('o', fillstyle='full'))
        plt.scatter(x_cm, y_cm, label='CM', marker=mark.MarkerStyle('.', fillstyle='full'))
        plt.scatter(x_ch, y_ch, label='CH', marker=mark.MarkerStyle(',', fillstyle='full'))
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title("Field")
        plt.legend()
        plt.show()

    def run(self):
        """
        Run process
        """
        self.random_claster_header(20)
        self.printField()