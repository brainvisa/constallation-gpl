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
         'oversampled_tracts_distantFibers', ReadDiskItem( 'Oversampled Fibers', 'Aims bundles' ),
  'length_filtered_tracts_fibersNearCortex', ReadDiskItem( 'Fibers Near Cortex', 'Aims bundles' ),
                             'gyri_texture', ReadDiskItem( 'FreesurferResampledBothParcellationType', 'Aims texture formats' ),
                               'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
                                 'dw_to_t1', ReadDiskItem( 'Transformation matrix', 'Transformation matrix' ),
                                    'gyrus', Integer(),
  
      'connectivity_matrix_distantFibers', WriteDiskItem( 'Connectivity Matrix Outside Fibers Of Cortex', 'Matrix sparse' ),
   'connectivity_matrix_fibersNearCortex', WriteDiskItem( 'Connectivity Matrix Fibers Near Cortex', 'Matrix sparse' ),
  'connectivity_profile_fibersNearCortex', WriteDiskItem( 'Connectivity Profile Fibers Near Cortex', 'Aims texture formats' ),
     'connectivity_profile_distantFibers', WriteDiskItem( 'Connectivity Profile Outside Fibers Of Cortex', 'Aims texture formats' ),
)

def initialization( self ):
  self.setOptional( 'gyrus' )
  self.linkParameters( 'length_filtered_tracts_fibersNearCortex', 'oversampled_tracts_distantFibers' )
  self.linkParameters( 'connectivity_matrix_distantFibers', 'oversampled_tracts_distantFibers')
  self.linkParameters( 'connectivity_matrix_fibersNearCortex', 'connectivity_matrix_distantFibers' )
  self.linkParameters( 'connectivity_profile_distantFibers', 'oversampled_tracts_distantFibers')
  self.linkParameters( 'connectivity_profile_fibersNearCortex', 'connectivity_profile_distantFibers' )
  self.linkParameters( 'gyri_texture', 'white_mesh' )

def execution ( self, context ):
  context.write( 'Connections between a given vertice and all the vertices of the cortex. Connectivity matrix is smoothed over the surface to account for a reasonable uncertainty on the tractography.' )
  if self.gyrus is not None:
    gyrus = self.gyrus
  else:
    gyrus = os.path.basename( os.path.dirname( os.path.dirname( self.oversampled_tracts_distantFibers.fullPath() ) ) )
    gyrus = gyrus.strip('G')
  context.write('gyrus = ', gyrus, '    Is it correct?')
  context.system( 'constelConnectivityMatrix',
    '-bundles', self.oversampled_tracts_distantFibers,
    '-connmatrix', self.connectivity_matrix_distantFibers,
    '-vertexindextype', 'both',
    '-seedvertexindex', 'VertexIndex',
    '-connfmt', 'binar_sparse',
    '-matrixcompute', 'meshintersectionpoint', 
    '-dist', 0.0,
    '-wthresh', 0.001,
    '-distmax', 5.0,
    '-seedregionstex', self.gyri_texture,
    '-outconntex', self.connectivity_profile_distantFibers,
    '-mesh',self. white_mesh,
    '-type', 'seed_mean_connectivity_profile',
    '-trs', self.dw_to_t1,
    '-seedlabel', gyrus,
    '-normalize', 0,
    '-verbose', 1
  )
  
  context.system( 'constelConnectivityMatrix',
    '-bundles', self.length_filtered_tracts_fibersNearCortex,    
    '-connmatrix', self.connectivity_matrix_fibersNearCortex,
    '-vertexindextype', 'both',
    '-seedvertexindex', 'VertexIndex',
    '-connfmt', 'binar_sparse',
    '-matrixcompute', 'meshclosestpoint', 
    '-dist', 0.0,
    '-wthresh', 0.001,
    '-distmax', 5.0,
    '-seedregionstex', self.gyri_texture,
    '-outconntex', self.connectivity_profile_fibersNearCortex,
    '-mesh',self. white_mesh,
    '-type', 'seed_mean_connectivity_profile',
    '-trs', self.dw_to_t1,
    '-seedlabel', gyrus,
    '-normalize', 0,
    '-verbose', 1
  )
  context.write( 'OK' )
