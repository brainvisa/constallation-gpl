# -*- coding: utf-8 -*-
#  This software and supporting documentation are distributed by
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
import numpy as np
import pylab
import scipy
import scipy.cluster.hierarchy as sch
import constel.lib.connmatrix.connmatrixtools as cm
from soma import aims

name = 'Dendrogram'
userLevel = 2

signature = Signature(
  'connectivity_matrix', ReadDiskItem( 'Group Matrix', 'GIS image' ),
  'transpose', Boolean(),
  'distance', Choice( ( 'correlation', 'c' ),
                      ( 'absolute value of correlation', 'a' ),
                      ( 'uncentered correlation', 'u' ),
                      ( 'Absolute uncentered correlation', 'x' ),
                      ( 'Spearman\'s rank correlation', 's' ),
                      ( 'Kendall\'s', 'k' ),
                      ( 'Euclidean', 'e' ),
                      ( 'City-block', 'b' ) ),
  'directory', ReadDiskItem( 'Directory', 'Directory' )
)

def initialization ( self ):
  self.distance = 'Euclidean'
  self.linkParameters( 'directory', 'connectivity_matrix' )

def execution ( self, context ):
  # Load connectivity matrix
  matrixFile = str(self.connectivity_matrix)
  vects = aims.read( matrixFile )
  if not self.transpose:
     matrix = np.asarray( vects )[ :, :, 0, 0 ]
  else:
    matrix = np.asarray( vects )[ :, :, 0, 0 ].transpose()
    print 'Transpose of a matrix.'

  Nsample = matrix.shape[0]
  Ndim = matrix.shape[1]

  # Calculate distance matrix
  
  distMat = cm.euclidianDistanceMatrix( matrix )
   
  # Compute and plot first dendrogram 
  fig = pylab.figure()
  axdendro1 = fig.add_axes( [ 0.09, 0.1, 0.2, 0.6] )
  Y = sch.linkage( distMat, method = 'centroid' )
  Z1 = sch.dendrogram( Y, orientation = 'right' )
  axdendro1.set_xticks( [] )
  axdendro1.set_yticks( [] )

  # Compute and plot second dendrogram.
  axdendro2 = fig.add_axes( [ 0.3, 0.71, 0.6, 0.2 ] )
  Y = sch.linkage( distMat, method = 'average' )
  Z2 = sch.dendrogram( Y )
  axdendro2.set_xticks([])
  axdendro2.set_yticks([])
  
  # Plot distance matrix.
  axmatrix = fig.add_axes( [ 0.3, 0.1, 0.6, 0.6 ] )
  index1 = Z1[ 'leaves' ]
  index2 = Z2[ 'leaves' ]
  distMat = distMat[index1, :]
  distMat = distMat[:, index2]
  im = axmatrix.matshow( distMat, aspect = 'auto', origin = 'lower' )
  axmatrix.set_xticks( [] )
  axmatrix.set_yticks( [] )

  # Plot colorbar.
  axcolor = fig.add_axes( [ 0.91, 0.1, 0.02, 0.8 ] )
  pylab.colorbar( im, cax = axcolor )

  # Save figure.
  fig.savefig( str(self.directory) + '/dendrogram.png')