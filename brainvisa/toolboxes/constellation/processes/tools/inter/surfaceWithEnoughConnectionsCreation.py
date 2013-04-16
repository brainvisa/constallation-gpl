# -*- coding: utf-8 -*-
from brainvisa.processes import *
from brainvisa.group_utils import Subject
from soma.minf.api import registerClass, readMinf
from soma.path import find_in_path
from soma import aims

def validation():
  try:
    import roca
  except:
    raise ValidationError( 'module roca is not here.' )

name = '01 - Creation of a mask'
userLevel = 2

signature = Signature(
                       'study_name', String(),
                       'texture_in', String(),
                      'texture_out', String(),
                      'patch_label', Integer(),
                            'group', ReadDiskItem( 'Group definition', 'XML' ),
  'individual_connectivity_profile', ListOf( ReadDiskItem( 'Gyrus Connectivity Profile', 'Aims texture formats' ) ),
                             'mask', WriteDiskItem( 'Mean Connectivity Profile Mask', 'Aims texture formats' ),
)

def initialization ( self ):
  def linkIndividualProfiles( self, dummy ):
    if self.group is not None and self.individual_connectivity_profile is not None:
      registerClass('minf_2.0', Subject, 'Subject')
      groupOfSubjects = readMinf(self.group.fullPath())
      profiles = []
      for subject in groupOfSubjects:
        proto = 'subjects'
        study = self.study_name
        texture = self.texture_in
        gyrus = 'G' + str(self.patch_label)
        profiles.append( ReadDiskItem( 'Gyrus Connectivity Profile', 'Aims texture formats' ).findValue( { 'protocol': proto, 'study': study, 'texture': texture, 'gyrus': gyrus }, subject.attributes() ) )
        print profiles
      return profiles
  def linkGroupProfiles( self, dummy ):
    if self.individual_connectivity_profile and self.group is not None:
      atts = dict( self.group.hierarchyAttributes() )
      atts[ 'study' ] = self.individual_connectivity_profile[0].get( 'study' )
      atts[ 'texture' ] = self.texture_out
      atts[ 'gyrus' ] = self.individual_connectivity_profile[0].get( 'gyrus' )
      return self.signature[ 'mask' ].findValue( atts )
  self.linkParameters( 'individual_connectivity_profile', ( 'group', 'study_name', 'texture_in', 'patch_label' ), linkIndividualProfiles )
  self.linkParameters( 'mask', ( 'individual_connectivity_profile', 'texture_out' ) , linkGroupProfiles )
  self.signature['individual_connectivity_profile'].userLevel = 2

def execution ( self, context ):
  mainThreadActions().call( aims.carto.PluginLoader.load )

  registerClass('minf_2.0', Subject, 'Subject')
  groupOfSubjects = readMinf(self.group.fullPath())

  context.write( 'Creation of a mask... ' )
  args = []
  for x in self.individual_connectivity_profile:
    args += [ '-p', x ]
  args += [ '-o', self.mask ]
  context.system('python', find_in_path( 'mask.py' ),
   *args
  )
  context.write( 'OK' )

  
