# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma import aims
from soma.path import find_in_path

def validation():
  if not find_in_path( 'AimsMeshWatershed.py' ):
    raise ValidationError( 'aims module is not here.' )


name = '12 - Watershed'
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
  commandMeshWatershedProcessing = [ sys.executable,
    find_in_path( 'AimsMeshWatershed.py' ),
    '-i', self.norm_mean_connectivity_profile,
    '-m', self.white_mesh,
    '-k', 10,
    '-q', 0.05,
    '-z', 'or',
    '-t', 0.05,
    '-o', self.watershed
  ]
  context.system( *commandMeshWatershedProcessing )
  context.write( 'OK' )

