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
import datetime
import subprocess

print ("""───▐▀▄──────▄▀▌───▄▄▄▄▄▄▄─────────────
───▌▒▒▀▄▄▄▄▀▒▒▐▄▀▀▒██▒██▒▀▀▄──────────
──▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▀▄────────
──▌▒▒▒▒▒▒▒▒▒▒▒▒▒▄▒▒▒▒▒▒▒▒▒▒▒▒▒▀▄──────
▀█▒▒█▌▒▒█▒▒▐█▒▒▀▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▌─────
▀▌▒▒▒▒▒▀▒▀▒▒▒▒▒▀▀▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▐───▄▄
▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▌▄█▒█
▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▐▒█▀─
▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▐▀───
▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▌────
─▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▐─────
─▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▌─────
──▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▐──────
──▐▄▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▄▌──────
────▀▄▄▀▀▀▀▄▄▀▀▀▀▀▀▄▄▀▀▀▀▀▀▄▄▀────────\n\n\n""")

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

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


def export(name, tile, translate) :
	print("Marching Cubes %s" % name)
	# print translate

	start = time.time()

	dim = tile.shape

	v, t = mcubes.marching_cubes(tile, 0)
	print("Reconstruction in %f" % (time.time() - start))
	obj_filename = "./%s.obj" % name
	decimated_obj = "./%s.5.obj"

	objFile = open(obj_filename, "w");

	# write obj vertices
	for i in range(len(v)):
		objFile.write("v %f %f %f\n" % (v[i][0], v[i][1], v[i][2]))

	# write obj triangles
	for i in range(len(t)):
		objFile.write("f %d %d %d\n" % (t[i][0]+1, t[i][1]+1, t[i][2]+1 ))

	print("\t Exporting %s (%d verts , %d tris) in %fs" % (name, len(v), len(t), (time.time() - start)))
	objFile.close()
	subprocess.call(["commandlineDecimater", "-M", "Q", "-n", "0.05", "-i", obj_filename, "-o", decimated_obj % name]); 

	translate_obj(obj_filename, translate)
	translate_obj(decimated_obj % name, translate)

def partition(data, total_dim, tile_dim, g_min) :
	start = time.time()
	n_tiles = np.ceil(total_dim / tile_dim)

	print("partitioning")
	print(n_tiles)

	partitions = []

	for x in range(int(n_tiles[0])):
		partitions.append([])
		for y in range(int(n_tiles[1])):
			partitions[x].append([])

	duration = (time.time() - start)
	print("\t Partitionined into %dx%d = %d in %fs" % (n_tiles[0], n_tiles[1], n_tiles[0]*n_tiles[1], duration))

	for p in data:
		x = int((p[0] - g_min[0]) / tile_dim) 
		y = int((p[1] - g_min[1]) / tile_dim)
		partitions[x][y].append(p)

	return partitions

def computeRange(pmin, pmax, p):
	for i in range(3):
		pmin[i] = min(pmin[i], p[i])
	for i in range(3):
		pmax[i] = max(pmax[i], p[i])


def populateVolume(points, vol_dim, tile_pos) :
	start = time.time()
	grid = np.ones(vol_dim)

	print("Populating %d x %d x %d volume" % grid.shape, end="\t")
	for p in points :
		p_grid = np.round(p[:3] - tile_pos) - np.ones(3)

		# print( "%d %d %d" % (p_grid[0], p_grid[1], p_grid[2]), file=f)

		for h in range( int(p_grid[2])):
			grid[p_grid[0]][p_grid[1]][h] = grid[p_grid[0]][p_grid[1]][h] - 50


		# grid[p_grid[0]] [p_grid[1]] [p_grid[2]] = -100
		
	print("in %fsec" % (time.time() - start)) 

	return grid

# ===============================================================================
# ============================== MAIN ===========================================

# files =  glob.glob("./*swc3.las.txt")
filename = "/Users/nshelton/lidar-processing/data/cinderAustin/Capitol.xyz"
programStart = time.time()

print("loading " + filename, end="\t")
start = time.time()

data = pd.read_csv(filename, delimiter=" ").values /1.4
end = time.time()
print (end - start)

p_min = np.array([1e10, 1e10, 1e10])
p_max = np.array([0, 0, 0])

for i in range(data.shape[0]) :
	computeRange(p_min, p_max, data[i])

downsample = 1
tileSize = 400

totalRange = (p_max-p_min)
tilePoints = partition(data, totalRange, tileSize, p_min)

vol_dim = np.array([tileSize,tileSize,totalRange[2]])

for tile_x in range(len(tilePoints)):
	for tile_y in range(len(tilePoints[tile_x])):
		print("Process Tile%d.%d : %d points" % ( tile_x, tile_y, len(tilePoints[tile_x][tile_y])))
		tile_pos =  p_min + np.array([tile_x,tile_y,0]) * vol_dim

		grid = populateVolume(tilePoints[tile_x][tile_y], vol_dim, tile_pos )

		filtered = gaussian_filter(grid, sigma=2, mode='constant', cval=1.0 )
		# filtered = gaussian_laplace(filtered, sigma=2, mode='nearest')

		export("test%d.%d" % (tile_x, tile_y), filtered, tile_pos)



print("total time " + str(time.time() - programStart))