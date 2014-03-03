# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma import aims
from soma.path import find_in_path

def validation():
  if not find_in_path( 'AimsMeshWatershed.py' ):
    raise ValidationError( 'aims module is not here.' )

name = 'Watershed'
userLevel = 2

signature = Signature(
  'normed_connectivity_profile', ReadDiskItem( 'Normed Connectivity Profile', 
                                               'Aims texture formats' ),
  'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
  'watershed', WriteDiskItem( 'Watershed Texture', 'Aims texture formats' ),
)

def initialization ( self ):
  self.linkParameters( 'white_mesh', 'normed_connectivity_profile' )
  self.linkParameters( 'watershed', 'normed_connectivity_profile' )

def execution ( self, context ):
  commandMeshWatershedProcessing = [ sys.executable,
    find_in_path( 'AimsMeshWatershed.py' ),
    '-i', self.normed_connectivity_profile,
    '-m', self.white_mesh,
    '-k', 10,
    '-q', 0.05,
    '-z', 'or',
    '-t', 0.05,
    '-o', self.watershed
  ]
  context.system( *commandMeshWatershedProcessing )