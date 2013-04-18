# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma import aims
import pylab

def validation():
  try:
    import roca
  except:
    raise ValidationError( 'module roca is not here.' )


name = '09 - Mean Connectivity Profile From Matrix'
userLevel = 2

signature = Signature(
  'connectivity_matrix_full', ReadDiskItem( 'Gyrus Connectivity Matrix', 'Matrix sparse' ),
         'gyri_segmentation', ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ),
               'patch_label', Integer(),
               
                     'vertex_index', WriteDiskItem( 'Vertex Index', 'Text file' ),
  'gyrus_mean_connectivity_profile', WriteDiskItem( 'Gyrus Connectivity Profile', 'Aims texture formats' ),
)

def initialization ( self ):
  self.setOptional( 'patch_label' )
  self.linkParameters( 'vertex_index','connectivity_matrix_full' )
  self.linkParameters( 'gyrus_mean_connectivity_profile', 'connectivity_matrix_full' )

def execution ( self, context ):
  context.write( 'The mean connectivity profile over this region is represented as a texture on the cortex.' )
  if self.patch_label is not None:
    patch_label = self.patch_label
  else:
    patch_label = os.path.basename( os.path.dirname( os.path.dirname( self.connectivity_matrix_full.fullPath() ) ) )
    patch_label = patch_label.strip('G')
  context.write('patch_label = ', patch_label, '    Is it correct?')
  context.system( 'constelMeanConnectivityProfileFromMatrix',
    '-connfmt', 'binar_sparse',
    '-connmatrixfile', self.connectivity_matrix_full,
    '-outconntex', self.gyrus_mean_connectivity_profile, 
    '-seedregionstex', self.gyri_segmentation,
    '-seedlabel', patch_label,
    '-outseedvertex', self.vertex_index,
    '-verbose', 1,
    '-type', 'seed_mean_connectivity_profile',
    '-normalize', 0
  )
  #dest = os.path.dirname( self.vertex_index.fullPath() )
  #dest = dest + '/VertexIndex.txt.txt'
  #context.write( dest )
  #os.rename( str(dest), self.vertex_index.fullPath() )
  