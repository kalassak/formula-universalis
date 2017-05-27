# tests frequency of retiring

import random

seasons = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
seasonstest = []

for x in xrange(0,27):
	seasonstest.append(1)

for i in xrange(0,20):
	ret = 0
	for x in seasonstest:
		if x > random.gauss(7.0, 3.0):
			ret += 1
			seasonstest.remove(x)
			seasonstest.append(0)

	seasonstest[:] = [x + 1 for x in seasonstest]
	print ret
	print seasonstest