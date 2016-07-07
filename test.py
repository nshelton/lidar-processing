
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


def tileName(x, y, l) :
	return " dec.l%d.%d.%d.obj" % ( l, x, y)


def tryGetTile(x, y, l):
	decname = tileName(x, y, l)
	if(os.path.exists(decname)):
		return pymesh.load_mesh(decname)
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
		merged = pymesh.boolean(f1, f2, operation="union")
		print("\tmerged in %f" % (time.time() - start))

	meshBuffer[index] = merged
	readyMutex[index] = 1
# matches = glob.glob(sys.argv[1])
# print("= = = = = = = = = Tiles = = = = = = = = = =")
# print(matches)




print("= = = = = = = = = Merges = = = = = = = = = =")

x = 0
y = 0
l = 0


readyMutex = [0, 0]
result_name = "output.obj"

ta = tryGetTile(x, y, l)
tb = tryGetTile(x+1, y, l)
tc = tryGetTile(x, y+1, l)
td = tryGetTile(x+1, y+1, l)

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

if meshBuffer[0] != "" :
	pymesh.save_mesh(result_name, meshBuffer[0])
	# subprocess.call(["commandlineDecimater", "-M", "AR", "-M", "NF", "-M", "ND:80", "-n", "0.1", "-i", result_name, "-o", dec_result_name])


exit(0)
