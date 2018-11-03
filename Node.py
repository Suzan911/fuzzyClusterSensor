"""
For declare Node class
"""
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
        self.__energy_CM_avg = 0
        self.__energy_all_avg = 0

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
        return self.__size if self.getType() == 'CH' else 0

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
        return 0 for Cluster member Node (CM)
        Return
            Cluster size
        """
        return self.__size

    def updateSize(self):
        """
        Update size of node if this node is Cluster Header Node
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

    def getResidualEnergy(self):
        """
        Get residual energy of all CM node that connect to this node, if this node is CH
        otherwise it should return energy itself
        Return
            Residual Energy
        """
        if self.getType() == 'CH':
            return sum([node.getEnergy() for node in self.getPointerNode()])
        else:
            return self.getEnergy()

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

    def computeAverageEnergy(self):
        """
        Compute calcuate average residual energy
        """
        size = self.getSize()
        member_list = self.getPointerNode()
        residual_energy = self.getResidualEnergy()
        if len(member_list):
            self.__energy_CM_avg = residual_energy / len(member_list)
            self.__energy_all_avg = (residual_energy + self.getEnergy()) / (len(member_list) + 1)
    
    def getAverageCM_energy(self):
        return self.__energy_CM_avg

    def getAverageAll_energy(self):
        return self.__energy_all_avg

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
        self.setEnergy(self.getEnergy() - eelec*ld)

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
