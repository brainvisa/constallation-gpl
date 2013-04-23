# -*- coding: utf-8 -*-
from brainvisa.processes import *

def validation():
  try:
    import roca
  except:
    raise ValidationError( 'module roca is not here.' )

name = '07 - Connectivity Matrix'
userLevel = 2

signature = Signature(
    'oversampled_tracts_MeshIntersectPoint', ReadDiskItem( 'Gyrus Oversampled Length Interval Tracts Mesh Intersect Point', 'Aims bundles' ),
  'length_filtered_tracts_MeshClosestPoint', ReadDiskItem( 'Gyrus Length Interval Tracts Mesh Closest Point', 'Aims bundles' ),
                        'gyri_segmentation', ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ),
                               'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
                   'diff_to_anat_transform', ReadDiskItem( 'Transformation matrix', 'Transformation matrix' ),
                              'patch_label', Integer(),
  
   'connectivity_matrix_MeshIntersectPoint', WriteDiskItem( 'Gyrus Connectivity Matrix Mesh Intersect Point', 'Matrix sparse' ),
     'connectivity_matrix_MeshClosestPoint', WriteDiskItem( 'Gyrus Connectivity Matrix Mesh Closest Point', 'Matrix sparse' ),
    'connectivity_profile_MeshClosestPoint', WriteDiskItem( 'Gyrus Connectivity Profile Mesh Closest Point', 'Aims texture formats' ),
  'connectivity_profile_MeshIntersectPoint', WriteDiskItem( 'Gyrus Connectivity Profile Mesh Intersect Point', 'Aims texture formats' ),
)

def initialization( self ):
  self.setOptional( 'patch_label' )
  self.linkParameters( 'length_filtered_tracts_MeshClosestPoint', 'oversampled_tracts_MeshIntersectPoint' )
  self.linkParameters( 'connectivity_matrix_MeshIntersectPoint', 'oversampled_tracts_MeshIntersectPoint')
  self.linkParameters( 'connectivity_matrix_MeshClosestPoint', 'connectivity_matrix_MeshIntersectPoint' )
  self.linkParameters( 'connectivity_profile_MeshIntersectPoint', 'oversampled_tracts_MeshIntersectPoint')
  self.linkParameters( 'connectivity_profile_MeshClosestPoint', 'connectivity_profile_MeshIntersectPoint' )
  self.linkParameters( 'gyri_segmentation', 'white_mesh' )

def execution ( self, context ):
  context.write( 'Connections between a given vertice and all the vertices of the cortex. Connectivity matrix is smoothed over the surface to account for a reasonable uncertainty on the tractography.' )
  if self.patch_label is not None:
    patch_label = self.patch_label
  else:
    patch_label = os.path.basename( os.path.dirname( os.path.dirname( self.oversampled_tracts_MeshIntersectPoint.fullPath() ) ) )
    patch_label = patch_label.strip('G')
  context.write('patch_label = ', patch_label, '    Is it correct?')
  context.system( 'constelConnectivityMatrix',
    '-bundles', self.oversampled_tracts_MeshIntersectPoint,
    '-connmatrix', self.connectivity_matrix_MeshIntersectPoint,
    '-vertexindextype', 'both',
    '-seedvertexindex', 'VertexIndex',
    '-connfmt', 'binar_sparse',
    '-matrixcompute', 'meshintersectionpoint', 
    '-dist', 0.0,
    '-wthresh', 0.001,
    '-distmax', 5.0,
    '-seedregionstex', self.gyri_segmentation, 
    '-outconntex', self.connectivity_profile_MeshIntersectPoint,
    '-mesh',self. white_mesh,
    '-type', 'seed_mean_connectivity_profile',
    '-trs', self.diff_to_anat_transform,
    '-seedlabel', patch_label,
    '-normalize', 0,
    '-verbose', 1
  )
  
  context.system( 'constelConnectivityMatrix',
    '-bundles', self.length_filtered_tracts_MeshClosestPoint,    
    '-connmatrix', self.connectivity_matrix_MeshClosestPoint,
    '-vertexindextype', 'both',
    '-seedvertexindex', 'VertexIndex',
    '-connfmt', 'binar_sparse',
    '-matrixcompute', 'meshclosestpoint', 
    '-dist', 0.0,
    '-wthresh', 0.001,
    '-distmax', 5.0,
    '-seedregionstex', self.gyri_segmentation, 
    '-outconntex', self.connectivity_profile_MeshClosestPoint,
    '-mesh',self. white_mesh,
    '-type', 'seed_mean_connectivity_profile',
    '-trs', self.diff_to_anat_transform,
    '-seedlabel', patch_label,
    '-normalize', 0,
    '-verbose', 1
  )
  context.write( 'OK' )
