# -*- coding: utf-8 -*-
from brainvisa.processes import *
from brainvisa.group_utils import Subject
from soma.minf.api import registerClass, readMinf
from soma.path import find_in_path
from soma import aims
import threading

def validation():
  if not find_in_path( 'constelConnectivityProfileOverlapMask.py' ):
    raise ValidationError( 'constellation module is not here.' )

name = 'Creation of a mask'
userLevel = 2

signature = Signature(
  'study_name', String(),
  'texture_ind', String(),
  'texture_group', String(),
  'patch_label', Integer(),
  'smoothing', Float(),
  'group', ReadDiskItem( 'Group definition', 'XML' ),
  'connectivity_profiles', ListOf( ReadDiskItem( 'Gyrus Connectivity Profile', 
                                                 'Aims texture formats' ) ),
  'mask', WriteDiskItem( 'Avg Connectivity Mask', 'Aims texture formats' ),
)

def initialization ( self ):
  self.smoothing = 3.0
  self.texture_group = 'fsgroup'
  
  def linkIndProfiles( self, dummy ):
    if self.group is not None:
      registerClass('minf_2.0', Subject, 'Subject')
      groupOfSubjects = readMinf(self.group.fullPath())
      profiles = []
      for subject in groupOfSubjects:      
        study = self.study_name
        texture = self.texture_ind
        smoothing = 'smoothing' + str(self.smoothing)
        gyrus = 'G' + str(self.patch_label)
        profile = ReadDiskItem( 'Gyrus Connectivity Profile', 
                                'Aims texture formats' ).findValue( 
                                { 'study': study, 'texture': texture, 
                                  'gyrus': gyrus, 'smoothing': smoothing }, 
                                 subject.attributes() )
        if profile is not None:
          profiles.append( profile )
      return profiles
  
  def linkMask( self, dummy ):
    if self.connectivity_profiles and self.group and self.smoothing is not None:
      atts = dict( self.group.hierarchyAttributes() )
      atts[ 'study' ] = self.connectivity_profiles[0].get( 'study' )
      atts[ 'texture' ] = self.texture_group
      atts[ 'gyrus' ] = self.connectivity_profiles[0].get( 'gyrus' )
      atts[ 'smoothing' ] = 'smoothing' + str(self.smoothing)
      return self.signature[ 'mask' ].findValue( atts )
      
  self.linkParameters( 'connectivity_profiles', ( 'group', 'study_name', 
                       'texture_ind', 'patch_label', 'smoothing' ), 
                       linkIndProfiles )
  self.linkParameters( 'mask', ( 'connectivity_profiles', 'texture_group', 
                                 'smoothing' ) , linkMask )
  self.signature['connectivity_profiles'].userLevel = 3

def execution ( self, context ):
  args = []
  for x in self.connectivity_profiles:
    args += [ '-p', x ]
  args += [ '-o', self.mask ]
  context.system( sys.executable, 
    find_in_path( 'constelConnectivityProfileOverlapMask.py' ),
    *args
  )