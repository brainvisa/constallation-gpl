# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path

def validation():
  if not find_in_path( 'comistFiberOversampler' ):
    raise ValidationError( 'connectomist module is not here.' )

name = 'Fiber Oversampler'
userLevel = 2

signature = Signature(
  'filtered_length_remote_Fibers', ReadDiskItem( 
                                     'Very OutSide Fibers Of Cortex', 
                                     'Aims bundles' 
                                   ),
  'oversampled_remote_Fibers', WriteDiskItem( 'Oversampled Fibers', 
                                              'Aims bundles' ),
)

def initialization( self ):
  self.linkParameters( 'oversampled_remote_Fibers', 'filtered_length_remote_Fibers' )

def execution ( self, context ):
  context.system( 'comistFiberOversampler',
    '-i', self.filtered_length_remote_Fibers,
    '-o', self.oversampled_remote_Fibers,
    '-points', 3,
    '-verbose', 1
  )
