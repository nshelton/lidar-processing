
from __future__ import print_function
import sys
import numpy as np
import glob
from scipy import spatial
import matplotlib
from matplotlib import cm


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


# remove all vertices within a threshold of the edge

def getVertexToEdgeDistances(verts) :

	v_max = np.amax(verts, axis=0) 
	v_min = np.amin(verts, axis=0) 

	n_verts = verts.shape[0]
	distances = np.zeros(n_verts)

	for i in range(n_verts):
		distances[i] = min(np.min(abs(verts[i] - v_min)) , np.min(abs(verts[i] - v_max))) + 1


	return distances

def faceFilter(faces, dist, th) :
	filtered = []

	for i in range(faces.shape[0]) :
		a = faces[i][0]
		b = faces[i][1]
		c = faces[i][2]

		if dist[a] > th or dist[b] > th or dist[c] > th :
			filtered.append(faces[i])

	return np.array(filtered)


def colorify(verts, dist):
	cmap = matplotlib.cm.get_cmap('inferno')

	v_max = np.amax(verts, axis=0) 
	v_min = np.amin(verts, axis=0) 
	v_range = v_max - v_min

	colors = np.zeros(verts.shape)
	for i in range(verts.shape[0]):
		if dist[i] < 2 :
			colors[i] = [255, 0, 255]
		else:
			c = min(max(0, dist[i] * 2), 255)
			colors[i] = cmap((verts[i][2] - v_min[2])/v_range[2])[0:3]

	return colors

def inRange(p, min, max):
	#ignore z here
	return p[0] > min[0] and p[0] < max[0] and p[1] > min[1] and p[1] < max[1]


def determineOverlap(v1, v2):
	v1_max = np.amax(v1, axis=0) 
	v1_min = np.amin(v1, axis=0)

	v2_max = np.amax(v2, axis=0) 
	v2_min = np.amin(v2, axis=0) 

	v1_in_v2 = 0
	v2_in_v1 = 0

	overlap1 = []
	overlap2 = []

	for i in range(v1.shape[0]) :
		if inRange(v1[i], v2_min, v2_max) :
			overlap1.append(i)
			v1_in_v2 += 1

	for i in range(v2.shape[0]) :
		if inRange(v2[i], v1_min, v1_max) :
			overlap2.append(i)
			v2_in_v1 += 1

	print("Overlap is: v1_in_v2:%d , \t v2_in_v1: %d" % (v1_in_v2, v2_in_v1) )
	return (np.array(overlap1), np.array(overlap2))

def removeFacesWithVertexIndices(tris, indices) :
	relatedVertices = []
	for i in range(tris.shape[0]) :
		num_involved = 0
		for x in range(3):
			if tris[i][x] in indices :
				num_involved += 1

		if num_involved > 2 :
			tris[i] = [0, 0, 0]

	return relatedVertices

#############################################################################
##---------------------------------------------------------------------------

matches = glob.glob(sys.argv[1])
print("= = = = = = = = = Merging = = = = = = = = = =")
print(matches[0], matches[1])

# print num_match
mesh1 = matches[0]
mesh2 = matches[1]
print("Reading " + mesh1)
(vert1, tri1) = readMesh(mesh1);
print("%d points, %d tris" % (vert1.shape[0], tri1.shape[0]) )

print("Reading " + mesh2)
(vert2, tri2) = readMesh(mesh2);
print("%d points, %d tris" % (vert2.shape[0], tri2.shape[0]) )

# tree1 = spatial.KDTree(vert1);
# tree2 = spatial.KDTree(vert2);

edgeMask = np.zeros(vert1.shape[0])
mergeMaskVerts2 = np.zeros(vert1.shape[0])
numEdges = 0
edgesProcessed = 0

remove_th = 1
merge_th = 10
edge_th = 0.1

dist1 = getVertexToEdgeDistances(vert1)
dist2 = getVertexToEdgeDistances(vert2)

tri1 = faceFilter(tri1, dist1, remove_th)
tri2 = faceFilter(tri2, dist2, remove_th)


color1 = colorify(vert1, dist1)
color2 = colorify(vert2, dist2)

(ov1, ov2) = determineOverlap(vert1, vert2)

relatedVerts1 = removeFacesWithVertexIndices(tri1, ov1)
relatedVerts2 = removeFacesWithVertexIndices(tri2, ov2)

writeMesh(vert1, color1, tri1, "cull1.obj")
writeMesh(vert2, color2, tri2, "cull2.obj")

overlap = []
overlapColors = []

for i in ov1:
	if ( dist1[i] > 2):
		overlap.append(vert1[i])
		overlapColors.append([0,100,255])
for i in relatedVerts1:
	overlap.append(vert1[i])
	overlapColors.append([0,100,255])

for i in ov2:
	if ( dist2[i] > 2):
		overlap.append(vert2[i])
		overlapColors.append([100,255,0])
for i in relatedVerts2:
	overlap.append(vert2[i])
	overlapColors.append([100,255,0])

writeMesh(overlap, overlapColors, [], "border.obj")

exit(0)




# num_merge = 0
# th = 10

# for i in range(vert1.shape[0]):
# 	if dist1[i] < merge_th:
# 		(dist, index) = tree2.query(vert1[i])
# 		if dist < merge_th * 10 :
# 			edgesProcessed += 1
# 			mergeMaskVerts2[index] = i
# 			num_merge += 1
# 			print ('>>%d %d%%' % (i, 100 * i / vert1.shape[0] ), end='\r')
# 			sys.stdout.flush()

# print("MERGE %d vertices" % num_merge)
# # make the triangles from vert2 point to verts in vert1 
# for i in range(tri2.shape[0]):	
# 	for j in range(3):
# 		if mergeMaskVerts2[tri2[i][j]] > 0 :
# 			tri2[i][j] = mergeMaskVerts2[tri2[i][j]]
# 		else :
# 			tri2[i][j] += vert1.shape[0]







# MERGE MESHES
# tri2 = tri2 + vert1.shape[0]
all_tris = np.vstack((tri1, tri2))
all_verts = np.vstack((vert1, vert2))
colors = np.ones(all_verts.shape)
all_dist = np.hstack((dist1, dist2))

#color function
cmap = matplotlib.cm.get_cmap('inferno')

v_max = np.amax(all_verts, axis=0) 
v_min = np.amin(all_verts, axis=0) 
v_range = v_max - v_min

for i in range(all_verts.shape[0]):
	if all_dist[i] < 1 :
		colors[i] = [255, 0, 255]
	else:
		c = min(max(0, all_dist[i] * 2), 255)
		colors[i] = cmap((all_verts[i][2] - v_min[2])/v_range[2])[0:3]

print("total points %f " % all_verts.shape[0])
print("total faces: %f " % all_tris.shape[0])

print(np.min(all_tris))
print(np.max(all_tris))

writeMesh(all_verts, colors, all_tris, "smooth.merged.obj")


