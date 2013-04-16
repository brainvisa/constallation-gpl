# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma import aims
import pylab

name = '11 - Threshold Mean Connectivity Profile'
userLevel = 2

signature = Signature(
  'gyrus_mean_connectivity_profile', ReadDiskItem( 'Gyrus Connectivity Profile', 'Aims texture formats' ),
                'gyri_segmentation', ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ),
                       'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
                      'patch_label', Integer(),
  
  'thresholded_mean_connectivity_profile', WriteDiskItem( 'Thresholded Connectivity Profile', 'Aims texture formats' ),
         'norm_mean_connectivity_profile', WriteDiskItem( 'Normed Connectivity Profile', 'Aims texture formats' ),
)

def initialization ( self ):
  self.setOptional( 'patch_label' )
  self.linkParameters( 'thresholded_mean_connectivity_profile', 'gyrus_mean_connectivity_profile' )
  self.linkParameters( 'norm_mean_connectivity_profile', 'thresholded_mean_connectivity_profile' )

def execution ( self, context ):
  context.write( 'Threshold mean connectivity profile.' )
  if self.patch_label is not None:
    patch_label = self.patch_label # keep internal connections, put 0
  else:
    patch_label = os.path.basename( os.path.dirname( os.path.dirname( self.gyrus_mean_connectivity_profile.fullPath() ) ) )
    patch_label = patch_label.strip('G')
  context.write('patch_label = ', patch_label, '    Is it correct?')
  mask = aims.read( self.gyri_segmentation.fullPath() )
  smoothMeanConnectivityProfileTex = aims.read( self.gyrus_mean_connectivity_profile.fullPath() )
  for i in xrange( smoothMeanConnectivityProfileTex[0].nItem() ):
    if mask[0][i] == int(patch_label):
      smoothMeanConnectivityProfileTex[0][i] = 0
  aims.write( smoothMeanConnectivityProfileTex, self.thresholded_mean_connectivity_profile.fullPath() )
  meanConnectivityProfileTexture_filename = self.thresholded_mean_connectivity_profile
  
  context.write( 'Normalized between 0 And 1 mean connectivity profiles.' )
  tex = aims.read( meanConnectivityProfileTexture_filename.fullPath() )
  tex_ar = tex[0].arraydata()
  dividende_coef = 0
  dividende_coef = tex_ar.max()
  print "max connections value:", dividende_coef
  if dividende_coef > 0:
    z = 1./dividende_coef
    for i in xrange(tex[0].nItem()):
      value = tex[0][i]
      tex[0][i]= z*value
  aims.write( tex, self.norm_mean_connectivity_profile.fullPath() )
  context.write( 'OK' )
  
  
  
  
  