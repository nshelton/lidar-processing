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

margin = 0.01

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

	v, t = mcubes.marching_cubes(tile, 0.3)
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
	subprocess.call(["commandlineDecimater", "-M", "AR", "-M", "NF", "-M", "ND:50", "-n", "0.04", "-i", obj_filename, "-o", decimated_obj % name]); 

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

		if (p[0] - g_min[0]) / tile_dim - int((p[0] - g_min[0]) / tile_dim) < margin and x > 0 and  (p[1] - g_min[1]) / tile_dim - int((p[1] - g_min[1]) / tile_dim) < margin and y > 0 :
			partitions[x-1][y-1].append(p)

		if (p[0] - g_min[0]) / tile_dim - int((p[0] - g_min[0]) / tile_dim) < margin and x > 0 :
			partitions[x-1][y].append(p)

		if (p[1] - g_min[1]) / tile_dim - int((p[1] - g_min[1]) / tile_dim) < margin and y > 0 :
			partitions[x][y-1].append(p)

	return partitions

def computeRange(pmin, pmax, p):
	for i in range(3):
		pmin[i] = min(pmin[i], p[i])
	for i in range(3):
		pmax[i] = max(pmax[i], p[i])


def populateVolume(points, vol_dim, tile_pos) :
	start = time.time()
	grid = np.zeros(vol_dim * ( 1 + margin))
	out = 0

	print("Populating %d x %d x %d volume" % grid.shape, end="\t")
	for p in points :
		p_grid = np.floor(p[:3] - tile_pos)

		# print( "%d %d %d" % (p_grid[0], p_grid[1], p_grid[2]), file=f)
		if p_grid[0] < grid.shape[0] and p_grid[1] < grid.shape[1] :
			for h in range( int(p_grid[2])):
				grid[p_grid[0]][p_grid[1]][h] = 1
		else :
			out += 1

	print("%d is out of bounds" % out)

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

data = pd.read_csv(filename, delimiter=" ").values
end = time.time()
print (end - start)

p_min = np.array([1e10, 1e10, 1e10])
p_max = np.array([0, 0, 0])

for i in range(data.shape[0]) :
	computeRange(p_min, p_max, data[i])

downsample = 2
tileSize = 400

totalRange = (p_max-p_min)
tilePoints = partition(data, totalRange, tileSize, p_min) 

vol_dim = np.array([tileSize,tileSize,totalRange[2]]) 

struct = ndimage.generate_binary_structure(3,3)

for tile_x in range(len(tilePoints)):
	for tile_y in range(len(tilePoints[tile_x])):
		print("Process Tile%d.%d : %d points" % ( tile_x, tile_y, len(tilePoints[tile_x][tile_y])))
		tile_pos =  p_min + np.array([tile_x,tile_y,0]) * vol_dim

		grid = populateVolume(tilePoints[tile_x][tile_y], vol_dim, tile_pos )
		
		# grid = ndimage.binary_closing(grid, iterations=5);
		grid = ndimage.binary_dilation(grid, structure=struct);
		grid = ndimage.binary_dilation(grid, structure=struct);
		# grid = ndimage.binary_dilation(grid);
		# grid = ndimage.binary_dilation(grid);
		# grid = ndimage.binary_dilation(grid);

		grid = ndimage.binary_erosion(grid, structure=struct);
		grid = ndimage.binary_erosion(grid, structure=struct);
		# grid = ndimage.binary_erosion(grid);
		# grid = ndimage.binary_erosion(grid);
		# grid = ndimage.binary_erosion(grid);

		# grid = gaussian_filter(grid.astype(np.float), sigma=1, mode='nearest' )
		# filtered = gaussian_filter(grid, sigma=2, mode='nearest')

		export("test%d.%d" % (tile_x, tile_y), grid, tile_pos)



print("total time " + str(time.time() - programStart))