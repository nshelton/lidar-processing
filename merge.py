
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
print("= = = = = = = = = MATCHES = = = = = = = = = =")
print(matches[0])

all_verts = np.array([])
all_tris = np.array([])
all_colors = np.array([])


progress = 0
verts = []
tris = []
trees = []

# for i in range(2):
# 	(v, t) = readMesh(matches[i])
# 	verts.append(v)
# 	tris.append(t)

# 	print "%d points in %s" % (v.shape[0], matches[i])
# 	# print v
# 	trees.append(spatial.KDTree(v));


# print "overlap is %d" % trees[0].count_neighbors(trees[1], 1)

# num_match = 0;

# for v in verts[1]:
# 	(dist, index) = trees[0].query(v)
# 	# print v 
# 	# print trees[0].data[index]
# 	# print v -trees[0].data[index]
# 	# print "----------"
# 	if ( dist < 1 ):
# 		# print index
# 		num_match += 1

# print num_match
obj_filename = matches[0]
print("Reading " + obj_filename)

(verts, tris) = readMesh(obj_filename);

num_verts = verts.shape[0]
num_tris = tris.shape[0]


tree = spatial.KDTree(verts);


num_match = 0;

diffs = []

for v in verts:
	(dist, index) = tree.query(v)
	diffs.append(dist)
	print "closest : %f" % dist

print num_match


print "Points %f " % num_verts
print "total_Points %f " % all_verts.shape[0]

writeMesh(all_verts, all_colors, all_tris, "color.merged.obj")

