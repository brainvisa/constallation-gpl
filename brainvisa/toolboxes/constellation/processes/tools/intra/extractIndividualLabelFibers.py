# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path

def validation():
  try:
    import roca
  except:
    raise ValidationError( 'module roca is not here.' )

name = '02 - Bundles Select For A LAbel'
userLevel = 2

signature = Signature(
  'reorganized_subsets_of_tracts', ReadDiskItem( 'Gyri Regrouped Subset of Tracts', 'Aims bundles' ),
              'gyri_segmentation', ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ),
                    'patch_label', Integer(),
  
    'gyrus_subsets_of_tracts_MeshClosestPoint', WriteDiskItem( 'Gyrus Subset of Tracts Mesh Closest Point', 'Aims bundles' ),
  'gyrus_subsets_of_tracts_MeshIntersectPoint', WriteDiskItem( 'Gyrus Subset of Tracts Mesh Intersect Point', 'Aims bundles' ),
  )

def initialization( self ):
  def linkTracts( self, dummy ):
    if self.reorganized_subsets_of_tracts is not None:
      attrs = dict( self.reorganized_subsets_of_tracts.hierarchyAttributes() )
      attrs['gyrus'] = 'G' + str(self.patch_label)
      filename = self.signature['gyrus_subsets_of_tracts_MeshClosestPoint'].findValue( attrs )
      print filename
      return filename
  self.linkParameters( 'gyrus_subsets_of_tracts_MeshClosestPoint', ( 'reorganized_subsets_of_tracts', 'patch_label' ), linkTracts )
  self.linkParameters( 'gyrus_subsets_of_tracts_MeshIntersectPoint', 'gyrus_subsets_of_tracts_MeshClosestPoint' )
  
def execution ( self, context ):
  context.write( 'For a given cortex region, the fibers associated are retained.' )
  context.system( 'python', find_in_path( 'BundlesSelectForALabel.py' ), 
    '--inputparcelstex', self.gyri_segmentation,
    '--label',  self.patch_label,
    '--bundles', self.reorganized_subsets_of_tracts,
    '--obundles', self.gyrus_subsets_of_tracts_MeshClosestPoint,
    '--verbose', 1
  )
  context.system( 'selectBundlesFromNames',
    '-i', self.reorganized_subsets_of_tracts,
    '-o', self.gyrus_subsets_of_tracts_MeshIntersectPoint,
    '-names', str(self.patch_label) + '_notInMesh',
    '-verbose'
  )
  context.write( 'OK' )
  