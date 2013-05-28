# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path

def validation():
  if not find_in_path( 'AimsSumSparseMatrix' ) \
      or not find_in_path( 'AimsSparseMatrixSmoothing' ):
    raise ValidationError( 'aims module is not here.' )

name = '08 - Sum Sparse Matrix Smoothing'
userLevel = 2

signature = Signature(
    'connectivity_matrix_MeshClosestPoint', ReadDiskItem( 'Gyrus Connectivity Matrix Mesh Closest Point', 'Matrix sparse' ),
  'connectivity_matrix_MeshIntersectPoint', ReadDiskItem( 'Gyrus Connectivity Matrix Mesh Intersect Point', 'Matrix sparse' ),
                       'gyri_segmentation', ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ),
                              'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
                                  'smooth', Float(),
                             'patch_label', Integer(),
  
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
    '-s', self.smooth,
    '-l', self.gyri_segmentation,
    '-p', self.patch_label,
  )
  
  context.write( 'OK' )

  
