"""
For declare Node class
"""
class Node:
    """
    Object Node
    """
    def __init__(self, x=0, y=0, energy=3, nodetype='CM', name='node'):
        """
        Initial variables for new node
        Args:
            x (float): Position x
            y (float): Position y
            energy (float): Energy
            nodetype (str): Node type
            name (str): Name of node   # Not used
        """
        self.__x = x
        self.__y = y
        self.__energy = energy
        self.__nodetype = nodetype
        self.__name = name
        self.__pointerNode = []
        self.__size = 0

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

    def setType(self, nodetype):
        """
        Set node to new type
        """
        self.__nodetype = nodetype

    def getSize(self):
        """
        Get size of node if this node is Cluster Header (CH)
        otherwise return 0
        Return
            size (float): Size of node
        """
        return self.__size if self.getType() == 'CH' else 0

    def updateSize(self):
        """
        Update size of node if this node is Cluster Node
        otherwise return 0
        Return
            size (float): Size of node
        """
        size = 0
        if self.getType() == 'CH' and self.hasPointerNode():
            size = max(list(map(lambda x: self.getDistanceFromNode(x), self.getPointerNode())))
            self.__size = size
        return size

    def getDistanceFromNode(self, node):
        """
        Get how far of distance from the other node
        Args:
            node (Node): The other node
        Return
            Difference of distance between node
        """
        return ((self.__x - node.getX())**2 + (self.__y - node.getY())**2)**0.5

    def getPointerNode(self):
        """
        Get pointer to some node that should be a header of this node (if CM)
        or get a list of CM that pointer to this node (if CH)
        Return
            Header of this node or list of CM
        """
        if self.getType() != 'CH':
            if len(self.__pointerNode) > 0:
                pointer = self.__pointerNode[0]
            else:
                pointer = self.__pointerNode
        else:
            pointer = self.__pointerNode
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

    def consume_receive(self):
        """
        Erx is the energy used by a sensor to receive
        a data packet of >Ld< bit size and >Eelec< is the
        constant factor of energy in transmitter and receiver
        circuitry
        """
        eelec = 50*(10**(-9)) #Energy dissipation of transmitter & receiver electronics
        ld = 4000
        return eelec*ld

    def consume_transmit(self, d):
        """
        Energy used by a sensor to transmit >Ld< Bit
        of data packet over a distance d. if d is less then
        the threshold distance, d0, we ues terms of >Efs< as
        the constant factors of energy in a free-space conmdition.
        when d is greter thne or equal to d0, we use terms of >Emp<
        for a multi-path fading condition.
        Args:
            d (float): Distance
        """
        eelec = 50*(10**(-9)) #Energy dissipation of transmitter & receiver electronics
        ld = 4000 #Length of data packet
        efs = 10**-12   #Energy dissipation of transmitter amplifier in Friis free space
        emp = 0.0013*(10**-(12)) #Energy dissipation of data aggregation
        dzero = 87
        if d < dzero:
            energy = ld * (eelec + efs * d**2)
        else:
            energy= ld * (eelec + emp * d**4)
        return energy

    def consume_Eproc(self, amount_nodes):
        """
        It depends on size of total numder of bit >Lt< that
        the CH received from all CMs and form itself and >Eagg< 
        which is the energy costant for data aggergation
        """
        ld = 4000 #Length of data packet
        eelec = 50*(10**(-9)) #Energy dissipation of transmitter & receiver electronics
        energy = ld * amount_nodes * eelec
        return energy

    def __lt__(self, _node):
        """
        Check this node have energy less than the other node
        Args:
            _node (Node): The other node
        Return
            True if this node have energy less than the other node, otherwise False
        """
        return self.__energy < _node.getEnergy()

    def __le__(self, _node):
        """
        Check this node have energy less than or equal the other node
        Args:
            _node (Node): The other node
        Return
            True if this node have energy less than or equal the other node, otherwise False
        """
        return self.__energy <= _node.getEnergy()

    def __eq__(self, _node):
        """
        Check this node have energy equal the other node
        Args:
            _node (Node): The other node
        Return
            True if this node have energy equal the other node, otherwise False
        """
        return self.__energy == _node.getEnergy()

    def __ne__(self, _node):
        """
        Check this node have energy not equal the other node
        Args:
            _node (Node): The other node
        Return
            True if this node have energy not equal the other node, otherwise False
        """
        return self.__energy != _node.getEnergy()

    def __gt__(self, _node):
        """
        Check this node have energy greater than the other node
        Args:
            _node (Node): The other node
        Return
            True if this node have energy greater than the other node, otherwise False
        """
        return self.__energy > _node.getEnergy()

    def __ge__(self, _node):
        """
        Check this node have energy greater than or equal the other node
        Args:
            _node (Node): The other node
        Return
            True if this node have energy greater than or equal the other node, otherwise False
        """
        return self.__energy >= _node.getEnergy()
