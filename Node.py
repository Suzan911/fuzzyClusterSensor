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
		self._x = x
		self._y = y
		self._energy = energy
		self._nodetype = nodetype
		self._name = name

	def getX(self):
		"""
		Get position x of node
		Return
		    Position x of node
		"""
		return self._x

	def getY(self):
		"""
		Get position y of node
		Return
		    Position y of node
		"""
		return self._y

	def getEnergy(self):
		"""
		Get energy of node
		Return
		    Energy of node
		"""
		return self._energy

	def getType(self):
		"""
		Get type of node
		Return
		    Type of node (CH, CCH, CM)
		"""
		return self._nodetype

	def setType(self, nodetype):
		"""
		Set node to new type
		"""
		self._nodetype = nodetype

	def getDistanceFromNode(self, _node):
		"""
		Get how far of distance from the other node
		Return
		    Difference of distance between node
		"""
		return ((self._x - _node.getX())**2 + (self._y - _node.getY())**2)**0.5

	def __lt__(self, _node):
		"""
		Check this node have energy less than the other node
		Args:
			_node (Node): The other node
		Return
			True if this node have energy less than the other node, otherwise False
		"""
		return self._energy < _node.getEnergy()

	def __le__(self, _node):
		"""
		Check this node have energy less than or equal the other node
		Args:
			_node (Node): The other node
		Return
			True if this node have energy less than or equal the other node, otherwise False
		"""
		return self._energy <= _node.getEnergy()

	def __eq__(self, _node):
		"""
		Check this node have energy equal the other node
		Args:
			_node (Node): The other node
		Return
			True if this node have energy equal the other node, otherwise False
		"""
		return self._energy == _node.getEnergy()

	def __ne__(self, _node):
		"""
		Check this node have energy not equal the other node
		Args:
			_node (Node): The other node
		Return
			True if this node have energy not equal the other node, otherwise False
		"""
		return self._energy != _node.getEnergy()

	def __gt__(self, _node):
		"""
		Check this node have energy greater than the other node
		Args:
			_node (Node): The other node
		Return
			True if this node have energy greater than the other node, otherwise False
		"""
		return self._energy > _node.getEnergy()

	def __ge__(self, _node):
		"""
		Check this node have energy greater than or equal the other node
		Args:
			_node (Node): The other node
		Return
			True if this node have energy greater than or equal the other node, otherwise False
		"""
		return self._energy >= _node.getEnergy()