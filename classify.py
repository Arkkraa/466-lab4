import sys


def getData(fp):
	data = fp.read().splitlines()

	for line in data:
		


if __name__ == '__main__':
	raw_data = sys.argv[1]
	fp = open(raw_data, 'r')

	data = getData(fp)