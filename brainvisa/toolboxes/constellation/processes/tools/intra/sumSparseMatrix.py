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
  'matrix_of_fibers_near_cortex', ReadDiskItem( 
                               'Connectivity Matrix Fibers Near Cortex', 
                               'Matrix sparse' 
                             ),
  'matrix_of_distant_fibers', ReadDiskItem( 
                            'Connectivity Matrix Outside Fibers Of Cortex', 
                            'Matrix sparse' 
                          ),
  'gyri_texture', ReadDiskItem( 'FreesurferResampledBothParcellationType', 
                                'Aims texture formats' ),
  'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
  'smoothing', Float(),
  'gyrus', Integer(),
  'complete_connectivity_matrix', WriteDiskItem( 'Gyrus Connectivity Matrix', 
                                                 'Matrix sparse' ),
)

def initialization( self ):
  self.smoothing = 3.0
  self.setOptional( 'gyrus' )
  
  def linkSmooth(self, dummy):
    if self.matrix_of_distant_fibers is not None:
      attrs = dict( self.matrix_of_distant_fibers.hierarchyAttributes() )
      print 'attrs de matrix_of_distant_fibers --> ', attrs
      attrs['subject'] =  self.matrix_of_distant_fibers.get('subject')
      attrs['study'] = self.matrix_of_distant_fibers.get('study')
      attrs['texture'] = self.matrix_of_distant_fibers.get('texture')
      attrs['gyrus'] = self.matrix_of_distant_fibers.get('gyrus')
      attrs['smoothing'] = str( self.smoothing )
      filename = self.signature['complete_connectivity_matrix'].findValue( 
                                                                attrs )
      return filename
  
  self.linkParameters( 'matrix_of_distant_fibers', 'matrix_of_fibers_near_cortex' )
  self.linkParameters( 'complete_connectivity_matrix', 
                       ( 'matrix_of_distant_fibers', 'smoothing'), linkSmooth )

def execution ( self, context ):
  if self.gyrus is not None:
    gyrus = self.gyrus
  else:
    gyrus = os.path.basename( os.path.dirname( 
            os.path.dirname( self.matrix_of_fibers_near_cortex.fullPath() ) ) )
    gyrus = gyrus.strip('G')
  context.write('gyrus ', gyrus)
  context.system( 'AimsSumSparseMatrix',
    '-i', self.matrix_of_distant_fibers,
    '-i', self.matrix_of_fibers_near_cortex,
    '-o', self.complete_connectivity_matrix
  )

  context.system( 'AimsSparseMatrixSmoothing',
    '-i', self.complete_connectivity_matrix,
    '-m', self.white_mesh,
    '-o', self.complete_connectivity_matrix,
    '-s', self.smoothing,
    '-l', self.gyri_texture,
    '-p', gyrus,
  )

  
