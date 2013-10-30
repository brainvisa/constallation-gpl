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

name = '01 - Creation of a mask'
userLevel = 2

signature = Signature(
                       'study_name', String(),
                       'texture_in', String(),
                      'texture_out', String(),
                      'patch_label', Integer(),
                           'smooth', Float(),
                            'group', ReadDiskItem( 'Group definition', 'XML' ),
  'individual_connectivity_profile', ListOf( ReadDiskItem( 'Gyrus Connectivity Profile', 'Aims texture formats' ) ),
                             'mask', WriteDiskItem( 'Avg Connectivity Mask', 'Aims texture formats' ),
)

def initialization ( self ):
  def linkIndividualProfiles( self, dummy ):
    if self.group is not None:
      registerClass('minf_2.0', Subject, 'Subject')
      groupOfSubjects = readMinf(self.group.fullPath())
      profiles = []
      for subject in groupOfSubjects:
        
        study = self.study_name
        texture = self.texture_in
        smooth = 'smooth' + str(self.smooth)
        gyrus = 'G' + str(self.patch_label)
        profile = ReadDiskItem( 'Gyrus Connectivity Profile', 'Aims texture formats' ).findValue( { 'study': study, 'texture': texture, 'gyrus': gyrus, 'smooth': smooth }, subject.attributes() )
        if profile is not None:
          profiles.append( profile )
      return profiles
  def linkGroupProfiles( self, dummy ):
    if self.individual_connectivity_profile and self.group is not None:
      atts = dict( self.group.hierarchyAttributes() )
      atts[ 'study' ] = self.individual_connectivity_profile[0].get( 'study' )
      atts[ 'texture' ] = self.texture_out
      atts[ 'gyrus' ] = self.individual_connectivity_profile[0].get( 'gyrus' )
      atts[ 'smooth' ] = self.individual_connectivity_profile[0].get( 'smooth' )
      return self.signature[ 'mask' ].findValue( atts )
  self.linkParameters( 'individual_connectivity_profile', ( 'group', 'study_name', 'texture_in', 'patch_label', 'smooth' ), linkIndividualProfiles )
  self.linkParameters( 'mask', ( 'individual_connectivity_profile', 'texture_out' ) , linkGroupProfiles )
  self.signature['individual_connectivity_profile'].userLevel = 2

def execution ( self, context ):
  if mainThread() is not threading.currentThread():
    mainThreadActions().call( aims.carto.PluginLoader.load )
  else:
    aims.carto.PluginLoader.load()

  registerClass('minf_2.0', Subject, 'Subject')
  groupOfSubjects = readMinf(self.group.fullPath())

  context.write( 'Creation of a mask... ' )
  args = []
  for x in self.individual_connectivity_profile:
    args += [ '-p', x ]
  args += [ '-o', self.mask ]
  context.system('python', 
    find_in_path( 'constelConnectivityProfileOverlapMask.py' ),
    *args
  )
  context.write( 'OK' )

  
