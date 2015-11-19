import sys
import re
import pprint
import math
import xml.etree.ElementTree as ET

class Edge:
	def __init__(self, label, num, toNode):
		self.label = label
		self.num = num
		self.toNode = toNode

	def getToNode(self):
		return self.toNode

	def getNum(self):
		return self.num

	def getLabel(self):
		return self.label

class Node:
	def __init__(self, label):
		self.edges = []
		self.label = label

	def addEdge(self, label, num, child):
		self.edges.append(Edge(label, num, child))

	def getLabel(self):
		return self.label

	def getEdges(self):
		return self.edges

	def hasEdges(self):
		return True if len(self.edges) > 0 else False
	
"""
class Node:
	def __init__(self, label):
		self.edges = {}
		self.label = label

	def addEdge(self, label, child):
		self.edges[label] = child

	def getLabel(self):
		return self.label

	def getEdges(self):
		return self.edges
"""

class TrainingSet:
	def __init__(self):
		self.domain = {}
		self.sizes = None
		self.category = None
		self.attributes = None
		self.records = []
		self.tree = []

	def addAttributes(self, attributes):
		""" Add a record """
		self.attributes = attributes

	def addCategory(self, category):
		""" Add a category """
		self.category = category

	def addSizes(self, sizes):
		""" Add numbers """
		self.sizes = sizes

	def printRecords(self):
		pprint.pprint(self.records)

	def printDomain(self):
		pprint.pprint(self.domain)

	def addData(self, data):
		""" Add training data to set """
		record = {}

		i = 0
		for value in data:
			domain = self.domain.get(self.attributes[i])

			if not value.isdigit():
				idx = domain.get('groups').index(value)
				record[self.attributes[i]] = {'name': domain.get('groups')[idx]}
			else:
				record[self.attributes[i]] = {'name': domain.get('groups')[value - 1]}

			i += 1

		self.records.append(record)

	def getTrainingSet(self, fp):
	 	""" get the training set data """
		data = fp.read().splitlines()

		i = 1
		for line in data:
			line = re.split(r',', line);
			if i == 1:
				self.addAttributes(line[1:])
			elif i == 2:
				self.addSizes(line[1:])
			elif i == 3:
				self.addCategory(line[0])
			else:
				self.addData(line[1:])
			i += 1

	def getDomain(self, domain):
		""" parse the domain into an easily accessible data struct """
		root = ET.parse(domain).getroot()

		for variable in root.findall('variable'):
			domain = {}
			domain['groups'] = []
			domain['ps'] = []

			i = 1
			for group in variable.findall('group'):
				domain['groups'].append(group.get('name'))
				domain['ps'].append(group.get('p'))
				i += 1
			self.domain[variable.get('name')] = domain

		category = root.find('Category')
		cat = {}
		cat['groups'] = []
		cat['ps'] = []

		i = 1
		for choice in category.findall('choice'):
			cat['groups'].append(choice.get('name'))
			cat['ps'].append(choice.get('type'))
			i += 1
		self.domain[category.get('name')] = cat

	def getSubset(self, data, attr, value):
		""" get a subset of records with a certain attribute and value """

		subset = []

		for record in data:
			attribute = record.get(attr)
			if attribute.get('name') == value:
				subset.append(record)

		return subset

	def getAttrEnthropy(self, data, attr):
		""" get attribute enthropy """
		
		sizeData = len(data)
		sum = 0
		
		domain = self.domain.get(attr)

		for group in domain.get('groups'):
			subset = self.getSubset(data, attr, group)

			e, c = self.getEnthropy(subset)
			sum += len(subset)/sizeData * e

		return sum

	def getEnthropy(self, data):
		""" get information enthropy """

		numRecords = len(data)
		category = self.domain.get(self.category)
		sum = 0
		c = None
		t = 0

		for choice in category.get('groups'):
			chosen = 0

			for record in data:
				if record.get(self.category).get('name') == choice:
					chosen += 1

			if numRecords != 0:
				probability = float(chosen) / float(numRecords)
			else:
				probability = 1

			if probability == 0:
				log = 0
			else:
				log = math.log(probability, 2)

			sum += probability * log

			if chosen > t:
				t = chosen
				c = choice

		return -sum, c

	def selectSplit(self, data, attrs, thresh):
		""" selects the best attribute to split the data """

		e0, choice = self.getEnthropy(data)
		entropies = {}
		gain = {}

		for attr in attrs:
			entropies[attr] = self.getAttrEnthropy(data, attr)
			gain[attr] = e0 - entropies[attr]

		best = max(gain, key=lambda x: x[0])
		if gain[best] > thresh:
			return best
		else:
			return None

	def C45(self, data, attrs, thresh):
		""" apply the c45 algorithm to data """

		e, choice = self.getEnthropy(data)
		node = None

		if e == 0:
			return Node(choice)
		elif len(attrs) == 0:
			return Node(choice)
		else:
			split = self.selectSplit(data, attrs, thresh)

			if split is None:
				return Node(choice)
			else:
				node = Node(split)

				for i, group in enumerate(self.domain.get(split).get('groups')):
					subset = self.getSubset(data, split, group)
					if len(subset) > 0:
						newAttrs = attrs[:]
						newAttrs.remove(split)
						child = self.C45(subset, newAttrs, thresh)
						node.addEdge(group, i + 1, child)

		return node

	def applyC45(self):
		tree = self.C45(self.records, self.attributes[:len(self.attributes) - 1], 0)

		return tree

def printTree(node):
	print "node: %s" % node.getLabel()

	for edge in node.getEdges():
		print "edge: %s" % edge.getLabel()
		print "num: %d" % edge.getNum()
		printTree(edge.getToNode())

def buildDecision(element, node):
	decision = ET.Element('decision')
	decision.choice = node.getLabel()

	element.append(decision)

	return element

def buildEdge(element, edge):
	edge_element = ET.Element('edge')
	edge_element.var = edge.getLabel()
	edge_element.num = edge.getNum()

	buildNode(edge_element, edge.getToNode())

def buildNode(element, node):
	element_node = ET.Element('node')
	element_node.var = node.getLabel()

	if node.hasEdges():
		for edge in node.getEdges():
			buildEdge(node, edge)
	else:
		element_node.append(buildDecision(element_node, node))

	element.append(element_node)
	return element

def buildXML(node):
	tree = ET.Element('tree')
	
	tree = buildNode(tree, node)
	t = ET.tostring(tree)

	print t


if __name__ == '__main__':
	domain = sys.argv[1]
	raw_data = sys.argv[2]
	if len(sys.argv) > 3:
		restriction = sys.argv[3]
	
	ts = TrainingSet()

	fp = open(raw_data, 'r')

	ts.getDomain(domain)
	#ts.printDomain()
	ts.getTrainingSet(fp)
	#ts.printRecords()
	node = ts.applyC45()

	buildXML(node)







