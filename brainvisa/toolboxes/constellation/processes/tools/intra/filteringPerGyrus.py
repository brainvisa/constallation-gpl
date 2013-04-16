# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path
import glob

def validation():
  try:
    import roca
  except:
    raise ValidationError( 'module roca is not here.' )


name = '02/03 - Filtering Per Gyrus'
userLevel = 2

signature = Signature(

          'reorganized_subset_of_tract', ReadDiskItem( 'Gyri Regrouped Subset of Tracts', 'Aims bundles' ),
  'listof_reorganized_subset_of_tracts', ListOf( ReadDiskItem( 'Gyri Regrouped Subset of Tracts', 'Aims bundles' ) ),
                    'gyri_segmentation', ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ),
                          'patch_label', Integer(),

  'reorganized_subsets_of_tracts_bundlesnames', ListOf( WriteDiskItem( 'Bundles Name List associated to One Subset of Tracts', 'Text file' ) ),
    'gyrus_subsets_of_tracts_MeshClosestPoint', ListOf( WriteDiskItem( 'Gyrus Subset of Tracts Mesh Closest Point', 'Aims bundles' ) ),
  'gyrus_subsets_of_tracts_MeshIntersectPoint', ListOf( WriteDiskItem( 'Gyrus Subset of Tracts Mesh Intersect Point', 'Aims bundles' ) ),
               'gyrus_tracts_MeshClosestPoint', WriteDiskItem( 'Gyrus Tracts Mesh Closest Point', 'Aims bundles' ),
             'gyrus_tracts_MeshIntersectPoint', WriteDiskItem( 'Gyrus Tracts Mesh Intersect Point', 'Aims bundles' ),
)

def initialization( self ):
  def lef(self, dummy):
    if self.reorganized_subset_of_tract is not None:
      d = os.path.dirname( self.reorganized_subset_of_tract.fullPath() )
      listBundles = glob.glob( d+'/*.bundles' )
      return listBundles
  def linkTracts( self, dummy ):
    if self.listof_reorganized_subset_of_tracts is not None and self.patch_label is not None:
      li = []
      i = 0
      for tex in self.listof_reorganized_subset_of_tracts:
        attrs = dict( self.listof_reorganized_subset_of_tracts[i].hierarchyAttributes() )
        attrs['gyrus'] = 'G' + str(self.patch_label)
        x = self.signature[ 'gyrus_subsets_of_tracts_MeshClosestPoint'].findValue( attrs )
        x = WriteDiskItem( 'Gyrus Subset of Tracts Mesh Closest Point', 'Aims bundles' ).findValue( attrs )
        li.append( x )
        i += 1
      return li
  def linkTractsBis( self, dummy ):
    if self.reorganized_subset_of_tract is not None and self.patch_label is not None:
      attrs = dict( self.reorganized_subset_of_tract.hierarchyAttributes() )
      attrs['gyrus' ] = 'G' + str(self.patch_label)
      filename = self.signature[ 'gyrus_tracts_MeshClosestPoint' ].findValue( attrs )
      return filename
  self.linkParameters( 'listof_reorganized_subset_of_tracts', 'reorganized_subset_of_tract', lef )
  self.linkParameters( 'reorganized_subsets_of_tracts_bundlesnames', 'listof_reorganized_subset_of_tracts' )
  self.linkParameters( 'gyrus_subsets_of_tracts_MeshClosestPoint', ( 'listof_reorganized_subset_of_tracts', 'patch_label' ), linkTracts )
  self.linkParameters( 'gyrus_subsets_of_tracts_MeshIntersectPoint', 'gyrus_subsets_of_tracts_MeshClosestPoint' )
  self.linkParameters( 'gyrus_tracts_MeshClosestPoint', ( 'reorganized_subset_of_tract', 'patch_label' ), linkTractsBis )
  self.linkParameters( 'gyrus_tracts_MeshIntersectPoint', 'gyrus_tracts_MeshClosestPoint' )

  self.signature['listof_reorganized_subset_of_tracts'].userLevel = 3
  self.signature['reorganized_subsets_of_tracts_bundlesnames'].userLevel = 3
  self.signature['gyrus_subsets_of_tracts_MeshClosestPoint'].userLevel = 3
  self.signature['gyrus_subsets_of_tracts_MeshIntersectPoint'].userLevel = 3

def execution( self, context ):
  if self.listof_reorganized_subset_of_tracts is not None:
    context.write( 'For a given cortex region, the fibers associated are retained.')
    i = 0
    for tractfile in self.listof_reorganized_subset_of_tracts:
      context.system( 'python', find_in_path( 'BundlesSelectForALabel.py' ),
        '--inputparcelstex', self.gyri_segmentation,
        '--label',  self.patch_label,
        '--bundles', self.listof_reorganized_subset_of_tracts[i],
        '--obundles', self.gyrus_subsets_of_tracts_MeshClosestPoint[i],
        '--verbose', 1
      )
      context.system( 'selectBundlesFromNames',
        '-i', self.listof_reorganized_subset_of_tracts[i],
        '-o', self.gyrus_subsets_of_tracts_MeshIntersectPoint[i],
        '-names', str(self.patch_label) + '_notInMesh',
        '-verbose'
      )
      i += 1
  context.write( 'OK (1/2)')

  context.write( 'Merging files into two general categories, according to their source (between two connected regions or one place in the brain)' )
  cmd_args = [ "-i" ]
  cmd_args += self.gyrus_subsets_of_tracts_MeshClosestPoint
  cmd_args += [ "-o", self.gyrus_tracts_MeshClosestPoint ]   
  context.system( "comistBundlesFusion_old", *cmd_args )

  cmd_args2 = [ "-i" ]
  cmd_args2 += self.gyrus_subsets_of_tracts_MeshIntersectPoint
  cmd_args2 += [ "-o", self.gyrus_tracts_MeshIntersectPoint ]    
  context.system( "comistBundlesFusion_old", *cmd_args2 )
  context.write( 'OK (2/2)' )
