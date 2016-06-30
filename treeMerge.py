
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
import math
import os.path


def writeMesh(v, c, t, filename):
	objFile = open(filename, "w");

	# write obj vertices
	for i in range(len(v)):
		objFile.write("v %f %f %f %f %f %f\n" % (v[i][0], v[i][1], v[i][2], c[i][0], c[i][1], c[i][2]))

	# write obj triangles
	for i in range(len(t)):
		objFile.write("f %d %d %d\n" % (t[i][0]+1, t[i][1]+1, t[i][2]+1 ))

	print("\t Exporting %s (%d verts , %d tris)" % (filename, len(v), len(t)))
	objFile.close()


def colorize(filename):

	mesh = pymesh.load_mesh(filename)
	vert = mesh.vertices
	tri = mesh.faces 

	cmap = matplotlib.cm.get_cmap('inferno')

	v_max = np.amax(vert, axis=0) 
	v_min = np.amin(vert, axis=0) 
	v_range = v_max - v_min

	colors = np.zeros(vert.shape)

	for i in range(vert.shape[0]):
		colors[i] = cmap((vert[i][2] - v_min[2])/v_range[2])[0:3]

	writeMesh(vert, colors, tri, "color." + filename)

#############################################################################
##---------------------------------------------------------------------------

def tileName(x, y) :
	return "dec.test%d.%d.obj" % (x, y)

def tryGetTile(x, y):
	name = tileName(x,y)
	print(name)
	if(os.path.exists(name)):
		return pymesh.load_mesh(name)
	else :
		return ""


def tryMerge(f1, f2):
	if f1 == "" and f2 == "" :
		return ""
	if f1 == "" :
		return f2
	if f2 == "" :
		return f1
	else:
		start = time.time()
		merged = pymesh.boolean(f1, f2, operation="union")
		print("\tmerged in %f" % (time.time() - start))
		return merged

matches = glob.glob(sys.argv[1])
print("= = = = = = = = = Tiles = = = = = = = = = =")
# print(matches)


tx = 6
ty = 5

baseLevel = []

for x in range(tx):
	baseLevel.append([])
	for y in range(ty):
		baseLevel[x].append(tileName(x,y))

	print(baseLevel[x])

print("= = = = = = = = = Merges = = = = = = = = = =")

#recursive step
for x in range(int(math.ceil(len(baseLevel) / 2.0))) :	
	for y in range(int(math.ceil(len(baseLevel[x]) / 2.0))) :
		ta = tryGetTile(2 * x + 0, 2 * y + 0)
		tb = tryGetTile(2 * x + 1, 2 * y + 0)
		tc = tryGetTile(2 * x + 0, 2 * y + 1)
		td = tryGetTile(2 * x + 1, 2 * y + 1)

		# TODO : Multithread dis bish??
		print(" === Merge ======> %s, %s" % (ta, tb))
		tab = tryMerge(ta, tb)
		
		print(" === Merge ======> %s, %s" % (tc, td))
		tcd = tryMerge(tc, td)

		result_name = "l1.%d.%d.obj" % (x, y)
		print(" === Merge Both ======> %s " % result_name)
		full_tile = tryMerge(tab, tcd)
		pymesh.save_mesh(result_name, full_tile)
		# subprocess.call(["commandlineDecimater", "-M", "AR", "-M", "NF", "-M", "ND:80", "-n", "0.1", "-i", result_name, "-o", "min." + result_name])


exit(0)
