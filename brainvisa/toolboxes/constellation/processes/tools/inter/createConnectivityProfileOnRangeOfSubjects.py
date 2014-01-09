# -*- coding: utf-8 -*-
from brainvisa.processes import *
from brainvisa.group_utils import Subject
from soma.minf.api import registerClass, readMinf

def validation():
  try:
    import soma.aims
  except:
    raise ValidationError( 'aims module is not here.' )

name = 'Connectivity Profile of Group'
userLevel = 2

signature = Signature(
  'study_name', String(),
  'texture_ind', String(),
  'texture_group', String(),
  'patch_label', Integer(),
  'smoothing', Float(),
  'group', ReadDiskItem( 'Group definition', 'XML' ),
  'normed_connectivity_profiles', ListOf( 
                                  ReadDiskItem( 'Normed Connectivity Profile', 
                                                'Aims texture formats' ) 
                                  ),
  'thresholded_connectivity_profile', ListOf( 
                                      ReadDiskItem( 'Thresholded Connectivity Profile', 
                                                    'Aims texture formats' ) 
                                      ),
  'normed_connectivity_profile_nb', ListOf( 
                                    WriteDiskItem( 'Group Normed Connectivity Profile', 
                                                   'Aims texture formats' ) 
                                    ),
  'group_connectivity_profile', WriteDiskItem( 'Avg Connectivity Profile', 
                                               'Aims texture formats' ),
)

def initialization ( self ):
  def linkIndividualProfiles( self, dummy ):
    if self.group is not None:
      registerClass('minf_2.0', Subject, 'Subject')
      groupOfSubjects = readMinf(self.group.fullPath())
      profiles = []
      for subject in groupOfSubjects:
        study = self.study_name
        texture = self.texture_ind
        gyrus = 'G' + str(self.patch_label)
        smoothing = 'smooth' + str(self.smoothing)
        profile = ReadDiskItem( 'Normed Connectivity Profile', 
                                'Aims texture formats' ).findValue( 
                                { 'study': study, 'texture': texture, 
                                'gyrus': gyrus, 'smoothing': smoothing }, 
                                subject.attributes() )
        if profile is None:
          return []
        profiles.append( profile )
      return profiles
  def linkProfiles( self, dummy ):
    if self.thresholded_connectivity_profile and self.group is not None:
      profiles = []
      for p in self.thresholded_connectivity_profile:
        if p is None:
          continue
        atts = dict( self.group.hierarchyAttributes() )
        atts[ 'study' ] = p.get( 'study' )
        atts[ 'texture' ] = self.texture_group
        atts[ 'gyrus' ] = p.get( 'gyrus' )
        atts[ 'subject' ] = p.get( 'subject' )
        profile = WriteDiskItem( 'Group Normed Connectivity Profile', 
                                 'Aims texture formats' ).findValue( atts )
        if profile is None:
          return []
        profiles.append( profile )
      return profiles
  def linkGroupProfiles( self, dummy ):
    if self.normed_connectivity_profile_nb and self.group is not None:
      atts = dict( self.group.hierarchyAttributes() )
      atts[ 'study' ] = self.normed_connectivity_profile_nb[0].get( 'study' )
      atts[ 'texture' ] = self.texture_group
      atts[ 'gyrus' ] = self.normed_connectivity_profile_nb[0].get( 'gyrus' )
      return self.signature[ 'group_connectivity_profile' ].findValue( atts )
  self.signature['normed_connectivity_profiles'].userLevel = 2
  self.linkParameters( 'normed_connectivity_profiles', ( 'group', 
                       'study_name', 'texture_ind', 'patch_label', 
                       'smoothing' ), linkIndividualProfiles )
  self.linkParameters( 'thresholded_connectivity_profile', 
                       'normed_connectivity_profiles' )
  self.linkParameters( 'normed_connectivity_profile_nb', 
                       ( 'thresholded_connectivity_profile', 'texture_group' ), 
                       linkProfiles )
  self.linkParameters( 'group_connectivity_profile', 
                       'normed_connectivity_profile_nb', linkGroupProfiles )

def execution ( self, context ):
  context.write( 'Process Combine All Subjects Mean Connectivity Profile...' )

  '''
  A connectivity profile is determinated on a range of subjects ( for a group of subjects )
  '''

  registerClass( 'minf_2.0', Subject, 'Subject' )
  groupOfSubjects = readMinf( self.group.fullPath() )

  n = 0
  listOfTex = []
  for texture, outtexname in zip( self.thresholded_connectivity_profile, self.normed_connectivity_profile_nb ):
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
      context.write( self.group_connectivity_profile )
      shutil.copyfile( str(tex_filename), str(self.group_connectivity_profile) )
    else:
      context.system('AimsLinearComb',
        '-i', tex_filename,
        '-j', self.group_connectivity_profile,
        '-o', self.group_connectivity_profile
      )
    count += 1
  
  averageTexture = aims.read( self.group_connectivity_profile.fullPath() )
  subjects_nb = len( groupOfSubjects )
  if subjects_nb == 0:
    raise exceptions.ValueError( "subjects_list is empty" )
  for i in xrange( averageTexture.nItem() ):
    val = averageTexture[0][i]
    averageTexture[0][i] = val/subjects_nb
  aims.write( averageTexture, self.group_connectivity_profile.fullPath() )
