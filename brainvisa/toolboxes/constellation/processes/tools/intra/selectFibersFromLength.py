# -*- coding: utf-8 -*-
from brainvisa.processes import *
import numpy as np

def validation():
  try:
    import constel
  except:
    raise ValidationError( 'constellation module is not here.' )


name = '05 - Select Fibers From Length'
userLevel = 2

signature = Signature(
    'tracts_by_length_MeshClosestPoint', ReadDiskItem( 'Gyrus Regrouped By Length Tracts Mesh Closest Point', 'Aims bundles' ),
  'tracts_by_length_MeshIntersectPoint', ReadDiskItem( 'Gyrus Regrouped By Length Tracts Mesh Intersect Point', 'Aims bundles' ),
          'min_length_fibersNearCortex', Integer(),
             'min_length_distantFibers', Integer(),
  
    'length_filtered_tracts_MeshClosestPoint', WriteDiskItem( 'Gyrus Length Interval Tracts Mesh Closest Point', 'Aims bundles' ),
  'length_filtered_tracts_MeshIntersectPoint', WriteDiskItem( 'Gyrus Length Interval Tracts Mesh Intersect Point', 'Aims bundles' ),
          'tracts_20percent_MeshClosestPoint', WriteDiskItem( 'Gyrus Length Interval Tracts Mesh Closest Point 20%', 'Aims bundles' ),
        'tracts_20percent_MeshIntersectPoint', WriteDiskItem( 'Gyrus Length Interval Tracts Mesh Intersect Point 20%', 'Aims bundles' ),
)
  
def initialization ( self ):
  self.min_length_fibersNearCortex = 30
  self.min_length_distantFibers = 20
  def linkLengthIn( self, dummy ):
    if self.tracts_by_length_MeshClosestPoint is not None and self.min_length_fibersNearCortex is not None:
      attrs = dict( self.tracts_by_length_MeshClosestPoint.hierarchyAttributes() )
      attrs['minlengthoffibersIn'] = str( self.min_length_fibersNearCortex )
      x = self.signature['length_filtered_tracts_MeshClosestPoint'].findValue( attrs )
      return x
  def linkLengthOut( self, dummy ):
    if self.tracts_by_length_MeshIntersectPoint is not None and self.min_length_distantFibers is not None:
      attrs = dict( self.tracts_by_length_MeshIntersectPoint.hierarchyAttributes() )
      attrs['minlengthoffibersOut'] = str( self.min_length_distantFibers )
      x = self.signature['length_filtered_tracts_MeshIntersectPoint'].findValue( attrs )
      return x
  self.linkParameters( 'tracts_by_length_MeshIntersectPoint', 'tracts_by_length_MeshClosestPoint' )
  self.linkParameters( 'length_filtered_tracts_MeshClosestPoint', ( 'tracts_by_length_MeshClosestPoint', 'min_length_fibersNearCortex' ), linkLengthIn )
  self.linkParameters( 'length_filtered_tracts_MeshIntersectPoint', ( 'tracts_by_length_MeshIntersectPoint', 'min_length_distantFibers' ), linkLengthOut )
  self.linkParameters( 'tracts_20percent_MeshClosestPoint', ('length_filtered_tracts_MeshClosestPoint', 'min_length_fibersNearCortex' ) )
  self.linkParameters( 'tracts_20percent_MeshIntersectPoint', ( 'length_filtered_tracts_MeshIntersectPoint', 'min_length_distantFibers' ) )

def execution ( self, context ):
  context.write( 'For a given cortex region, select fibers from length...' )
  length_max = 500 # sufficient length
  context.system( 'constelSelectBundlesFromNames',
    '-i', self.tracts_by_length_MeshClosestPoint,
    '-o', self.length_filtered_tracts_MeshClosestPoint,
    '-names', *[ str(x) for x in xrange( self.min_length_fibersNearCortex, length_max + 1 ) ]
  )
  
  context.system( 'constelSelectBundlesFromNames',
    '-i', self.tracts_by_length_MeshIntersectPoint,
    '-o', self.length_filtered_tracts_MeshIntersectPoint,
    '-names', *[ str(x) for x in xrange( self.min_length_distantFibers, length_max + 1 ) ]
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
  
