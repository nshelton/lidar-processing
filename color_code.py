
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
print(matches[:2])

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

for obj_filename in matches:
	print("Reading " + obj_filename)

	(verts, tris) = readMesh(obj_filename);

	num_verts = verts.shape[0]
	num_tris = tris.shape[0]

	if verts.shape[0] == 0:
		continue

	print ("---" )
	v_max = np.amax(verts, axis=0) 
	v_min = np.amin(verts, axis=0) 
	v_range = v_max-v_min

	colors = np.ones(verts.shape)
	mask = np.zeros(num_verts)

	v_labels = np.zeros(num_verts)

	for i in range(num_verts):
		d_min = np.abs(verts[i] - v_min);
		d_max = np.abs(verts[i] - v_max);
		th = 0.1;
		if d_min[0] < th or d_min[1] < th or d_max[0] < th or d_max[1] < th or d_min[2] < th :
			mask[i] = 10


	tri_mask = np.zeros(num_tris, dtype=np.bool)
	 # cull tris
	print v_labels.shape
	for j in range(num_tris):
		num_bordering = 0
		for jj in range(3):
			if (mask[tris[j][jj]] > 0 ) :
				num_bordering += 1

		if num_bordering > 0:
			tri_mask[j] = 1

		for jj in range(3):
			v_labels[tris[j][jj]] = max(v_labels[tris[j][jj]],  num_bordering)


	# #label triangles for removal
	# for j in range(num_tris):
	# 	remove = 0;
	# 	for jj in range(3):
	# 		if (v_labels[tris[j][jj]] == 2 ) :
	# 			remove = 1

	# 	tri_mask[j] = remove

	for k in range(num_verts):
		if v_labels[k] == 1:
			colors[k] = [255, 0, 255];
		if v_labels[k] == 2:
			colors[k] = [0, 255, 255];
		if v_labels[k] == 3:
			colors[k] = [255, 255, 0];

	for k in range(num_tris):
		if tri_mask[k]:
			tris[k] = [0, 0, 0];




	if all_tris.shape[0] == 0:
		all_tris = tris
	else:
		tris += all_verts. shape[0]
		all_tris = np.vstack((all_tris, tris))

	if all_verts.shape[0] == 0:
		all_verts = verts;
	else:
		all_verts = np.vstack((all_verts, verts))

	if all_colors.shape[0] == 0:
		all_colors = colors;
	else:
		all_colors = np.vstack((all_colors, colors))

	print "Points %f " % num_verts
	print "total_Points %f " % all_verts.shape[0]

writeMesh(all_verts, all_colors, all_tris, "color.merged.obj")

