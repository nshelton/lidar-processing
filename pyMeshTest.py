
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

matches = glob.glob(sys.argv[1])
print("= = = = = = = = = Merging = = = = = = = = = =")
print(matches)


dims = np.array([5,4])

for y in [0] : 
	print("merging COL %d" % y)
	filename = "dec.test0.%d.obj" % y
	total = pymesh.load_mesh(filename)
	

	for x in range(1, dims[0]) : 
		filename = "dec.test%d.%d.obj" % (x,y)

		print("loading " + filename)

		to_merge = pymesh.load_mesh(filename)


		print("%d verts" % (to_merge.num_vertices))
		start = time.time()

		total = pymesh.boolean(total, to_merge, operation="union")
		print("Merged in %f" % (time.time() - start))
		print("Exporting Master %dpts, %dfaces" % (total.num_vertices, total.num_faces) )
		
		column_name = "col%d.obj" % y
		pymesh.save_mesh(column_name, total)

		subprocess.call(["commandlineDecimater", "-M", "AR", "-M", "NF", "-M", "ND:80", "-n", "0.1", "-i", column_name, "-o", "min." + column_name])

		total = pymesh.load_mesh(column_name)
