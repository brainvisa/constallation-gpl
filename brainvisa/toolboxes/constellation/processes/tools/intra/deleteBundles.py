# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path
import glob

name = 'Cancel Intermediate Fibers'
userLevel = 2

signature = Signature(
                'reorganized_subset_of_tract', ReadDiskItem( 'Gyri Regrouped Subset of Tracts', 'Aims bundles' ),
        'listof_reorganized_subset_of_tracts', ListOf( ReadDiskItem( 'Gyri Regrouped Subset of Tracts', 'Aims bundles' ) ),
                                'patch_label', Integer(),
   'gyrus_subsets_of_tracts_MeshClosestPoint', ListOf( ReadDiskItem( 'Gyrus Subset of Tracts Mesh Closest Point', 'Aims bundles' ) ),
 'gyrus_subsets_of_tracts_MeshIntersectPoint', ListOf( ReadDiskItem( 'Gyrus Subset of Tracts Mesh Intersect Point', 'Aims bundles' ) ),
              'gyrus_tracts_MeshClosestPoint', ReadDiskItem( 'Gyrus Tracts Mesh Closest Point', 'Aims bundles' ),
            'gyrus_tracts_MeshIntersectPoint', ReadDiskItem( 'Gyrus Tracts Mesh Intersect Point', 'Aims bundles' ),            
          'tracts_by_length_MeshClosestPoint', ReadDiskItem( 'Gyrus Regrouped By Length Tracts Mesh Closest Point', 'Aims bundles' ),
        'tracts_by_length_MeshIntersectPoint', ReadDiskItem( 'Gyrus Regrouped By Length Tracts Mesh Intersect Point', 'Aims bundles' ),
           'tracts_5percent_MeshClosestPoint', ReadDiskItem( 'Gyrus Tracts Mesh Closest Point 5%', 'Aims bundles' ),
         'tracts_5percent_MeshIntersectPoint', ReadDiskItem( 'Gyrus Tracts Mesh Intersect Point 5%', 'Aims bundles' ),
          'tracts_20percent_MeshClosestPoint', ReadDiskItem( 'Gyrus Length Interval Tracts Mesh Closest Point 20%', 'Aims bundles' ),
        'tracts_20percent_MeshIntersectPoint', ReadDiskItem( 'Gyrus Length Interval Tracts Mesh Intersect Point 20%', 'Aims bundles' ),
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
  self.linkParameters( 'gyrus_subsets_of_tracts_MeshClosestPoint', ( 'listof_reorganized_subset_of_tracts', 'patch_label' ), linkTracts )
  self.linkParameters( 'gyrus_subsets_of_tracts_MeshIntersectPoint', 'gyrus_subsets_of_tracts_MeshClosestPoint' )
  self.linkParameters( 'gyrus_tracts_MeshClosestPoint', ( 'reorganized_subset_of_tract', 'patch_label' ), linkTractsBis )
  self.linkParameters( 'gyrus_tracts_MeshIntersectPoint', 'gyrus_tracts_MeshClosestPoint' )
  self.linkParameters( 'tracts_by_length_MeshIntersectPoint', 'gyrus_tracts_MeshIntersectPoint' )
  self.linkParameters( 'tracts_by_length_MeshClosestPoint', 'gyrus_tracts_MeshClosestPoint' )
  self.linkParameters( 'tracts_5percent_MeshIntersectPoint', 'gyrus_tracts_MeshIntersectPoint' )
  self.linkParameters( 'tracts_5percent_MeshClosestPoint', 'gyrus_tracts_MeshClosestPoint' )
  self.linkParameters( 'tracts_20percent_MeshIntersectPoint', 'gyrus_tracts_MeshIntersectPoint' )
  self.linkParameters( 'tracts_20percent_MeshClosestPoint', 'gyrus_tracts_MeshClosestPoint' )
  self.signature['listof_reorganized_subset_of_tracts'].userLevel = 3

def execution ( self, context ):
  context.write( 'Test if all files are present.' )
  for tract in self.gyrus_subsets_of_tracts_MeshClosestPoint:
    if os.path.exists( tract.fullPath() ):
      context.write( tract.fullPath() + " --- " + str(os.path.exists( tract.fullPath() ) ) )
      os.remove( tract.fullPath() )
    else:
      context.write( 'file do not exist!' )

  for tract in self.gyrus_subsets_of_tracts_MeshIntersectPoint:
    if os.path.exists( tract.fullPath() ):
      context.write( tract.fullPath() + " - " + str(os.path.exists( tract.fullPath() ) ) )
      os.remove( tract.fullPath() )
    else:
      context.write( 'file do not exist!' )


  if os.path.exists( self.gyrus_tracts_MeshClosestPoint.fullPath() ):
    context.write( self.gyrus_tracts_MeshClosestPoint.fullPath() + " - " + str( os.path.exists( self.gyrus_tracts_MeshClosestPoint.fullPath() ) ) )
    os.remove( self.gyrus_tracts_MeshClosestPoint.fullPath() )
  else:
    context.write( 'file do not exist!' )

    
  if os.path.exists(self.gyrus_tracts_MeshIntersectPoint.fullPath()):
    context.write( self.gyrus_tracts_MeshIntersectPoint.fullPath() + " --- " + str(os.path.exists(self.gyrus_tracts_MeshIntersectPoint.fullPath() ) ) )
    os.remove( self.gyrus_tracts_MeshIntersectPoint.fullPath() )
  else:
    context.write( 'file do not exist!' )

  if os.path.exists(self.tracts_by_length_MeshClosestPoint.fullPath()):
    context.write( self.tracts_by_length_MeshClosestPoint.fullPath() + " --- " + str(os.path.exists(self.tracts_by_length_MeshClosestPoint.fullPath() ) ) )
    os.remove( self.tracts_by_length_MeshClosestPoint.fullPath() )
  else:
    context.write( 'file do not exist!' )
    
  if os.path.exists(self.tracts_by_length_MeshIntersectPoint.fullPath()):
    context.write( self.tracts_by_length_MeshIntersectPoint.fullPath() + " --- " + str(os.path.exists(self.tracts_by_length_MeshIntersectPoint.fullPath() ) ) )
    os.remove( self.tracts_by_length_MeshIntersectPoint.fullPath() )
  else:
    context.write( 'file do not exist!' )

  if os.path.exists(self.tracts_5percent_MeshClosestPoint.fullPath()):
    context.write( self.tracts_5percent_MeshClosestPoint.fullPath() + " --- " + str(os.path.exists(self.tracts_5percent_MeshClosestPoint.fullPath() ) ) )
    os.remove( self.tracts_5percent_MeshClosestPoint.fullPath() )
  else:
    context.write( 'file do not exist!' )

  if os.path.exists(self.tracts_5percent_MeshIntersectPoint.fullPath()):
    context.write( self.tracts_5percent_MeshIntersectPoint.fullPath() + " --- " + str(os.path.exists(self.tracts_5percent_MeshIntersectPoint.fullPath() ) ) )
    os.remove( self.tracts_5percent_MeshIntersectPoint.fullPath() )
  else:
    context.write( 'file do not exist!' )

  if os.path.exists(self.tracts_20percent_MeshClosestPoint.fullPath()):
    context.write( self.tracts_20percent_MeshClosestPoint.fullPath() + " --- " + str(os.path.exists(self.tracts_20percent_MeshClosestPoint.fullPath() ) ) )
    os.remove( self.tracts_20percent_MeshClosestPoint.fullPath() )
  else:
    context.write( 'file do not exist!' )

  if os.path.exists(self.tracts_20percent_MeshIntersectPoint.fullPath()):
    context.write( self.tracts_20percent_MeshIntersectPoint.fullPath() + " --- " + str(os.path.exists(self.tracts_20percent_MeshIntersectPoint.fullPath() ) ) )
    os.remove( self.tracts_20percent_MeshIntersectPoint.fullPath() )
  else:
    context.write( 'file do not exist!' )




  #context.remove( x )
  






















  
  #patch_label = 38
  #context.system( 'python', find_in_path( 'BundlesSelectForALabel.py' ),
    #'--inputparcelstex', self.gyri_segmentation,
    #'--label',  patch_label,
    #'--bundles', self.reorganized_subsets_of_tracts,
    #'--obundles', self.gyrus_subsets_of_tracts_MeshClosestPoint,
    #'--verbose', 1
  #)
  #length_max = 500
  #length_min_MeshClosestPoint = 60
  #context.system( 'selectBundlesFromNames',
    #'-i', self.reorganized_subsets_of_tracts,
    #'-o', self.gyrus_subsets_of_tracts_MeshIntersectPoint,
    #'-names', '59_59',#'[0-9]+_[0-9]+',
    #'-verbose',
  #)
#'-r'


  #length_min_MeshClosestPoint = 60
  #length_max = 500
  #context.system( 'selectBundlesFromNames',
    #'-i', self.tracts_by_length_MeshClosestPoint,
    #'-o', self.length_filtered_tracts_MeshClosestPoint,
    #'-names', *[ str(x) for x in xrange( length_min_MeshClosestPoint, length_max + 1 ) ]
  #)
