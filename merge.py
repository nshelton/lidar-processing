
from __future__ import print_function
import sys
import numpy as np
import glob
from scipy import spatial


def readMesh(filename):
	infile = open(filename, "r")
	verts = []
	tris = []
	for line in infile:
		fields = line.split(' ')
		if ( fields[0] == 'v'):
  			verts.append(fields[1:])

		if ( fields[0] == 'f'):
  			tris.append([int(fields[1])-1, int(fields[2])-1, int(fields[3])-1])
	return (np.array(verts,  dtype='float'), np.array(tris,  dtype='int'))


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




#############################################################################
##---------------------------------------------------------------------------

matches = glob.glob(sys.argv[1])
print("= = = = = = = = = Merging = = = = = = = = = =")
print(matches[0], matches[1])

sys.setrecursionlimit(15000)

# print num_match
mesh1 = matches[0]
mesh2 = matches[1]
print("Reading " + mesh1)
(vert1, tri1) = readMesh(mesh1);
print("%d points, %d tris" % (vert1.shape[0], tri1.shape[0]) )

print("Reading " + mesh2)
(vert2, tri2) = readMesh(mesh2);
print("%d points, %d tris" % (vert2.shape[0], tri2.shape[0]) )

tree1 = spatial.KDTree(vert1);
tree2 = spatial.KDTree(vert2);


print("iterating through "+ mesh1)


v_max = np.amax(vert1, axis=0) 
v_min = np.amin(vert1, axis=0) 

edgeMask = np.zeros(vert1.shape[0])
numEdges = 0
edgesProcessed = 0

th = 10

#Label edge verts
for i in range(vert1.shape[0]):
	d_min = np.abs(vert1[i] - v_min);
	d_max = np.abs(vert1[i] - v_max);
	if d_min[0] < th or d_min[1] < th or d_max[0] < th or d_max[1] < th or d_min[2] < th :
		edgeMask[i] = 1
		numEdges += 1

mergeMaskVerts2 = np.zeros(vert2.shape[0])
num_merge = 0

for i in range(vert1.shape[0]):
	if edgeMask[i] > 0:
		(dist, index) = tree2.query(vert1[i])

		if dist < th * 2 :
			edgesProcessed += 1
			mergeMaskVerts2[index] = i
			num_merge += 1
			print ('>>%d %d%%' % (i, 100 * edgesProcessed / numEdges), end='\r')
			sys.stdout.flush()

print("MErgine %d vertices" % num_merge)
# make the triangles from vert2 point to verts in vert1 

for i in range(tri2.shape[0]):	
	for j in range(3):
		if mergeMaskVerts2[tri2[i][j]] > 0 :
			tri2[i][j] = mergeMaskVerts2[tri2[i][j]]
		else :
			tri2[i][j] += vert1.shape[0]

# print("merging verts: " + str(len(diffs)))

all_tris = np.vstack((tri1, tri2))
all_verts = np.vstack((vert1, vert2))
colors = np.ones(all_verts.shape)



print("total points %f " % all_verts.shape[0])
print("total faces: %f " % all_tris.shape[0])


print(np.min(all_tris))
print(np.max(all_tris))

writeMesh(all_verts, colors, all_tris, "smooth.merged.obj")


