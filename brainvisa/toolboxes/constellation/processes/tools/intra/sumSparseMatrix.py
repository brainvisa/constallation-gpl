# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path

def validation():
  if not find_in_path( 'AimsSumSparseMatrix' ) \
      or not find_in_path( 'AimsSparseMatrixSmoothing' ):
    raise ValidationError( 'aims module is not here.' )

name = 'Sum Sparse Matrix Smoothing'
userLevel = 2

signature = Signature(
  'connectivity_matrix_fibersNearCortex', ReadDiskItem( 'Connectivity Matrix Fibers Near Cortex', 'Matrix sparse' ),
     'connectivity_matrix_distantFibers', ReadDiskItem( 'Connectivity Matrix Outside Fibers Of Cortex', 'Matrix sparse' ),
                          'gyri_texture', ReadDiskItem( 'FreesurferResampledBothParcellationType', 'Aims texture formats' ),
                            'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
                             'smoothing', Float(),
                                 'gyrus', Integer(),
  
  'connectivity_matrix_full', WriteDiskItem( 'Gyrus Connectivity Matrix', 'Matrix sparse' ),
)

def initialization( self ):
  def linkSmooth(self, dummy):
    if self.connectivity_matrix_distantFibers is not None:
      attrs = dict( self.connectivity_matrix_distantFibers.hierarchyAttributes() )
      attrs['subject'] =  self.connectivity_matrix_distantFibers.get('subject')
      attrs['study'] = self.connectivity_matrix_distantFibers.get('study')
      attrs['texture'] = self.connectivity_matrix_distantFibers.get('texture')
      attrs['gyrus'] = self.connectivity_matrix_distantFibers.get('gyrus')
      attrs['smooth'] = str( self.smoothing )
      filename = self.signature['connectivity_matrix_full'].findValue( attrs )
      return filename
  self.setOptional( 'gyrus' )
  self.linkParameters( 'connectivity_matrix_distantFibers', 'connectivity_matrix_fibersNearCortex' )
  self.linkParameters( 'connectivity_matrix_full', ( 'connectivity_matrix_distantFibers', 'smoothing'), linkSmooth )

def execution ( self, context ):
  context.write( 'Sum sparse matrix (categories : between two connected regions or one place in the brain).' )
  if self.gyrus is not None:
    gyrus = self.gyrus
  else:
    gyrus = os.path.basename( os.path.dirname( os.path.dirname( self.connectivity_matrix_fibersNearCortex.fullPath() ) ) )
    gyrus = gyrus.strip('G')
  context.write('gyrus = ', gyrus, '    Is it correct?')
  context.system( 'AimsSumSparseMatrix',
    '-i', self.connectivity_matrix_distantFibers,
    '-i', self.connectivity_matrix_fibersNearCortex,
    '-o', self.connectivity_matrix_full
  )

  context.system( 'AimsSparseMatrixSmoothing',
    '-i', self.connectivity_matrix_full,
    '-m', self.white_mesh,
    '-o', self.connectivity_matrix_full,
    '-s', self.smoothing,
    '-l', self.gyri_texture,
    '-p', self.gyrus,
  )
  
  context.write( 'OK' )

  
