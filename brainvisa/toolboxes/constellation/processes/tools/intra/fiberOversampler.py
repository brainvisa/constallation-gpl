# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path

def validation():
  if not find_in_path( 'comistFiberOversampler' ):
    raise ValidationError( 'connectomist module is not here.' )

name = 'Fiber Oversampler'
userLevel = 2

signature = Signature(
  'filtered_length_distant_fibers', ReadDiskItem( 
                                     'Very OutSide Fibers Of Cortex', 
                                     'Aims bundles' 
                                   ),
  'oversampled_distant_fibers', WriteDiskItem( 'Oversampled Fibers', 
                                              'Aims bundles' ),
)

def initialization( self ):
  self.linkParameters( 'oversampled_distant_fibers', 'filtered_length_distant_fibers' )

def execution ( self, context ):
  context.system( 'comistFiberOversampler',
    '-i', self.filtered_length_distant_fibers,
    '-o', self.oversampled_distant_fibers,
    '-points', 3,
    '-verbose', 1
  )
