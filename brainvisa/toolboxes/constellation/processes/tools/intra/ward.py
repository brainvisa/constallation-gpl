from brainvisa.processes import *
from soma import aims
import scipy
import scipy.cluster.hierarchy
import scipy.spatial.distance
from soma.path import find_in_path
import os
import numpy as np

def validation():
    if not find_in_path( 'constelConnectionDensityTexture' ):
        raise ValidationError( 'constellation module is not here.' )

name = 'Clustering Ward'
userLevel = 2

signature = Signature( 
    'group_matrix', ReadDiskItem('Group Matrix', 'GIS image'),
    'output_directory', ReadDiskItem( 'Directory', 'Directory' ),
)

def initialization (self):
    pass

def execution(self, context):
    '''Use hieararchical clustering to identify patterns.
    '''
    # Load the matrix
    matrix = aims.read(self.group_matrix.fullPath())
    mat = np.asarray(matrix)[:, :, 0, 0]
    n, p = s = mat.shape
    # Compute linkage
    Z = scipy.cluster.hierarchy.linkage(mat, method='ward', metric='euclidean')
    OUTPUT_DIR_FMT = '/home/sl236442'
    TS = []
    for nb in n_clusters:
        print "Trying {nb} cluster(s)".format(nb=nb)
        T = scipy.cluster.hierarchy.fcluster(Z,criterion='maxclust',t=nb)
        T = T - 1
        TS.append(T)
        output_dir = OUTPUT_DIR_FMT.format(k=nb)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        assign_filename = os.path.join(output_dir, "assign.npy")
        np.save(assign_filename, T)
        centers = np.zeros((nb, p))
        for i in range(nb):
            index = np.where(T == i)[0]
            all_data = mat[index]
            mean_data = all_data.mean(axis=0)
            centers[i] = mean_data
        centers_filename = os.path.join(output_dir, "centers.npy")
        np.save(centers_filename, centers)
        dst_to_centers = scipy.spatial.distance.cdist(mat, centers)
        dst_to_centers_filename = os.path.join(output_dir, "dst_to_centers.npy")
        np.save(dst_to_centers_filename, dst_to_centers)
        n_points_per_cluster_filename = os.path.join(output_dir, "n_points_per_cluster.txt")
        f = open(n_points_per_cluster_filename, "w+")
        for i in range(nb):
            index = np.where(T == i)[0]
            print >> f, index.shape[0]
            dst_to_this_center = dst_to_centers[:, i]
            closest_subject_index = np.argmin(dst_to_this_center)
                                                                        
        f.close()