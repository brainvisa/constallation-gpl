# -*- coding: utf-8 -*-
from brainvisa.processes import *
from brainvisa.group_utils import Subject
from soma.minf.api import registerClass, readMinf

name = '02 - Conectivity Profile of Group'
userLevel = 2

signature = Signature(
                                 'study_name', String(),
                                 'texture_in', String(),
                                'texture_out', String(),
                                'patch_label', Integer(),
                                      'group', ReadDiskItem( 'Group definition', 'XML' ),
  'individual_norm_mean_connectivity_profile', ListOf( ReadDiskItem( 'Normed Connectivity Profile', 'Aims texture formats' ) ),
      'thresholded_mean_connectivity_profile', ListOf( ReadDiskItem( 'Thresholded Connectivity Profile', 'Aims texture formats' ) ),
   'norm_mean_connectivity_profile_nb_normed', ListOf( WriteDiskItem( 'Group Normed Connectivity Profile', 'Aims texture formats' ) ),
                 'connectivity_profile_group', WriteDiskItem( 'Averaged Connectivity Profile', 'Aims texture formats' ),
)

def initialization ( self ):
  def linkIndividualProfiles( self, dummy ):
    if self.group is not None:
      registerClass('minf_2.0', Subject, 'Subject')
      groupOfSubjects = readMinf(self.group.fullPath())
      profiles = []
      for subject in groupOfSubjects:
        proto = 'subjects'
        study = self.study_name
        texture = self.texture_in
        gyrus = 'G' + str(self.patch_label)
        profiles.append( ReadDiskItem( 'Normed Connectivity Profile', 'Aims texture formats' ).findValue( { 'protocol': proto, 'study': study, 'texture': texture, 'gyrus': gyrus }, subject.attributes() ) )
      return profiles
  def linkProfiles( self, dummy ):
    if self.thresholded_mean_connectivity_profile and self.group is not None:
      registerClass('minf_2.0', Subject, 'Subject')
      groupOfSubjects = readMinf(self.group.fullPath())
      profiles = []
      i = 0
      for p in self.thresholded_mean_connectivity_profile:
        atts = dict( self.group.hierarchyAttributes() )
        atts[ 'study' ] = self.thresholded_mean_connectivity_profile[i].get( 'study' )
        atts[ 'texture' ] = self.texture_out
        atts[ 'gyrus' ] = self.thresholded_mean_connectivity_profile[i].get( 'gyrus' )
        atts[ 'subject' ] = self.thresholded_mean_connectivity_profile[i].get( 'subject' )
        profiles.append( WriteDiskItem( 'Group Normed Connectivity Profile', 'Aims texture formats' ).findValue( atts ) )
        i += 1
      return profiles
  def linkGroupProfiles( self, dummy ):
    if self.norm_mean_connectivity_profile_nb_normed is not None and self.group is not None:
      atts = dict( self.group.hierarchyAttributes() )
      atts[ 'study' ] = self.norm_mean_connectivity_profile_nb_normed[0].get( 'study' )
      atts[ 'texture' ] = self.texture_out
      atts[ 'gyrus' ] = self.norm_mean_connectivity_profile_nb_normed[0].get( 'gyrus' )
      return self.signature[ 'connectivity_profile_group' ].findValue( atts )
  self.signature['individual_norm_mean_connectivity_profile'].userLevel = 2
  self.linkParameters( 'individual_norm_mean_connectivity_profile', ( 'group', 'study_name', 'texture_in', 'patch_label' ), linkIndividualProfiles )
  self.linkParameters( 'thresholded_mean_connectivity_profile', 'individual_norm_mean_connectivity_profile' )
  self.linkParameters( 'norm_mean_connectivity_profile_nb_normed', ( 'group', 'thresholded_mean_connectivity_profile', 'texture_out' ), linkProfiles )
  self.linkParameters( 'connectivity_profile_group', 'norm_mean_connectivity_profile_nb_normed', linkGroupProfiles )

def execution ( self, context ):
  context.write( 'Process Combine All Subjects Mean Connectivity Profile...' )

  '''
  A connectivity profile is determinated on a range of subjects ( for a group of subjects )
  '''

  registerClass( 'minf_2.0', Subject, 'Subject' )
  groupOfSubjects = readMinf( self.group.fullPath() )

  n = 0
  listOfTex = []
  for texture, outtexname in zip( self.thresholded_mean_connectivity_profile, self.norm_mean_connectivity_profile_nb_normed ):
    tex = aims.read( texture.fullPath() )
    tex_ar = tex[0].arraydata()
    dividende_coef = 0
    mode = "nb_mode"
    if mode == "max_mode":
      dividende_coef = tex_ar.max()
    elif mode == "nb_mode":
      dividende_coef = tex_ar.sum()
    if dividende_coef > 0:
      z = 1./dividende_coef
      for i in xrange(tex[0].nItem()):
        value = tex[0][i]
        tex[0][i]= z*value
    n += 1
    listOfTex.append( outtexname )
    aims.write( tex, outtexname.fullPath() )

  tex_nb = len( listOfTex )
  count = 0
  for tex_filename in listOfTex:
    if count == 0:
      context.write( tex_filename )
      context.write( self.connectivity_profile_group )
      shutil.copyfile( str(tex_filename), str(self.connectivity_profile_group) )
    else:
      context.system('AimsLinearComb',
        '-i', tex_filename,
        '-j', self.connectivity_profile_group,
        '-o', self.connectivity_profile_group
      )
    count += 1
  
  averageTexture = aims.read( self.connectivity_profile_group.fullPath() )
  subjects_nb = len( groupOfSubjects )
  if subjects_nb == 0:
    raise exceptions.ValueError( "subjects_list is empty" )
  for i in xrange( averageTexture.nItem() ):
    val = averageTexture[0][i]
    averageTexture[0][i] = val/subjects_nb
  aims.write( averageTexture, self.connectivity_profile_group.fullPath() )
