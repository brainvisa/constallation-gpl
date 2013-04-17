# -*- coding: utf-8 -*-
from brainvisa.processes import *

def validation():
  try:
    import roca
  except:
    raise ValidationError( 'module roca is not here.' )

name = '08 - Sum Sparse matrix'
userLevel = 2

signature = Signature(
    'connectivity_matrix_MeshClosestPoint', ReadDiskItem( 'Gyrus Connectivity Matrix Mesh Closest Point', 'Matrix sparse' ),
  'connectivity_matrix_MeshIntersectPoint', ReadDiskItem( 'Gyrus Connectivity Matrix Mesh Intersect Point', 'Matrix sparse' ),
                              'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
                                  'smooth', Float(),
  
  'connectivity_matrix_full', WriteDiskItem( 'Gyrus Connectivity Matrix', 'Matrix sparse' ),
)

def initialization( self ):
  self.linkParameters( 'connectivity_matrix_MeshIntersectPoint', 'connectivity_matrix_MeshClosestPoint' )
  self.linkParameters( 'connectivity_matrix_full', 'connectivity_matrix_MeshIntersectPoint' )

def execution ( self, context ):
  context.write( 'Sum sparse matrix (categories : between two connected regions or one place in the brain).' )
  context.system( 'AimsSumSparseMatrix',
    '-i', self.connectivity_matrix_MeshIntersectPoint,
    '-i', self.connectivity_matrix_MeshClosestPoint,
    '-o', self.connectivity_matrix_full
  )

  context.system( 'AimsSparseMatrixSmoothing',
    '-i', self.connectivity_matrix_full,
    '-m', self.white_mesh,
    '-o', self.connectivity_matrix_full,
    '-s', self.smooth
  )
  
  context.write( 'OK' )

  