# -*- coding: utf-8 -*-
from brainvisa.processes import *
import numpy as np

def validation():
  try:
    import roca
  except:
    raise ValidationError( 'module roca is not here.' )


name = '05 - Select Fibers From Length'
userLevel = 2

signature = Signature(
    'tracts_by_length_MeshClosestPoint', ReadDiskItem( 'Gyrus Regrouped By Length Tracts Mesh Closest Point', 'Aims bundles' ),
  'tracts_by_length_MeshIntersectPoint', ReadDiskItem( 'Gyrus Regrouped By Length Tracts Mesh Intersect Point', 'Aims bundles' ),
  
    'length_filtered_tracts_MeshClosestPoint', WriteDiskItem( 'Gyrus Length Interval Tracts Mesh Closest Point', 'Aims bundles' ),
  'length_filtered_tracts_MeshIntersectPoint', WriteDiskItem( 'Gyrus Length Interval Tracts Mesh Intersect Point', 'Aims bundles' ),
          'tracts_20percent_MeshClosestPoint', WriteDiskItem( 'Gyrus Length Interval Tracts Mesh Closest Point 20%', 'Aims bundles' ),
        'tracts_20percent_MeshIntersectPoint', WriteDiskItem( 'Gyrus Length Interval Tracts Mesh Intersect Point 20%', 'Aims bundles' ),
)
  
def initialization ( self ):
  self.linkParameters( 'tracts_by_length_MeshIntersectPoint', 'tracts_by_length_MeshClosestPoint' )
  self.linkParameters( 'length_filtered_tracts_MeshClosestPoint', 'tracts_by_length_MeshClosestPoint' )
  self.linkParameters( 'length_filtered_tracts_MeshIntersectPoint', 'tracts_by_length_MeshIntersectPoint' )
  self.linkParameters( 'tracts_20percent_MeshClosestPoint','tracts_by_length_MeshClosestPoint' )
  self.linkParameters( 'tracts_20percent_MeshIntersectPoint', 'tracts_by_length_MeshIntersectPoint' )

def execution ( self, context ):
  context.write( 'For a given cortex region, select fibers from length...' )
  length_min_MeshClosestPoint = 60
  length_min_MeshIntersectPoint = 20
  length_max = 500  
  context.system( 'constelSelectBundlesFromNames',
    '-i', self.tracts_by_length_MeshClosestPoint,
    '-o', self.length_filtered_tracts_MeshClosestPoint,
    '-names', *[ str(x) for x in xrange( length_min_MeshClosestPoint, length_max + 1 ) ]
  )
  
  context.system( 'constelSelectBundlesFromNames',
    '-i', self.tracts_by_length_MeshIntersectPoint,
    '-o', self.length_filtered_tracts_MeshIntersectPoint,
    '-names', *[ str(x) for x in xrange( length_min_MeshIntersectPoint, length_max + 1 ) ]
  )

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # This is just for viewing purposes. Fibers are filtered (20%)#
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  context.system( 'comistBundleSampler',
    '-i', self.length_filtered_tracts_MeshClosestPoint,
    '-o', self.tracts_20percent_MeshClosestPoint,
    '-percent', 20,
    '-mode', 1
  )
  
  context.system( 'comistBundleSampler',
    '-i', self.length_filtered_tracts_MeshIntersectPoint,
    '-o', self.tracts_20percent_MeshIntersectPoint,
    '-percent', 20,
    '-mode', 1
  )
  context.write( 'OK' )
  
