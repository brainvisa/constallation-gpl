# -*- coding: utf-8 -*-
from brainvisa.processes import *
#import glob

def validation():
  if not findInPath( 'constelBundlesFiltering' ):
    raise ValidationError( 'constellation module is not here.' )

name = 'Bundles Filtering'
userLevel = 2

signature = Signature(
                    'study', String(),
                  'texture', String(),
                    'gyrus', String(),
          'subset_of_tract', ReadDiskItem( 'Fascicles bundles', 'Aims bundles' ),
  'listOf_subsets_of_tract', ReadDiskItem( 'Fascicles bundles', 'Aims bundles' ),
               'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
             'gyri_texture', ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ),
                 'dw_to_t1', ReadDiskItem( 'Transformation matrix', 'Transformation matrix' ),

  'subsets_of_tracts_FibersNearCortex', WriteDiskItem( 'Gyrus Subset of Tracts Mesh Closest Point', 'Aims bundles' ),
     'subsets_of_tracts_distantFibers', WriteDiskItem( 'Gyrus Subset of Tracts Mesh Intersect Point', 'Aims bundles' ),
                       'bundles_names', WriteDiskItem( 'Bundles Name List associated to One Subset of Tracts', 'Text file' ),
)


def initialization( self ):
  #def lef(self, dummy):
    #if self.subset_of_tract is not None:
      #d = os.path.dirname( self.subset_of_tract.fullPath() )
      #listBundles = glob.glob( d+'/*.bundles' )
      #return listBundles
      
  #self.linkParameters( 'listOf_subsets_of_tract', 'subset_of_tract', lef )
  
  self.signature['listOf_subsets_of_tract'].userLevel = 2


def execution( self, context ):
  context.system( 'constelBundlesFiltering',
    '-i', self.listOf_subsets_of_tract,
    '-o', self.subsets_of_tracts_FibersNearCortex,
    '-n', self.subsets_of_tracts_distantFibers,
    '--namesfile', self.bundles_names,
    '--mesh', self.white_mesh,
    '--tex', self.gyri_texture,
    '--trs', self.dw_to_t1,
    '--mode', 'Name1_Name2orNotInMesh',
    '--names', '^' + self.gyrus + '_[0-9]+$',
    '--names', '^[0-9]+_' + self.gyrus + '$',
    '-g', self.gyrus,
    '--verbose',
    '-r'
  )