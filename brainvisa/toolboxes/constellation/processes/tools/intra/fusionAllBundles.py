# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path

def validation():
  if not find_in_path( 'comistBundlesFusion_old' ):
    raise ValidationError( 'connectomist module is not here.' )


name = 'Fusion All Bundles'
userLevel = 2

signature = Signature(
    'gyrus_subsets_of_tracts_MeshClosestPoint', ListOf( ReadDiskItem( 'Gyrus Subset of Tracts Mesh Closest Point', 'Aims bundles' ) ),
  'gyrus_subsets_of_tracts_MeshIntersectPoint', ListOf( ReadDiskItem( 'Gyrus Subset of Tracts Mesh Intersect Point', 'Aims bundles' ) ),
  
     'gyrus_tracts_MeshClosestPoint', WriteDiskItem( 'Gyrus Tracts Mesh Closest Point', 'Aims bundles' ),
  'gyrus_tracts_MeshIntersectPoint',  WriteDiskItem( 'Gyrus Tracts Mesh Intersect Point', 'Aims bundles' ),
)

def initialization( self ):
  def tri( self, dummy ):
    if len( self.gyrus_subsets_of_tracts_MeshClosestPoint ) >= 1:
      len( self.gyrus_subsets_of_tracts_MeshClosestPoint ).sort()
  def linkBundleParam( self, dummy ):
    if len( self.gyrus_subsets_of_tracts_MeshClosestPoint ) >= 1:
      return self.signature[ 'gyrus_tracts_MeshClosestPoint' ].findValue( self.gyrus_subsets_of_tracts_MeshClosestPoint[0] )
  def linkBundleParam2( self, dummy ):
    if len( self.gyrus_subsets_of_tracts_MeshIntersectPoint ) >= 1:
      return self.signature[ 'gyrus_tracts_MeshIntersectPoint' ].findValue( self.gyrus_subsets_of_tracts_MeshIntersectPoint[0] )
  self.linkParameters( 'gyrus_subsets_of_tracts_MeshIntersectPoint', 'gyrus_subsets_of_tracts_MeshClosestPoint' )
  self.linkParameters( 'gyrus_tracts_MeshClosestPoint', 'gyrus_subsets_of_tracts_MeshClosestPoint', linkBundleParam )
  self.linkParameters( 'gyrus_tracts_MeshIntersectPoint', 'gyrus_subsets_of_tracts_MeshClosestPoint', linkBundleParam2 )
  
def execution ( self, context ):
  context.write( 'Merging files into two general categories, according to their source (between two connected regions or one place in the brain)' )
  cmd_args = [ "-i" ]
  cmd_args += self.gyrus_subsets_of_tracts_MeshClosestPoint #listeNearCortex
  cmd_args += [ "-o", self.gyrus_tracts_MeshClosestPoint ]
  
  context.system( "comistBundlesFusion_old", *cmd_args )
  
  cmd_args2 = [ "-i" ]
  cmd_args2 += self.gyrus_subsets_of_tracts_MeshIntersectPoint #listeNotMesh
  cmd_args2 += [ "-o", self.gyrus_tracts_MeshIntersectPoint]
  context.system( "comistBundlesFusion_old", *cmd_args2 )

  context.write( 'OK' )


