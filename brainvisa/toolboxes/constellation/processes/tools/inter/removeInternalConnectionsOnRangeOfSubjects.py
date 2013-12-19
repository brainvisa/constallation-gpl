# -*- coding: utf-8 -*-
from brainvisa.processes import *

def validation():
  try:
    import soma.aims
  except:
    raise ValidationError( 'aims module is not here.' )

name = 'Normed Connectivity Profile of Group'
userLevel = 2

signature = Signature(
  'mask', ReadDiskItem( 'Avg Connectivity Mask', 'Aims texture formats' ),
  'connectivity_profiles', ReadDiskItem( 'Avg Connectivity Profile', 
                                              'Aims texture formats' ),
  'thresholded_connectivity_profile', WriteDiskItem( 
                                        'Avg Thresholded Connectivity Profile', 
                                        'Aims texture formats' 
                                      ),
  'normed_connectivity_profile', WriteDiskItem( 
                                   'Avg Normed Connectivity Profile', 
                                   'Aims texture formats' 
                                 ),
)

def initialization ( self ):
  self.linkParameters( 'connectivity_profiles', 'mask' )
  self.linkParameters( 'thresholded_connectivity_profile', 
                       'connectivity_profiles' )
  self.linkParameters( 'normed_connectivity_profile', 
                       'thresholded_connectivity_profile' )

def execution ( self, context ):
  context.write( 'Mean connectivity profile thresholding... ' )

  mask = aims.read( self.mask.fullPath() )
  meanConnectivityProfileTex = aims.read( 
                               self.connectivity_profiles.fullPath() )
  for i in xrange( meanConnectivityProfileTex[0].nItem() ):
    if mask[0][i] == 0:
      meanConnectivityProfileTex[0][i] = 0
  aims.write( meanConnectivityProfileTex, 
              self.thresholded_connectivity_profile.fullPath() )
  
  tex = aims.read( self.thresholded_connectivity_profile.fullPath() )
  tex_ar = tex[0].arraydata()
  max_connections_nb = tex_ar.max()
  if max_connections_nb > 0:
    z = 1./max_connections_nb
    for i in xrange(tex[0].nItem()):
      value = tex[0][i]
      tex[0][i]= z*value
  aims.write(tex, self.normed_connectivity_profile.fullPath() )


