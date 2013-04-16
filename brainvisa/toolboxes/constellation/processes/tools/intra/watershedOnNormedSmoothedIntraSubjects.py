# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma import aims
import pylab
import roca.lib.textureTools as TT


name = '12 - Mesh Watershed Processing'
userLevel = 2

signature = Signature(
  'norm_mean_connectivity_profile', ReadDiskItem( 'Normed Connectivity Profile', 'Aims texture formats' ),
                      'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
  
  'watershed', WriteDiskItem( 'Watershed', 'Aims texture formats' ),
)

def initialization ( self ):
  self.linkParameters( 'white_mesh', 'norm_mean_connectivity_profile' )
  self.linkParameters( 'watershed', 'norm_mean_connectivity_profile' )

def execution ( self, context ):
  context.write( 'A watershed is performed to obtain different patches of interest. These patches correspond to cortex sites with a strong connection to the gyrus.' )
  commandMeshWatershedProcessing = [ 'MeshWatershedProcessing.py',
    '-i', self.norm_mean_connectivity_profile,
    '-m', self.white_mesh,
    '--group', 'value',
    '--ksize', 10,
    '--kdepth', 0.05, 
    '--mode', 'and', 
    '--threshold', 0.05,
    '-o', self.watershed
  ]
  context.system( *commandMeshWatershedProcessing )
  context.write( 'OK' )

