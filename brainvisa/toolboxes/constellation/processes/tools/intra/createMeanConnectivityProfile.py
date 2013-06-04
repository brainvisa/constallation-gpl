# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path
from soma import aims

def validation():
  if not find_in_path( 'constelMeanConnectivityProfileFromMatrix' ):
    raise ValidationError( 'constellation module is not here.' )


name = 'Mean Connectivity Profile'
userLevel = 2

signature = Signature(
  'connectivity_matrix_full', ReadDiskItem( 'Gyrus Connectivity Matrix', 'Matrix sparse' ),
              'gyri_texture', ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ),
                     'gyrus', Integer(),
               
                'vertex_index', WriteDiskItem( 'Vertex Index', 'Text file' ),
  'gyrus_connectivity_profile', WriteDiskItem( 'Gyrus Connectivity Profile', 'Aims texture formats' ),
)

def initialization ( self ):
  self.setOptional( 'gyrus' )
  self.linkParameters( 'vertex_index','connectivity_matrix_full' )
  self.linkParameters( 'gyrus_connectivity_profile', 'connectivity_matrix_full' )

def execution ( self, context ):
  context.write( 'The mean connectivity profile over this region is represented as a texture on the cortex.' )
  if self.gyrus is not None:
    gyrus = self.gyrus
  else:
    gyrus = os.path.basename( os.path.dirname( os.path.dirname( self.connectivity_matrix_full.fullPath() ) ) )
    gyrus = gyrus.strip('G')
  context.write('gyrus = ', gyrus, '    Is it correct?')
  context.system( 'constelMeanConnectivityProfileFromMatrix',
    '-connfmt', 'binar_sparse',
    '-connmatrixfile', self.connectivity_matrix_full,
    '-outconntex', self.gyrus_connectivity_profile,
    '-seedregionstex', self.gyri_texture,
    '-seedlabel', gyrus,
    '-outseedvertex', self.vertex_index,
    '-verbose', 1,
    '-type', 'seed_mean_connectivity_profile',
    '-normalize', 0
  )
  #dest = os.path.dirname( self.vertex_index.fullPath() )
  #dest = dest + '/VertexIndex.txt.txt'
  #context.write( dest )
  #os.rename( str(dest), self.vertex_index.fullPath() )
  
