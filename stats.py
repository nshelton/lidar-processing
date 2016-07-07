#!/usr/bin/python2.7
# -*- coding: iso-8859-15 -*-

from __future__ import print_function
import glob
import numpy as np
import pandas as pd
# from mpl_toolkits.mplot3d import Axes3D
# import matplotlib.pyplot as plt
import time
import mcubes
from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage.filters import gaussian_laplace
from scipy import ndimage
import datetime
import subprocess
import os

import sys
import glob
from scipy import spatial


translate = np.array([3113903.000000, 10072758.300000, 504.980011])

def translate_obj(filename, translation) : 
	subprocess.call(["cp", filename, filename+".bak"])
	subprocess.call(["rm", filename])
	infile = file(filename + ".bak")
	outfile = file(filename, "w+")
	for line in infile:
		if line[0] == 'v':
			fields = line.split()
			outfile.write("v %f %f %f\n" % (float(fields[1]) + translation[0], float(fields[2]) + translation[1], float(fields[3]) + translation[2]))
		else:
			outfile.write(line)

	infile.close()
	
	outfile.close()

	subprocess.call(["rm", filename+".bak"])

def print_stats(filename) : 
	print(filename)
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

	center = v_min+v_range/2

	print(center)

	if center[0] > 10000:
		print("Subtract")
		translate_obj(filename, -translate)


	if center[0] < -10000:
		print("Add")
		translate_obj(filename, translate)

	print("\t Extrema: %s  --> %s " % (v_min, v_max))
	print("\t Range: %s " % (v_range))

matches = glob.glob(sys.argv[1])
print(matches)

for file_name in matches:
	print_stats(file_name)

