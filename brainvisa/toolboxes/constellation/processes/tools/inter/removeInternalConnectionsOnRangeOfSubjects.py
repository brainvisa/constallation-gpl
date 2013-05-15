# -*- coding: utf-8 -*-
from brainvisa.processes import *

def validation():
  try:
    import soma.aims
  except:
    raise ValidationError( 'aims module is not here.' )

name = '03 - Normed Connectivity Profile of Group'
userLevel = 2

signature = Signature(
                        'mask', ReadDiskItem( 'Mean Connectivity Profile Mask', 'Aims texture formats' ),
  'connectivity_profile_group', ReadDiskItem( 'Averaged Connectivity Profile', 'Aims texture formats' ),
  
       'thresholded_mean_connectivity_profile', WriteDiskItem( 'Averaged Thresholded Connectivity Profile', 'Aims texture formats' ),
  'norm_thresholded_mean_connectivity_profile', WriteDiskItem( 'Averaged Normed Connectivity Profile', 'Aims texture formats' ),
)

def initialization ( self ):
  self.linkParameters( 'connectivity_profile_group', 'mask' )
  self.linkParameters( 'thresholded_mean_connectivity_profile', 'connectivity_profile_group' )
  self.linkParameters( 'norm_thresholded_mean_connectivity_profile', 'thresholded_mean_connectivity_profile' )

def execution ( self, context ):
  context.write( 'Mean connectivity profile thresholding... ' )

  mask = aims.read( self.mask.fullPath() )
  meanConnectivityProfileTex = aims.read( self.connectivity_profile_group.fullPath() )
  for i in xrange( meanConnectivityProfileTex[0].nItem() ):
    if mask[0][i] == 0:
      meanConnectivityProfileTex[0][i] = 0
  aims.write( meanConnectivityProfileTex, self.thresholded_mean_connectivity_profile.fullPath() )
  
  tex = aims.read( self.thresholded_mean_connectivity_profile.fullPath() )
  tex_ar = tex[0].arraydata()
  max_connections_nb = tex_ar.max()
  print "max connections nb:", max_connections_nb
  if max_connections_nb > 0:
    z = 1./max_connections_nb
    for i in xrange(tex[0].nItem()):
      value = tex[0][i]
      tex[0][i]= z*value
  aims.write(tex, self.norm_thresholded_mean_connectivity_profile.fullPath() )


