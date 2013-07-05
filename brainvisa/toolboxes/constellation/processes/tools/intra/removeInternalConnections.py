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
  'gyrus_connectivity_profile', ReadDiskItem( 'Gyrus Connectivity Profile', 'Aims texture formats' ),
                'gyri_texture', ReadDiskItem( 'FreesurferResampledBothParcellationType', 'Aims texture formats' ),
                  'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
                       'gyrus', Integer(),
  
  'thresholded_connectivity_profile', WriteDiskItem( 'Thresholded Connectivity Profile', 'Aims texture formats' ),
         'norm_connectivity_profile', WriteDiskItem( 'Normed Connectivity Profile', 'Aims texture formats' ),
)

def initialization ( self ):
  self.setOptional( 'gyrus' )
  self.linkParameters( 'thresholded_connectivity_profile', 'gyrus_connectivity_profile' )
  self.linkParameters( 'norm_connectivity_profile', 'thresholded_connectivity_profile' )

def execution ( self, context ):
  context.write( 'Threshold mean connectivity profile.' )
  if self.gyrus is not None:
    gyrus = self.gyrus # keep internal connections, put 0
  else:
    gyrus = os.path.basename( os.path.dirname( os.path.dirname( self.gyrus_connectivity_profile.fullPath() ) ) )
    gyrus = gyrus.strip('G')
  context.write('gyrus = ', gyrus, '    Is it correct?')
  mask = aims.read( self.gyri_texture.fullPath() )
  smoothMeanConnectivityProfileTex = aims.read( self.gyrus_connectivity_profile.fullPath() )
  marr =  mask[0].arraydata()
  smcarr = smoothMeanConnectivityProfileTex[0].arraydata()
  for i in xrange( smoothMeanConnectivityProfileTex[0].nItem() ):
    smcarr[marr==int(gyrus)] = 0
  aims.write( smoothMeanConnectivityProfileTex, self.thresholded_connectivity_profile.fullPath() )
  meanConnectivityProfileTexture_filename = self.thresholded_connectivity_profile

  context.write( 'Normalized between 0 And 1 mean connectivity profiles.' )
  dividende_coef = 0
  dividende_coef = smcarr.max()
  print "max connections value:", dividende_coef
  if dividende_coef > 0:
    z = 1./dividende_coef
    smcarr *= z
  aims.write( smoothMeanConnectivityProfileTex, self.norm_connectivity_profile.fullPath() )
  context.write( 'OK' )


