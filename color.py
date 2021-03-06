
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
import os


def getRange(filename) : 
	points = []
	num_faces = 0
	infile = open(filename)

	for line in infile:
		if line[0] == 'v':
			fields = line.split()
			points.append([float(fields[1]), float(fields[2]), float(fields[3])])

		if line[0] == 'f':
			num_faces += 1

	infile.close()
	
	points = np.array(points)

	v_max = np.amax(points, axis=0) 
	v_min = np.amin(points, axis=0) 
	v_range = v_max - v_min

	return (v_min, v_max)

matches = glob.glob(sys.argv[1])
print("= = = = = = = = = Coloring = = = = = = = = = =")
print(matches)

for filename in matches:
	start = time.time()

	(p_min, p_max ) = getRange(filename)

	inFile = open(filename, "r");
	path = filename.split("/")

	path[len(path) - 1] =  "color." + path[len(path) - 1]
	outName = "/".join(path)

	if(os.path.exists(outName)):
		print("tile %s exists, skipping" % outName)
		continue


	outFile = open(outName, "w");


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

			c = cmap((float(v[2]) * 1.5 - p_min[2]/2) /(p_max[2] - p_min[2]))
			# print("color", c)

			outFile.write("v %s %s %s %s %s %s\n" % (v[0], v[1], v[2], c[0], c[1], c[2]))

		else :
			outFile.write(line)


	outFile.close()
	print("ecported " +filename)
