import sys
import re
import pprint
import math
import xml.etree.ElementTree as ET
from lxml import etree

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
	def __init__(self, label, num):
		self.edges = []
		self.label = label
		self.num = num

	def addEdge(self, label, num, child):
		self.edges.append(Edge(label, num, child))

	def getLabel(self):
		return self.label

	def getEdges(self):
		return self.edges

	def getNum(self):
		return self.num

class TrainingSet:
	def __init__(self):
		self.domain = {}
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
				record[self.attributes[i]] = value
			else:
				record[self.attributes[i]] = domain[value - 1]

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
			elif i == 3:
				self.addCategory(line[0])
			elif i > 3:
				self.addData(line[1:])
			i += 1

	def getDomain(self, domain):
		""" parse the domain into an easily accessible data struct """
		root = ET.parse(domain).getroot()

		for variable in root.findall('variable'):
			domain = []
			for group in variable.findall('group'):
				domain.append(group.get('name'))

			self.domain[variable.get('name')] = domain

		category = root.find('Category')
		cat = []
		for choice in category.findall('choice'):
			cat.append(choice.get('name'))

		self.domain[category.get('name')] = cat

	def getSubset(self, data, attr, value):
		""" get a subset of records with a certain attribute and value """

		subset = []

		for record in data:
			attribute = record.get(attr)
			if attribute == value:
				subset.append(record)
		#print subset
		#print "*" * 50 
		return subset

	def getAttrEnthropy(self, data, attr):
		""" get attribute enthropy """
		
		sizeData = len(data)
		sum = 0
		
		domain = self.domain.get(attr)

		for group in domain:
			subset = self.getSubset(data, attr, group)

			e, c = self.getEnthropy(subset)
			sum += float((float(len(subset))/float(sizeData)) * e)

		return sum

	def getEnthropy(self, data):
		""" get information enthropy """

		numRecords = len(data)
		#print numRecords
		category = self.domain.get(self.category)
		sum = 0
		c = None
		t = 0

		for choice in category:
			chosen = 0

			for record in data:
				if record.get(self.category) == choice:
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
		#entropies = {}
		gain = {}

		for attr in attrs:
			#entropies[attr] = self.getAttrEnthropy(data, attr)
			entropy = self.getAttrEnthropy(data, attr)
			
			gain[attr] = e0 - entropy

		best = max(gain, key=lambda x: x[0])
		if gain[best] > thresh:
			return best
		else:
			return None

	def C45(self, data, attrs, thresh):
		""" apply the c45 algorithm to data """

		e, choice = self.getEnthropy(data)
		node = None
		num = self.domain.get(self.category).index(choice) + 1

		if e == 0:
			return Node(choice, num)
		elif len(attrs) == 0:
			return Node(choice, num)
		else:
			split = self.selectSplit(data, attrs, thresh)
			if split is None:
				return Node(choice, num)
			else:
				node = Node(split, 0)

				for i, group in enumerate(self.domain.get(split)):
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

def buildDecision(node):
	decision = etree.Element('decision', choice=node.getLabel(), end=str(node.getNum()))

	return decision

def buildEdge(edge):
	edge_element = etree.Element('edge', var=edge.getLabel(), num=str(edge.getNum()))

	rest = buildNode(edge.getToNode())
	edge_element.append(rest)
	return edge_element


def buildNode(node):

	node_element = etree.Element('node', var=node.getLabel())

	if len(node.getEdges()) > 0:
		for edge in node.getEdges():
			rest = buildEdge(edge)
			node_element.append(rest)
	else:
		return buildDecision(node)

	return node_element

def buildXML(node):
	tree = etree.Element('tree')
	
	tree.append(buildNode(node))

	print etree.tostring(tree, pretty_print=True)

	xml = ET.ElementTree(tree)
	xml.write("tree.xml")


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
	#printTree(node)

	buildXML(node)







