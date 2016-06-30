
from __future__ import print_function
import sys
import numpy as np
import glob
from scipy import spatial
import matplotlib
from matplotlib import cm
import pymesh
import time
import subprocess



matches = glob.glob(sys.argv[1])
print("= = = = = = = = = Merging = = = = = = = = = =")
print(matches)

for filename in matches:
	start = time.time()

	inFile = open(filename, "r");
	outFile = open("color." + filename, "w");



	for line in inFile:
		result = line.split(' ')

		if result[0] == "#":
			continue

		if result[0] == "v":
			result = line.replace("\n", "").split(' ')
			# if len(result) == 7 :
				# outFile.write(line)
			# if len(result) == 4 :
			v = result[1:4]

			# print(v)

			cmap = matplotlib.cm.get_cmap('inferno')

			c = cmap(float(v[2]) / 350)
			# print("color", c)

			outFile.write("v %s %s %s %s %s %s\n" % (v[0], v[1], v[2], c[0], c[1], c[2]))

		else :
			outFile.write(line)


	outFile.close()
	print("ecported " +filename)
