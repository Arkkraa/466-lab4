


if __name__ == '__main__':
	test = {'lol': 2, 'lmao': 4, 'rofl': 8, 'black': 1}

	print test[max(test, key=lambda x: x[0])]