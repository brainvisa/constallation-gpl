#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
#
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.

from brainvisa.processes import *
from brainvisa import anatomist as ana
from soma import aims
import numpy
import exceptions
try:
    import constel.lib.connmatrix.connmatrixtools as CM
except:
    pass

def validation():
  try:
      import constel.lib.connmatrix.connmatrixtools as CM
  except:
      raise ValidationError( 'constel module is not available' )

name = 'Anatomist view reorder matrix from labeled texture'
userLevel = 2
roles = ( 'viewer', )

signature = Signature(
    'clustering_texture', ReadDiskItem('Group Clustering Texture', 
                                       'anatomist texture formats'),
    'connectivity_matrix', ReadDiskItem('Group matrix', 
                                        'aims readable volume formats'),
    'time_step', Integer(),
    'transpose', Boolean(),
)

def initialization( self ):
    self.linkParameters('connectivity_matrix', 'clustering_texture') 

def execution(self, context):
    
    a = ana.Anatomist()

    # load a matrix of size (nb_basins, vertices_patch)
    matrix = aims.read(self.connectivity_matrix.fullPath()) 
    matrix = numpy.asarray(matrix)[:,:,0,0]

    clusters = aims.read(self.clustering_texture.fullPath())
    
    matrix = numpy.transpose(matrix)

    # retrieves the vertices corresponding to patch
    labels = clusters[self.time_step].arraydata()[
        clusters[self.time_step].arraydata() != 0]
    
    order_mat, sortLabels = CM.orderDataMatrix(matrix, labels)
    
    dissmatrix = CM.euclidianDistanceMatrix(order_mat)

    (n, p) = order_mat.shape
    (i, j) = dissmatrix.shape
    lines_length = 100.0
    cols_length = 80.0
    row_thickness = 50
        
    mat_ima = aims.Volume_FLOAT(n, p, 1, 1)
    mat_ima_array = mat_ima.arraydata()
    mat_ima_array[0,0,:,:] = order_mat.transpose()

    dissmat_ima = aims.Volume_FLOAT(i, j, 1, 1)
    dissmat_ima_array = dissmat_ima.arraydata()
    dissmat_ima_array[ 0, 0, :, : ] = dissmatrix.transpose()

    if n == p:
        mat_ima.header()['voxel_size'] = aims.vector_FLOAT([lines_length / n, lines_length / p, 1, 1])
        dissmat_ima.header()['voxel_size'] = aims.vector_FLOAT([lines_length / i, lines_length / j, 1, 1])
    else:
        mat_ima.header()['voxel_size'] = aims.vector_FLOAT([lines_length / n, cols_length / p, 1, 1])
        dissmat_ima.header()['voxel_size'] = aims.vector_FLOAT([lines_length / i, cols_length / j, 1, 1])

    labels_ima = aims.Volume_FLOAT(sortLabels.size, row_thickness, 1, 1)
    labels_ima_array = labels_ima.arraydata()
    labels_ima.header()['voxel_size'] = aims.vector_FLOAT([lines_length / sortLabels.size, 1, 1, 1])
    for i in xrange(row_thickness):
        labels_ima_array[0, 0, i, :] = sortLabels

    mat_ima = a.toAObject(mat_ima)
    labels_ima = a.toAObject(labels_ima)
    dissmat_ima = a.toAObject(dissmat_ima)

    mat_ima.releaseAppRef()
    labels_ima.releaseAppRef()
    dissmat_ima.releaseAppRef()
    
    mat_ima.setPalette(palette = 'random')
    labels_ima.setPalette(palette = 'random')
    dissmat_ima.setPalette(palette = 'random')
    
    wgroup = a.createWindowsBlock(nbCols = 2)
    win1 = a.createWindow('Axial', block = wgroup)
    win2 = a.createWindow('Axial', block = wgroup)
    win3 = a.createWindow('Axial', block = wgroup)
    #win4 = a.createWindow('Axial', block = wgroup)
    br = a.createWindow('Browser', block = wgroup)
    win1.addObjects(mat_ima)
    win2.addObjects(dissmat_ima)
    win3.addObjects(labels_ima)
    #win4.addObjects( [ mat_ima, labels_ima ] )
    br.addObjects([mat_ima, dissmat_ima, labels_ima])

    return [win1, win2, win3, br, labels_ima, mat_ima, dissmat_ima]

