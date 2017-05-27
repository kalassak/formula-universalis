import random

seasons = [(1, 1), (3, 2), (4, 3), (1, 4), (1, 5), (3, 11), (4, 19), (4, 20), (4, 21), (4, 22), (4, 29), (4, 30), (4, 31), (3, 41), (4, 42), (1, 44), (4, 47), (4, 53), (4, 69), (4, 74), (4, 80), (4, 81), (4, 94), (4, 98)]
seasonstest = []

ret = 0
for x in seasons:
	if x[0] > random.gauss(7.0, 3.0):
		ret += 1
		seasons.remove(x)
		print "Driver number " + str(x[1]) + " has decided to retire."

print ret
print seasons