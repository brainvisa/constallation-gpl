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
  'complete_connectivity_matrix', ReadDiskItem( 'Gyrus Connectivity Matrix',  
                                                'Matrix sparse' ),
  'gyri_texture', ReadDiskItem( 'FreesurferResampledBothParcellationType', 
                                'Aims texture formats' ),
  'gyrus', Integer(),
  'patch_connectivity_profile', WriteDiskItem( 'Gyrus Connectivity Profile', 
                                               'Aims texture formats' ),
)

def initialization ( self ):
  def linkSmoothing(self, dummy):
    if self.complete_connectivity_matrix is not None:
      attrs = dict( self.complete_connectivity_matrix.hierarchyAttributes() )
      attrs['subject'] =  self.complete_connectivity_matrix.get('subject')
      attrs['study'] = self.complete_connectivity_matrix.get('study')
      attrs['texture'] = self.complete_connectivity_matrix.get('texture')
      attrs['gyrus'] = self.complete_connectivity_matrix.get('gyrus')
      attrs['smoothing'] = 'smooth' + str( attrs['smoothing'] )
      filename = self.signature['patch_connectivity_profile'].findValue( attrs )
      return filename
  self.setOptional( 'gyrus' )
  self.linkParameters( 'patch_connectivity_profile', 
                       'complete_connectivity_matrix' , linkSmoothing )

def execution ( self, context ):
  if self.gyrus is not None:
    gyrus = self.gyrus
  else:
    gyrus = os.path.basename( os.path.dirname( os.path.dirname( 
      self.complete_connectivity_matrix.fullPath() ) ) )
    gyrus = gyrus.strip('G')
  context.write( 'gyrus ', gyrus )
  context.system( 'constelMeanConnectivityProfileFromMatrix',
    '-connfmt', 'binar_sparse',
    '-connmatrixfile', self.complete_connectivity_matrix,
    '-outconntex', self.patch_connectivity_profile,
    '-seedregionstex', self.gyri_texture,
    '-seedlabel', gyrus,
    '-verbose', 1,
    '-type', 'seed_mean_connectivity_profile',
    '-normalize', 0
  )