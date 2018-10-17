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
	def __init__(self, size=1, nodes=0, density=0):
		"""
		Initial variable for new field

		Args:
		    size (int): Size of field in meter
		    nodes (int): Amount of iniital nodes in field
		"""
		self._size = size
		self._density = density
		self.nodeList = []
		self.nodeCH = []
		for _ in range(nodes):
			self.createNode(rand.random() * size, rand.random() * size)
	
	def createNode(self, x, y):
		"""
		Create new nodes

		Args:
		    x (float): Position x of new node
		    y (float): Position y of new node
		"""
		self.nodeList.append([Node(x, y), 'CM'])

	def getNodes(self, nodetype='none'):
		"""
		Get all or (nodetype) nodes in field

		Return
		    List of nodes in field
		"""
		nodeList = self.nodeList
		if nodetype != 'none':
			nodeList = filter(lambda x: x[1] == nodetype, nodeList)
		return nodeList

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
				nodeList[index][1] = 'CH'
				node = nodeList[index][0]
				node.setType('CH')
				self.nodeCH.append(node)
				count += 1
		self.nodeList = nodeList
		print("# Claster Header = ", count)

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
			else:
				x_cm.append(node[0].getX())
				y_cm.append(node[0].getY())
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
