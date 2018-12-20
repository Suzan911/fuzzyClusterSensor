"""
For declare Node class
"""
import numpy as np
class Node:
    """
    Object Node
    """
    def __init__(self, x=0, y=0, energy=3, nodetype='CM', name='node', delay=0, t=0.2, state='active'):
        """
        Initial variables for new node
        Args:
            x (float): Position x
            y (float): Position y
            energy (float): Energy
            nodetype (str): Node type
            name (str): Name of node   # Not used
            delay (float): Delay of node using while phase 2 if this node is CCH
            t (float): Chance to be CCH
        """
        self.__x = x
        self.__y = y
        self.__energy = energy
        self.__nodetype = nodetype
        self.__name = name
        self.__pointerNode = []
        self.__size = 0
        self.__t = t
        self.__delay = delay
        self.__state = state

        """
        Use to stored average residual energy if this node is CH
        """
        self.__packet_energy = []
        self.__energy_CM_avg = 0
        self.__energy_all_avg = 0

        """
        Use to stored distance from this node to the others node
        """
        self.__distance_node = dict()

    def getName(self):
        """
        Get name of node
        Return
            Node name
        """
        return self.__name

    def getPosition(self):
        """
        Get positions of node
        Return
            Tuple of position of node (x, y)
        """
        return self.__x, self.__y

    def getX(self):
        """
        Get position x of node
        Return
            Position x of node
        """
        return self.__x

    def getY(self):
        """
        Get position y of node
        Return
            Position y of node
        """
        return self.__y

    def getEnergy(self):
        """
        Get energy of node
        Return
            Energy of node
        """
        return self.__energy

    def getType(self):
        """
        Get type of node
        Return
            Type of node (CH, CCH, CM)
        """
        return self.__nodetype

    def getState(self):
        """
        Get state of node
        Return
            Action or Sleep
        """
        return self.__state

    def getSize(self):
        """
        Get size of node if this node is Cluster Header (CH)
        otherwise return 0
        Return
            size (float): Size of node
        """
        return self.__size

    def getDelay(self):
        """
        Get delay
        Return
            delay (float): Delay of node
        """
        return self.__delay

    def getT(self):
        """
        Get T
        Return
            t (float): T Chance
        """
        return self.__t

    def setType(self, nodetype):
        """
        Set node to new type
        """
        self.__nodetype = nodetype

    def setState(self, state):
        """
        Set state of node
        """
        self.__state = state

    def setDelay(self, delay):
        """
        Set delay of node
        Args:
            delay (float): Delay of node
        """
        self.__delay = delay

    def setT(self, t):
        """
        Set T
        Args:
            t (float): T Change
        """
        self.__t = t

    def getSize(self):
        """
        Get size of Cluster Header node (CH) or 
        return size of pointer cluster for Cluster member Node (CM)
        Return
            Cluster size
        """
        return self.__size

    def setSize(self, size):
        """
        Set size of Cluster node
        Args:
            size (float): Size
        """
        self.__size = size

    def updateSize(self):
        """
        Update size of node if this node is Cluster Header Node
        update size of pointer node if this node is Cluster Member Node
        Return
            size (float): Size of node
        """
        size = 0
        if self.getType() == 'CH' and self.hasPointerNode():
            size = max(list(map(lambda x: self.getDistanceFromNode(x), self.getPointerNode())))
            self.setSize(size)
        elif self.getType() == 'CH':
            self.setSize(0)
        elif self.getType() == 'CM':
            size = self.getPointerNode().getSize()
            self.setSize(size)
        return self.getSize()

    def getDistanceFromNode(self, node):
        """
        Get how far of distance from the other node
        Args:
            node (Node): The other node
        Return
            Difference of distance between node
        """
        '''
        if node not in self.__distance_node:
            self.__distance_node[node] = ((self.__x - node.getX())**2 + (self.__y - node.getY())**2)**0.5
        '''
        if node not in self.__distance_node:
            self.__distance_node[node] = ((self.__x - node.getX())**2 + (self.__y - node.getY())**2)**0.5
        return self.__distance_node[node]

    def getResidualEnergy(self):
        """
        Get residual energy of all CM node that connect to this node, if this node is CH
        otherwise it should return energy itself
        Return
            Residual Energy
        """
        if self.getType() == 'CH':
            return np.sum([node.getEnergy() for node in self.getPointerNode()])
        else:
            return self.getEnergy()

    def getPointerNode(self):
        """
        Get pointer to some node that should be a header of this node (if CM)
        or get a list of CM that pointer to this node (if CH)
        Return
            Header of this node or list of CM
        """
        # Need Fix
        if self.getType() == 'CH':
            pointer = self.__pointerNode
        else:
            pointer = self.__pointerNode[0]
        return pointer

    def setPointerNode(self, node):
        """
        Set pointer to some node that should be a header of this node
        Args:
            node (Node): Header of this node
        """
        if self.getType() != 'CH':
            self.__pointerNode.clear()
        self.__pointerNode.append(node)

    def hasPointerNode(self):
        """
        Check if this node has a pointer node
        Return
            True if this node has pointer, otherwise False
        """
        return len(self.__pointerNode) != 0

    def removePointerNode(self, node):
        """
        Remove pointer from some node, use to switch pointer from header node
        Args:
            node (Node): Node that want to switch
        """
        self.__pointerNode.remove(node)

    def clearPointerNode(self):
        """
        Clear pointer node
        """
        self.__pointerNode.clear()
    
    def setEnergy(self, energy):
        """
        Set energy to this node
        Args:
            energy (float): Energy of this node
        """
        self.__energy = energy

    def computeAverageEnergy(self):
        """
        Compute calcuate average residual energy
        """
        size = self.getSize()
        packets = self.getPacketEnergy()
        residual_energy = np.sum(packets)
        if len(packets):
            self.__energy_CM_avg = residual_energy / len(packets)
            self.__energy_all_avg = (residual_energy + self.getEnergy()) / (len(packets) + 1)
        else:
            self.__energy_CM_avg = 0
            self.__energy_all_avg = self.getEnergy()
    
    def getAverageCM_energy(self):
        if self.getType() == 'CH':
            return self.__energy_all_avg
        else:
            return self.getPointerNode().getAverageCM_energy()

    def getAverageAll_energy(self):
        if self.getType() == 'CH':
            return self.__energy_all_avg
        else:
            return self.getPointerNode().getAverageAll_energy()

    """
    Sections Energy consumption

    Variables define
        eagg = 5*(10**(-9))             # (nJ/bit/signal) Energy dissipation for data aggergation
        dzero = 87                      # Distance which we swap to the others equation of energy loss
        ld = 4000                       # Length of data packet
        eelec = 50*(10**(-9))           # Energy dissipation of transmitter & receiver electronics
        efs = 10**-12                   # Energy dissipation of transmitter amplifier in Friis free space
        emp = 0.0013*(10**-(12))        # Energy dissipation of data aggregation
    """
    def consume_receive(self, packet_size):
        """
        Erx is the energy used by a sensor to receive
        a data packet of >packet_size< bit size and >Eelec< is the
        constant factor of energy in transmitter and receiver
        circuitry
        """
        eelec = 50*(10**(-9)) #Energy dissipation of transmitter & receiver electronics        
        self.setEnergy(self.getEnergy() - eelec * packet_size) # eelec * ld = 50 * (10**(-9)) * 4000

    def consume_transmit(self, packet_size, d, debug=0):
        """
        Energy used by a sensor to transmit >Ld< Bit
        of data packet over a distance d.
        
        If d is less then the threshold distance, d0, we ues terms of >Efs< as
        the constant factors of energy in a free-space conmdition.
        when d is greater then or equal to d0, we use terms of >Emp<
        for a multi-path fading condition.
        Args:
            d   (float): Distance
            debug (int): Debug
        """
        eelec = 50*(10**(-9)) #Energy dissipation of transmitter & receiver electronics
        ld = packet_size #Length of data packet
        efs = 10**-12   #Energy dissipation of transmitter amplifier in Friis free space
        emp = 0.0013*(10**(-12)) #Energy disipation of data aggregation
        dzero = 87
        if d < dzero:
            energy = ld * (eelec + efs * d**2)
            if debug:
                print(' +', end=' ')
        else:
            energy= ld * (eelec + emp * d**4)
            if debug:
                print(' -', end=' ')
        self.setEnergy(self.getEnergy() - energy)

    def consume_Eproc(self, amount_nodes):
        """
        It depends on size of total numder of bit >Lt< that
        the CH received from all CMs and form itself and >Eagg< 
        which is the energy costant for data aggergation
        """
        ld = 4000 #Length of data packet
        eelec = 50*(10**(-9)) #Energy dissipation of transmitter & receiver electronics
        energy = ld * amount_nodes * eelec
        self.setEnergy(self.getEnergy() - energy)

    def getPacketEnergy(self):
        """
        Get Packet energy
        Return
            Packet energy of Cluster member that pointer to this node
        """
        return self.__packet_energy

    def append_packet_energy(self, packet):
        """
        Append packet energy for Cluster Member if this node is Cluster Header
        Args:
            packet (float): Packet of residual energy
        """
        self.__packet_energy.append(packet)

    def clearPackets(self):
        """
        Clear packet energy
        """
        self.__packet_energy.clear()
