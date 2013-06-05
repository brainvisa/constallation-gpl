# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path

def validation():
  if not find_in_path( 'AimsSparseMatrixToDense.py' ):
    raise ValidationError( 'aims module is not here.' )

name = 'Convert Sparse Matrix to Ima'
userLevel = 2

signature = Signature(
  'connectivity_matrix_full', ReadDiskItem( 'Gyrus Connectivity Matrix', 'Matrix sparse' ),
  'patch_connectivity_matrix', WriteDiskItem( 'Patch Connectivity Matrix', 'GIS image' ),
)

def initialization ( self ):
  self.linkParameters( 'patch_connectivity_matrix', 'connectivity_matrix_full' )

def execution ( self, context ):
  context.system( 'AimsSparseMatrixToDense.py',
    '-i', self.connectivity_matrix_full,
    '-o', self.patch_connectivity_matrix,
  )
  context.write( 'Convert sparse matrix to ima : OK' )
