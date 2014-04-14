from brainvisa.processes import *
from soma.path import find_in_path
import constel.lib.plot as p
import numpy as np
import pylab

name = 'Validity Indexes'
userLevel = 2

signature = Signature(
  'matrix', ReadDiskItem( 'Group Matrix', 'GIS image' ),
  'kmax', Integer(),
  'nbIter', Integer(),
  'indexFile', WriteDiskItem('Text File', ['Text File', 'CSV file'] ),
)

class MatplotlibFig( object ):
  def __init__( self, fig ):
    self._fig = fig
  def __del__( self ):
    mainThreadActions().call( pylab.close, self._fig )
    
def initialization ( self ):
  self.kmax = 12
  self.nbIter = 100
  self.indexFile = '/tmp/validityindexes.txt'

def execution ( self, context ):
  context.system( 'python', find_in_path( 'constelGettingValidityIndexes.py' ),
    '-m', self.matrix,
    '-n', self.nbIter,
    '-k', self.kmax,
    '-f', self.indexFile
  )
  context.write( 'OK' )
  
  fileR = open(self.indexFile, 'w')
  
  
  
  fileR.close()
  
  fig = mainThreadActions().call( p.validity_indexes_plot, sDB, sDunn, sCH, SFA, SFG, SFMed)
  return MatplotlibFig( fig )