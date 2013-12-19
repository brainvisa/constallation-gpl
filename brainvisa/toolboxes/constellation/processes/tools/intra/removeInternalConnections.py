# -*- coding: utf-8 -*-
from brainvisa.processes import *
try:
  from soma import aims
except:
  pass

def validation():
  try:
    import soma.aims
  except:
    raise ValidationError( 'module soma.aims is not here.' )

name = 'Remove Internal Connections'
userLevel = 2

signature = Signature(
  'patch_connectivity_profile', ReadDiskItem( 'Gyrus Connectivity Profile', 
                                              'Aims texture formats' ),
  'gyri_texture', ReadDiskItem( 'FreesurferResampledBothParcellationType', 
                                'Aims texture formats' ),
  'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
  'gyrus', Integer(),
  'thresholded_connectivity_profile', WriteDiskItem( 
                                        'Thresholded Connectivity Profile', 
                                        'Aims texture formats' 
                                      ),
  'norm_connectivity_profile', WriteDiskItem( 'Normed Connectivity Profile', 
                                              'Aims texture formats' ),
)

def initialization ( self ):
  self.setOptional( 'gyrus' )
  self.linkParameters( 'thresholded_connectivity_profile', 
                       'patch_connectivity_profile' )
  self.linkParameters( 'norm_connectivity_profile', 
                       'thresholded_connectivity_profile' )

def execution ( self, context ):
  context.write( 'Threshold mean connectivity profile.' )
  if self.gyrus is not None:
    gyrus = self.gyrus # keep internal connections, put 0
  else:
    gyrus = os.path.basename( os.path.dirname( os.path.dirname( 
            os.path.dirname( self.patch_connectivity_profile.fullPath() ) ) ) )
    gyrus = gyrus.strip('G')
  context.write('gyrus ', gyrus )
  mask = aims.read( self.gyri_texture.fullPath() )
  pcp = aims.read( self.patch_connectivity_profile.fullPath() )
  maskarr =  mask[0].arraydata()
  pcparr = pcp[0].arraydata()
  for i in xrange( pcp[0].nItem() ):
    pcparr[maskarr == int(gyrus)] = 0
  aims.write( pcp, self.thresholded_connectivity_profile.fullPath() )

  dividende_coef = 0
  dividende_coef = pcparr.max()
  if dividende_coef > 0:
    z = 1./dividende_coef
    pcparr *= z
  aims.write( pcp, self.norm_connectivity_profile.fullPath() )
  context.write( 'OK' )


