import sys
import re
import xml.etree.ElementTree as ET

class TrainingSet:
	def __init__(self, domain):
		self.domain = ET.parse(domain).getroot()
		self.sizes = None
		self.category = None
		self.names = None
		self.tset = {"Tree name": "test"}
		self.nodes = {}
		self.edges = {}

	def addNames(self, names):
	""" Add a record """
		self.names = names

	def addCategory(self, category):
	""" Add a category """
		self.category = category

	def addNumbers(self, numbers):
	""" Add numbers """
		self.numbers = numbers

	def addData(self, data):
	""" Add training data to set """

		i = 0
		for name in data:
			newNode = {}
			newEdge = {}

			newNode["var"] = self.names[i]
			newEdge["var"] = name

			for group in self.domain.findall("variable"):
				group = group.get("name")
				if group == self.names[i]:
					num = 1
					for 

			newEdge["num"] = self.domain.find()

	def createNode(self):
	""" Create a node """
		print "create node"

	def createEdge(self):
	""" Create an edge """
		print "create edge"


def getTrainingSet(fp, domain):
	ts = TrainingSet(domain)
	data = fp.read().splitlines()

	i = 1
	for line in data:
		line = re.strip(r',', line);
		if i == 1:
			ts.addNames(line[1:])
		elif i == 2:
			ts.addSizes(line[1:])
		elif i == 3:
			ts.addCategory(line[0])
		else:
			ts.addData(line[1:])

if __name__ == '__main__':
	domain = sys.argv[1]
	raw_data = sys.argv[2]
	if len(sys.argv) > 3:
		restriction = sys.argv[3]
	
	fp = open(raw_data, 'r')
	data = getTrainingSet(fp, domain)