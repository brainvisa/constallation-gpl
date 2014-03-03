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
from soma import aims
import numpy as np
import pylab
import itertools

import constel.lib.misctools as clm
import constel.lib.clustering.clusterstools as clcc
import constel.lib.measuringtools as cls

name = 'Scores'
userLevel = 2

signature = Signature(
  'clustering_1', ReadDiskItem( 'Group Clustering Time', 'BrainVISA texture formats' ),
  'clustering_2', ReadDiskItem( 'Group Clustering Time', 'BrainVISA texture formats' ),
  'time_step', Integer(),
  'directory', ReadDiskItem( 'Directory', 'Directory' )
)

def initialization ( self ):
  pass

def execution ( self, context ):
  clus1 = str( self.clustering_1.fullPath() )
  clus2 = str( self.clustering_2.fullPath() )
  
  c1 = aims.read( clus1 )
  c2 = aims.read( clus2 )
  
  labels1 = c1[ self.time_step ].arraydata()
  labels2 = c2[ self.time_step ].arraydata()
  
  list1, list2 = clm.sameNbElements( labels1, labels2 )
  
  entropy1 = clcc.entropy( list1 )
  entropy2 = clcc.entropy( list2 )

  mi = cls.mutual_information( list1, list2 )
  ri = cls.rand_index( list1, list2 )
  
  homogeneity = mi / ( entropy1 )
  completeness = mi / ( entropy2 )
  
  if homogeneity + completeness == 0.0:
    v_measure = 0.0
  else:
    v_measure = ( 2.0 * homogeneity * completeness
                           / (homogeneity + completeness))
  
  group1 = os.path.basename( os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( self.clustering_1.fullPath() ) ) ) ) ) ) ) )
  group2 = os.path.basename( os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( self.clustering_2.fullPath() ) ) ) ) ) ) ) )
  gyrus = os.path.basename( os.path.dirname( os.path.dirname( os.path.dirname( self.clustering_1.fullPath() ) ) ) )
  scoreFile = str(self.directory.fullPath() ) + '/' + str(group1) + '_' + str(group2) + '_step' + str(self.time_step) + '_'+ str(gyrus) + '_' + 'scoreFile.txt'
  
  fileR = open( scoreFile, 'w')
  fileR.write( 'Clustering 1 -----> ' + clus1 + '\n')
  fileR.write( '\n' )
  fileR.write( 'Clustering 2 -----> ' + clus2 + '\n')
  fileR.write( '\n' )
  lineEntropy1 = ''
  lineEntropy2 = ''
  lineRI = ''
  lineMI = ''
  lineHomogeneity = ''
  lineCompleteness = ''
  lineVmeasure = ''
  
  lineEntropy1 = lineEntropy1 + str(entropy1) + ' '
  lineEntropy2 = lineEntropy2 + str(entropy2) + ' '
  lineRI = lineRI + str(ri) + ' '
  lineMI = lineMI + str(mi) + ' '
  lineHomogeneity = lineHomogeneity + str(homogeneity) + ' '
  lineCompleteness = lineCompleteness + str(completeness) + ' '
  lineVmeasure = lineVmeasure + str(v_measure) + ' '
  
  fileR.write( '-----> entropy (clustering 1)   : ' + lineEntropy1 + '\n' )
  fileR.write( '\n' )
  fileR.write( '-----> entropy (clustering 2)   : ' + lineEntropy2 + '\n' )
  fileR.write( '\n' )
  fileR.write( '-----> rand index               : ' + lineRI + '\n' )
  fileR.write( '\n' )
  fileR.write( '-----> mutual information       : ' + lineMI + '\n' )
  fileR.write( '\n' )
  fileR.write( '-----> homogeneity              : ' + lineHomogeneity + '\n' )
  fileR.write( '\n' )
  fileR.write( '-----> completeness             : ' + lineCompleteness + '\n' )
  fileR.write( '\n' )
  fileR.write( '-----> v_measure                : ' + lineVmeasure + '\n' )

  fileR.close()
    
  
  
  
  
