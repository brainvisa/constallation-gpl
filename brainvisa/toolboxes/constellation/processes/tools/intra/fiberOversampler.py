# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path

def validation():
  if not find_in_path( 'comistFiberOversampler' ):
    raise ValidationError( 'connectomist module is not here.' )

name = 'Fiber Oversampler'
userLevel = 2

signature = Signature(
  'length_filtered_tracts_distantFibers', ReadDiskItem( 'Gyrus Length Interval Tracts Distant Fibers', 'Aims bundles' ),
      'oversampled_tracts_distantFibers', WriteDiskItem( 'Gyrus Oversampled Length Interval Tracts Distant Fibers', 'Aims bundles' ),
)

def initialization( self ):
  self.linkParameters( 'oversampled_tracts_distantFibers', 'length_filtered_tracts_distantFibers' )

def execution ( self, context ):
  context.write( 'Gyrus tracts Oversampling.' )
  context.system( 'comistFiberOversampler',
    '-i', self.length_filtered_tracts_distantFibers,
    '-o', self.oversampled_tracts_distantFibers,
    '-points', 3,
    '-verbose', 1
  )
  context.write( 'OK' )
