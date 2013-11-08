# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path
from soma import aims

def validation():
  if not find_in_path( 'constelMeanConnectivityProfileFromMatrix' ):
    raise ValidationError( 'constellation module is not here.' )


name = 'Mean Connectivity Profile'
userLevel = 2

signature = Signature(
  'connectivity_matrix_full', ReadDiskItem( 'Gyrus Connectivity Matrix', 'Matrix sparse' ),
              'gyri_texture', ReadDiskItem( 'FreesurferResampledBothParcellationType', 'Aims texture formats' ),
                     'gyrus', Integer(),

  'gyrus_connectivity_profile', WriteDiskItem( 'Gyrus Connectivity Profile', 'Aims texture formats' ),
)

def initialization ( self ):
  def linkSmooth(self, dummy):
    if self.connectivity_matrix_full is not None:
      attrs = dict( self.connectivity_matrix_full.hierarchyAttributes() )
      attrs['subject'] =  self.connectivity_matrix_full.get('subject')
      attrs['study'] = self.connectivity_matrix_full.get('study')
      attrs['texture'] = self.connectivity_matrix_full.get('texture')
      attrs['gyrus'] = self.connectivity_matrix_full.get('gyrus')
      attrs['smooth'] = 'smooth' + str( self.connectivity_matrix_full.get('smooth') )
      print 'atts', attrs
      filename = self.signature['gyrus_connectivity_profile'].findValue( attrs )
      print filename
      return filename
  self.setOptional( 'gyrus' )
  self.linkParameters( 'gyrus_connectivity_profile', 'connectivity_matrix_full' , linkSmooth )

def execution ( self, context ):
  context.write( 'The mean connectivity profile over this region is represented as a texture on the cortex.' )
  if self.gyrus is not None:
    gyrus = self.gyrus
  else:
    gyrus = os.path.basename( os.path.dirname( os.path.dirname( self.connectivity_matrix_full.fullPath() ) ) )
    gyrus = gyrus.strip('G')
  context.write('gyrus = ', gyrus, '    Is it correct?')
  context.system( 'constelMeanConnectivityProfileFromMatrix',
    '-connfmt', 'binar_sparse',
    '-connmatrixfile', self.connectivity_matrix_full,
    '-outconntex', self.gyrus_connectivity_profile,
    '-seedregionstex', self.gyri_texture,
    '-seedlabel', gyrus,
    '-verbose', 1,
    '-type', 'seed_mean_connectivity_profile',
    '-normalize', 0
  )