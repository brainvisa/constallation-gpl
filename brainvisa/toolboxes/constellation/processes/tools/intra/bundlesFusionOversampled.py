# -*- coding: utf-8 -*-
from brainvisa.processes import *

name = '06 - Fiber Oversampler'
userLevel = 2

signature = Signature(
  'length_filtered_tracts_MeshIntersectPoint', ReadDiskItem( 'Gyrus Length Interval Tracts Mesh Intersect Point', 'Aims bundles' ),
  'oversampled_tracts_MeshIntersectPoint', WriteDiskItem( 'Gyrus Oversampled Length Interval Tracts Mesh Intersect Point', 'Aims bundles' ),
)

def initialization( self ):
  self.linkParameters( 'oversampled_tracts_MeshIntersectPoint', 'length_filtered_tracts_MeshIntersectPoint' )

def execution ( self, context ):
  context.write( 'Gyrus tracts Oversampling.' )
  context.system( 'testFiberOversampler',
    '-i', self.length_filtered_tracts_MeshIntersectPoint,
    '-o', self.oversampled_tracts_MeshIntersectPoint,
    '-points', 3,
    '-verbose', 1
  )
  context.write( 'OK' )