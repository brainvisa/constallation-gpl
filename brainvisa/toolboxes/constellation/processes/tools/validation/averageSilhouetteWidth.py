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
import constel.lib.clustervalidity as cv
import constel.lib.plot as p
import numpy as np
import pylab

name = 'Average Silhouette Width'
userLevel = 2

signature = Signature(
  'connectivity_matrix_reduced', ReadDiskItem( 'Reduced Connectivity Matrix', 'GIS image' ),
  'kmax', Integer(),
)

class MatplotlibFig( object ):
  def __init__( self, fig ):
    self._fig = fig
  def __del__( self ):
    mainThreadActions().call( pylab.close, self._fig )

def initialization ( self ):
  self.kmax = 10

def execution ( self, context ):
  reduced_matrix = aims.read(self.connectivity_matrix_reduced.fullPath())
  reduced_matrix = np.transpose(np.asarray(reduced_matrix)[:,:,0,0])
  asw = []
  for k in range(2, self.kmax+1):
    s = cv.silhouette_score(reduced_matrix, k)
    context.write('ASW is ', s, 'for K =', k ) 
    asw.append(s)
  aswOpt = max(asw)
  context.write('The larger ASW is', aswOpt)
  list_k = range(self.kmax+1)
  list_k = [x for x in list_k if x!=0 and x!=1]
  fig = mainThreadActions().call( p.silhouette_score_plot, asw, list_k )
  return MatplotlibFig( fig )
