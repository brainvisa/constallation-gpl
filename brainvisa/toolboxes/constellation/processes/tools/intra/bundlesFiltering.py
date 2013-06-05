# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path
import glob

def validation():
  if not find_in_path( 'constelBundlesFiltering' ):
    raise ValidationError( 'constellation module is not here.' )

name = 'Bundles Filtering'
userLevel = 2

signature = Signature(
                    'study', String(),
                  'texture', String(),
                    'gyrus', String(),
                 'database', Choice(),
                  'subject', ReadDiskItem( 'subject', 'directory' ),
          'subset_of_tract', ReadDiskItem( 'Fascicles bundles', 'Aims bundles' ),
  'listOf_subsets_of_tract', ListOf( ReadDiskItem( 'Fascicles bundles', 'Aims bundles' ) ),
             'gyri_texture', ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ),
               'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
                 'dw_to_t1', ReadDiskItem( 'Transformation matrix', 'Transformation matrix' ),
        'min_cortex_length', Float(),
        'max_cortex_length', Float(),
'min_distant_fibers_length', Float(),
'max_distant_fibers_length', Float(),

  'subsets_of_tracts_FibersNearCortex', WriteDiskItem( 'Gyrus Length Interval Tracts Fibers Near Cortex', 'Aims bundles' ),
     'subsets_of_tracts_distantFibers', WriteDiskItem( 'Gyrus Length Interval Tracts Distant Fibers', 'Aims bundles' ),
)


def initialization( self ):
  databases=[h.name for h in neuroHierarchy.hierarchies() if h.fso.name == 'brainvisa-3.2.0']
  self.signature['database'].setChoices(*databases)
  if len( databases ) != 0:
    self.database=databases[0]
  else:
    self.signature[ 'database' ] = OpenChoice()
  def lef( self, dummy ):
    if self.subset_of_tract is not None:
      d = os.path.dirname( self.subset_of_tract.fullPath() )
      listBundles = glob.glob( os.path.join( d, '*.bundles' ) )
      return listBundles
  def linkProfile( self, dummy ):
    if self.subject is None:
      return None
    if self.subset_of_tract is not None and self.gyrus is not None and self.study is not None and self.texture is not None and self.min_cortex_length is not None and self.database is not None and self.subject is not None:
      attrs = dict( self.subset_of_tract.hierarchyAttributes() )
      attrs.update( self.subject.hierarchyAttributes() )
      attrs['study'] = self.study
      attrs['texture'] = self.texture
      attrs['_database'] = self.database
      attrs['subject'] = os.path.basename( self.subject.fullPath() )
      attrs['gyrus'] = 'G' + str( self.gyrus )
      attrs['minlengthoffibersIn'] = str( int(self.min_cortex_length) )
      filename = self.signature[ 'subsets_of_tracts_FibersNearCortex' ].findValue( attrs )
      print attrs
      return filename
  def linkProfileDistantFibers( self, dummy ):
    if self.subsets_of_tracts_FibersNearCortex is not None:
      attrs = dict( self.subsets_of_tracts_FibersNearCortex.hierarchyAttributes() )
      attrs['minlengthoffibersOut'] = str( int( self.min_distant_fibers_length ) )
      filename = self.signature[ 'subsets_of_tracts_distantFibers' ].findValue( attrs )
      return filename
  self.linkParameters( 'listOf_subsets_of_tract', 'subset_of_tract', lef )
  self.linkParameters( 'subsets_of_tracts_FibersNearCortex', ( 'database', 'subset_of_tract', 'subject', 'study', 'texture', 'gyrus', 'min_cortex_length' ), linkProfile )
  self.linkParameters( 'subsets_of_tracts_distantFibers', ( 'subsets_of_tracts_FibersNearCortex', 'min_distant_fibers_length' ), linkProfileDistantFibers )
  self.linkParameters( 'white_mesh', 'subject' )
  self.linkParameters( 'dw_to_t1', 'subset_of_tract' )
  
  self.signature['listOf_subsets_of_tract'].userLevel = 2
  self.min_cortex_length = 30.
  self.max_cortex_length = 500.
  self.min_distant_fibers_length = 20.
  self.max_distant_fibers_length = 500.


def execution( self, context ):
  cmd = [ 'constelBundlesFiltering' ]
  for subset_of_tract in self.listOf_subsets_of_tract:
    cmd += [ '-i', subset_of_tract ]
  cmd += [
    '-o', self.subsets_of_tracts_FibersNearCortex,
    '-n', self.subsets_of_tracts_distantFibers,
    '--mesh', self.white_mesh,
    '--tex', self.gyri_texture,
    '--trs', self.dw_to_t1,
    '--mode', 'Name1_Name2orNotInMesh',
    '--names', '^' + self.gyrus + '_[0-9]+$',
    '--names', '^[0-9]+_' + self.gyrus + '$',
    '-g', self.gyrus,
    #'--verbose',
    '-r',
    '-l', self.min_cortex_length,
    '-L', self.max_cortex_length,
    '--nimlmin', self.min_distant_fibers_length,
    '--nimlmax', self.max_distant_fibers_length,
  ]

  context.system( *cmd )