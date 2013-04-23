# -*- coding: utf-8 -*-
from brainvisa.processes import *

def validation():
  try:
    import roca
  except:
    raise ValidationError( 'module roca is not here.' )


name = '04 - Regroup Fibers From Length'
userLevel = 2

signature = Signature(
    'gyrus_tracts_MeshClosestPoint', ReadDiskItem( 'Gyrus Tracts Mesh Closest Point', 'Aims bundles' ),
  'gyrus_tracts_MeshIntersectPoint', ReadDiskItem( 'Gyrus Tracts Mesh Intersect Point', 'Aims bundles' ),
  
         'fiberlength_MeshClosestPoint', WriteDiskItem( 'List of Fibers Length Mesh Closest Point', 'Text file' ),
       'fiberlength_MeshIntersectPoint', WriteDiskItem( 'List of Fibers Length Mesh Intersect Point', 'Text file' ),
    'tracts_by_length_MeshClosestPoint', WriteDiskItem( 'Gyrus Regrouped By Length Tracts Mesh Closest Point', 'Aims bundles' ),
  'tracts_by_length_MeshIntersectPoint', WriteDiskItem( 'Gyrus Regrouped By Length Tracts Mesh Intersect Point', 'Aims bundles' ),
     'tracts_5percent_MeshClosestPoint', WriteDiskItem( 'Gyrus Tracts Mesh Closest Point 5%', 'Aims bundles' ),
   'tracts_5percent_MeshIntersectPoint', WriteDiskItem( 'Gyrus Tracts Mesh Intersect Point 5%', 'Aims bundles' ),
  )
  
def initialization ( self ):
  self.linkParameters( 'gyrus_tracts_MeshIntersectPoint', 'gyrus_tracts_MeshClosestPoint' )
  self.linkParameters( 'fiberlength_MeshClosestPoint', 'gyrus_tracts_MeshClosestPoint' )
  self.linkParameters( 'fiberlength_MeshIntersectPoint', 'gyrus_tracts_MeshIntersectPoint' )
  self.linkParameters( 'tracts_by_length_MeshClosestPoint', 'gyrus_tracts_MeshClosestPoint' )
  self.linkParameters( 'tracts_by_length_MeshIntersectPoint', 'gyrus_tracts_MeshIntersectPoint' )
  self.linkParameters( 'tracts_5percent_MeshClosestPoint', 'tracts_by_length_MeshClosestPoint' )
  self.linkParameters( 'tracts_5percent_MeshIntersectPoint', 'tracts_by_length_MeshIntersectPoint' )

def execution ( self, context ):
  context.write( 'For a given cortex region, regroup fibers from length...' )
  
  context.system( 'constelFibersLengths',
    '-i', self.gyrus_tracts_MeshClosestPoint,
    '-o', self.fiberlength_MeshClosestPoint
  )
  
  context.system( 'constelFibersLengths',
    '-i', self.gyrus_tracts_MeshIntersectPoint,
    '-o', self.fiberlength_MeshIntersectPoint
  )
  
  context.system( 'comistBundleRegroup',
    '-i', self.gyrus_tracts_MeshClosestPoint,
    '-o', self.tracts_by_length_MeshClosestPoint,
    '-file', self.fiberlength_MeshClosestPoint
  )
  
  context.system( 'comistBundleRegroup',
    '-i', self.gyrus_tracts_MeshIntersectPoint,
    '-o', self.tracts_by_length_MeshIntersectPoint,
    '-file', self.fiberlength_MeshIntersectPoint
  )

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # This is just for viewing purposes. Fibers are filtered (5%) #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  context.system( 'comistBundleSampler',
    '-i', self.tracts_by_length_MeshClosestPoint,
    '-o', self.tracts_5percent_MeshClosestPoint,
    '-percent', 5,
    '-mode', 1
  ) 
  context.system( 'comistBundleSampler',
    '-i', self.tracts_by_length_MeshIntersectPoint,
    '-o', self.tracts_5percent_MeshIntersectPoint,
    '-percent', 5,
    '-mode', 1
  )
  context.write( 'OK' )
