# -*- coding: utf-8 -*-
from brainvisa.processes import *

def validation():
  try:
    import constel
  except:
    raise ValidationError( 'constellation module is not here.' )

name = 'Connectivity Matrix'
userLevel = 2

signature = Signature(
  'oversampled_distant_fibers', ReadDiskItem( 'Oversampled Fibers', 'Aims bundles' ),
  'filtered_length_fibers_near_cortex', ReadDiskItem( 'Fibers Near Cortex', 'Aims bundles' ),
  'gyri_texture', ReadDiskItem( 'FreesurferResampledBothParcellationType', 'Aims texture formats' ),
  'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
  'dw_to_t1', ReadDiskItem( 'Transformation matrix', 'Transformation matrix' ),
  'gyrus', Integer(),
  
  'matrix_of_distant_fibers', WriteDiskItem( 'Connectivity Matrix Outside Fibers Of Cortex', 'Matrix sparse' ),
  'matrix_of_fibers_near_cortex', WriteDiskItem( 'Connectivity Matrix Fibers Near Cortex', 'Matrix sparse' ),
  'profile_of_fibers_near_cortex', WriteDiskItem( 'Connectivity Profile Fibers Near Cortex', 'Aims texture formats' ),
  'profile_of_distant_fibers', WriteDiskItem( 'Connectivity Profile Outside Fibers Of Cortex', 'Aims texture formats' ),
)

def initialization( self ):
  self.setOptional( 'gyrus' )
  self.linkParameters( 'filtered_length_fibers_near_cortex', 'oversampled_distant_fibers' )
  self.linkParameters( 'matrix_of_distant_fibers', 'oversampled_distant_fibers')
  self.linkParameters( 'matrix_of_fibers_near_cortex', 'matrix_of_distant_fibers' )
  self.linkParameters( 'profile_of_distant_fibers', 'oversampled_distant_fibers')
  self.linkParameters( 'profile_of_fibers_near_cortex', 'profile_of_distant_fibers' )
  self.linkParameters( 'gyri_texture', 'white_mesh' )

def execution ( self, context ):
  context.write( 'Connections between a given vertice and all the vertices of the cortex. Connectivity matrix is smoothed over the surface to account for a reasonable uncertainty on the tractography.' )
  if self.gyrus is not None:
    gyrus = self.gyrus
  else:
    gyrus = os.path.basename( os.path.dirname( os.path.dirname( self.oversampled_distant_fibers.fullPath() ) ) )
    gyrus = gyrus.strip('G')
  context.write('gyrus = ', gyrus )
  context.system( 'constelConnectivityMatrix',
    '-bundles', self.oversampled_distant_fibers,
    '-connmatrix', self.matrix_of_distant_fibers,
    '-connfmt', 'binar_sparse',
    '-matrixcompute', 'meshintersectionpoint', 
    '-dist', 0.0,
    '-wthresh', 0.001,
    '-distmax', 5.0,
    '-seedregionstex', self.gyri_texture,
    '-outconntex', self.profile_of_distant_fibers,
    '-mesh',self. white_mesh,
    '-type', 'seed_mean_connectivity_profile',
    '-trs', self.dw_to_t1,
    '-seedlabel', gyrus,
    '-normalize', 0,
    '-verbose', 1
  )
  
  context.system( 'constelConnectivityMatrix',
    '-bundles', self.filtered_length_fibers_near_cortex,    
    '-connmatrix', self.matrix_of_fibers_near_cortex,
    '-connfmt', 'binar_sparse',
    '-matrixcompute', 'meshclosestpoint', 
    '-dist', 0.0,
    '-wthresh', 0.001,
    '-distmax', 5.0,
    '-seedregionstex', self.gyri_texture,
    '-outconntex', self.profile_of_fibers_near_cortex,
    '-mesh',self. white_mesh,
    '-type', 'seed_mean_connectivity_profile',
    '-trs', self.dw_to_t1,
    '-seedlabel', gyrus,
    '-normalize', 0,
    '-verbose', 1
  )
