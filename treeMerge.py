
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
import thread


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

meshBuffer = [0, 0]
readyMutex = [0, 0]
block = "swc1"


def decTileName(x, y, l) :
	return "%s-tiles/dec.l%d.%d.%d.obj" % (block, l, x, y)

def tileName(x, y, l) :
	return "%s-tiles/l%d.%d.%d.obj" % (block, l, x, y)

def tryGetTile(x, y, l):
	decname = decTileName(x, y, l)
	if(os.path.exists(decname)):
		return pymesh.load_mesh(decname)
	name = tileName(x, y, l)
	if(os.path.exists(name)):
		print("loaded ", name)
		# return pymesh.load_mesh(name)
	else :
		return ""


def tryMerge(f1, f2, index):
	merged = ""
	if f1 == "" and f2 == "" :
		merged = ""
	if f1 == "" :
		merged = f2
	if f2 == "" :
		merged = f1
	else:
		start = time.time()
		# merged = pymesh.boolean(f1, f2, operation="union")
		print("\tmerged in %f" % (time.time() - start))

	meshBuffer[index] = merged
	readyMutex[index] = 1
# matches = glob.glob(sys.argv[1])
# print("= = = = = = = = = Tiles = = = = = = = = = =")
# print(matches)



tx = 16
ty = 16

print("= = = = = = = = = Merges = = = = = = = = = =")
levels = 4

for l in range(levels) :
	tx /=2
	ty /=2

	for x in range(tx):
		for y in range(ty):
			readyMutex = [0, 0]
			result_name = "%s-tiles/l%d.%d.%d.obj" % (block, l+1, x, y)
			dec_result_name = "%s-tiles/dec.l%d.%d.%d.obj" % (block, l+1, x, y)

			if(os.path.exists(result_name) or os.path.exists(dec_result_name) ):
				print("tile %s exists, skipping" % result_name)
				continue

			ta = tryGetTile(2 * x + 0, 2 * y + 0, l)
			tb = tryGetTile(2 * x + 1, 2 * y + 0, l)
			tc = tryGetTile(2 * x + 0, 2 * y + 1, l)
			td = tryGetTile(2 * x + 1, 2 * y + 1, l)

			start = time.time()

			print(" === Merge ======> %s, %s" % (ta, tb))
			thread.start_new_thread(tryMerge, (ta, tb, 0 ))
			
			print(" === Merge ======> %s, %s" % (tc, td))
			thread.start_new_thread(tryMerge, (tc, td, 1 ))

			# wait to finish
			while readyMutex[0] == 0 and readyMutex[1] == 0 :
				time.sleep(1)

			print("\with multithreading: %f" % (time.time() - start))

			print(" === Merge Both ======> %s " % result_name)
			tryMerge(meshBuffer[0], meshBuffer[1], 0)

			# wait to finis	h
			while readyMutex[0] == 0 :
				time.sleep(1)

			# if meshBuffer[0] != "" :
				# pymesh.save_mesh(result_name, meshBuffer[0])
				# subprocess.call(["commandlineDecimater", "-M", "AR", "-M", "NF", "-M", "ND:80", "-n", "0.1", "-i", result_name, "-o", dec_result_name])


exit(0)
