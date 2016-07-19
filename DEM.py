#!/usr/bin/python2.7
# -*- coding: iso-8859-15 -*-
import pandas as pd
import time

import numpy as np
import sys



# print (data.shape)



# print data

# tilesize = 2000

# for tx in range(data.shape[0] / tilesize) :
# 	for ty in range(data.shape[1] / tilesize) :
#  		a_x = tx * tilesize
# 		b_x = (tx + 1) * tilesize
# 		a_y = ty * tilesize
# 		b_y = (ty + 1) * tilesize
# 		print("let's save %d:%d %d:%d" % (tx, ty))
# 		name = "dem.%d.%d.txt" %(tx, ty)
# 		np.savetxt(name, data[a_x:b_x,a_y:b_y], delimiter=" ")

# exit(0)

for tx in range(6) :
	for ty in range(7) :
		name = "dem.%d.%d" % (tx, ty)

		start = time.time()
		data = pd.read_csv(name +".txt", delimiter=" ").values
		print (time.time() - start)

		outfile = file(name + ".xyz", "w+")
		print("converting %d, %d" % (tx, ty))
		for x in range(data.shape[0]):
			for y in range(data.shape[1]):
				outfile.write("%f %f %f\n" % (x, y, data[x, y]))

		outfile.close()

# f = open(sys.argv[1], "r")

# maxlines = 0
# for line in f:
# 	if maxlines > 50:
# 		break
# 	maxlines+= 1
# 	print (line)
# 	outfile.write(line)
	# print (len(line.split()))

# ncols         15661
# nrows         12529
# xllcorner     -123.3000462963
# yllcorner     37.319953718265
# cellsize      9.259259e-005
# NODATA_value  -9999

