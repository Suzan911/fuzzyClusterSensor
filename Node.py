"""
For declare Node class
"""
class Node:
    """
    Object Node
    """
    def __init__(self, x=0, y=0, energy=10, nodetype='CM', name='node'):
        """
        Initial variables for new node
        Args:
            x (float): Position x
            y (float): Position y
            energy (float): Energy
        """
        self.__x = x
        self.__y = y
        self.__energy = energy
        self.__nodetype = nodetype
        self.__name = name
        self.__pointerNode = []

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
        Get pointer to some node that should be a header of this node
        Return
            Header of this node
        """
        return self.__pointerNode

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
