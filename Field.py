"""
For declare field class
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.markers as mark
import matplotlib.patches as patches
from Node import Node

class Field:
    """
    Object Field
    """
    def __init__(self, size=1, density=0, radius=30, start_energy=3, r=1, t=0.2):
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
        self._radius = radius
        self._round = r
        self._t = t
        self._start_energy = start_energy
        self.nodeList = []
        self.nodeCH = []

        self.createNode(-50, 50, 'BS')
        for i in range(1, int(self._density * self._size**2) + 1):
            self.createNode(np.random.rand() * size, np.random.rand() * size, 'CM', t=t, name="Node_%d" % i)
        # self.updateDistance() // Feature

    def getSize(self):
        """
        Get size of field
        Return
            Size of field (int)
        """
        return self._size

    def getDensity(self):
        """
        Get node density of field
        Return
            Node density of field
        """
        return self._density

    def getRadius(self):
        """
        Get node find radius in field
        Return
            Radius
        """
        return self._radius

    def createNode(self, x, y, nodetype='CM', t=0.2, name='node'):
        """
        Create new nodes
        and store it in list which have 2 element
        First element: Node
        Second element: Delay
        Args:
            x      (float): Position x of new node
            y      (float): Position y of new node
            nodetype (str): Node type
            t      (float): T chance
        """
        self.nodeList.append(Node(x, y, energy=self._start_energy + 0.01 * np.random.rand() * (1 if np.random.rand() < 0.5 else - 1), nodetype=nodetype, t=t, name=name))

    def deleteNode(self, node):
        """
        Delete node from field
        Args:
            node (Node): Node that will be removed
        """
        self.nodeList.remove(node)

    def getBaseStation(self):
        """
        Get Base station node
        Return
            Base station node
        """
        return self.nodeList[0]

    def getNodes(self, nodetype='none'):
        """
        Get all or (nodetype) nodes in field
        Args:
            nodetype (str): Node type (init='none')
        Return0
            List of nodes in field
        """
        nodeList = self.nodeList[1:]
        if nodetype != 'none':
            return list(filter(lambda x: x.getType() == nodetype, nodeList))
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
        nearbyNodes = list(filter(lambda x: node.getDistanceFromNode(x) <= radius and node != x, self.getNodes(nodetype)))
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

    def getRound(self):
        """
        Get Round
        Return
            Round
        """
        return self._round

    def nextRound(self):
        """
        Goto next round
        """
        self._round += 1

    def resetNode(self):
        """
        Reset node status
        """
        nodeList = self.getNodes()
        for node in nodeList:
            node.setType('CM')
            node.setDelay(0)
            node.setState('active')
            node.clearPointerNode()
            node.clearPackets()
        plt.clf()

    def printField(self, testcase=0, rnd=0, showplot=0, radius=0):
        """
        Plot field

        Args:
            pic_id (int): Save image id
            showplot (bool): Show plot graph
        """
        x_cm, y_cm, x_ch, y_ch, i = [], [], [], [], 0
        for node in self.getNodes():
            if node.getType() == 'CH':
                x_ch.append(node.getX())
                y_ch.append(node.getY())
            elif node.getType() != 'BS':
                x_cm.append(node.getX())
                y_cm.append(node.getY())
        plt.scatter([-50], [50], s=35, label='BS', marker=mark.MarkerStyle('o', fillstyle='full'))
        plt.scatter(x_cm, y_cm, s=18, label='CM', marker=mark.MarkerStyle('.', fillstyle='full'))
        plt.scatter(x_ch, y_ch, s=20, label='CH', marker=mark.MarkerStyle(',', fillstyle='full'))
        plt.gca().add_patch(patches.Rectangle((0, 0), self.getSize(), self.getSize(), linewidth='1', linestyle='-', facecolor='none', edgecolor='k'))
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title("Field")
        plt.legend(loc=0)
        if rnd:
            plt.savefig("sample_case_proc/R%02d/T%02d/%04d/%04d" % (self.getRadius(), (self._t * 100), testcase, rnd), dpi=72)
        if showplot:
            plt.show()
        plt.clf()
        #print("--- Save Field ---")
