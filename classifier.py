import sys
import re
import pprint
import xml.etree.ElementTree as ET
from c45 import Node
from c45 import Edge

class Classifier:
	def __init__(self):
		self.ts = None
		self.attr = None
		self.records = []

	def addAttributes(self, attr):
		self.attr = attr

	def loadTS(self, xml):
		self.ts = ET.parse(xml).getroot()

	def addData(self, data):
		record = {}

		for i, group in enumerate(data):
			if not group.isdigit():
				record[self.attr[i]] = group

		record['record'] = data
		self.records.append(record)

	def loadData(self, fp):
		data = fp.read().splitlines()

		i = 0
		for line in data:
			line = re.split(r',', line)
			if i == 0:
				self.addAttributes(line[1:])
			if i == 1:
				wut = "wut about sizes?"
			if i == 2:
				if len(line) > 1:
					self.addData(line[1:])
			if i > 2:
				self.addData(line[1:])
			i += 1


	def processNode(self, record, node, nodeName):
		record_val = record[nodeName]
		for edge in node.findall('edge'):
			if edge.get('var') == record_val:
				if edge.find('decision') is not None:
					return edge.find('decision').get('choice')
				else:
					ret = self.processNode(record, edge.find('node'), edge.find('node').get('var'))

		return ret

	def classify(self):
		true = []
		false = []

		root = self.ts.find('node')
		rootName = root.get('var')
		for record in self.records:
			got = self.processNode(record, root, rootName)
			expected = record['record'][len(record['record']) - 1]

			print record['record'], expected, got
			if got == expected:
				true.append(record)
			else:
				false.append(record)

		acc = float(len(true)) / float(len(self.records))
		err = 1 - acc

		print "Total number of records classified: %d" % len(self.records)
		print "Total number of records correctly classified: %d" % len(true)
		print "Total number of records incorrectly classified: %d" % len(false)
		print "Accuracy: %f" % acc
		print "Error: %f" % err

if __name__ == '__main__':
	raw_data = sys.argv[1]
	xml = sys.argv[2]

	dataFp = open(raw_data, 'r')

	classifier = Classifier()

	classifier.loadTS(xml)
	classifier.loadData(dataFp)
	classifier.classify()

