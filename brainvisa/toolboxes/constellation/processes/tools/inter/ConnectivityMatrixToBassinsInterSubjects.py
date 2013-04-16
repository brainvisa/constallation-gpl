# -*- coding: utf-8 -*-
from brainvisa.processes import *
from brainvisa.group_utils import Subject
from soma.minf.api import registerClass, readMinf

name = '05 - Connectivity Matrix Reduced'
userLevel = 2

signature = Signature(
                'study_name', String(),
                'texture_in', String(),
               'texture_out', String(),
               'patch_label', Integer(),
                     'group', ReadDiskItem('Group definition', 'XML' ),
        'filtered_watershed', ReadDiskItem( 'Averaged Filtered Watershed', 'Aims texture formats' ),
  'individual_matrix_sparse', ListOf( ReadDiskItem( 'Gyrus Connectivity Matrix', 'Matrix sparse' ) ),
              'average_mesh', ReadDiskItem( 'BothAverageBrainWhite', 'BrainVISA mesh formats' ),
         'gyri_segmentation', ListOf( ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ) ),
              'vertex_index', ListOf( ReadDiskItem( 'Vertex Index', 'Text file' ) ),
                
  'connectivity_matrix_reduced', ListOf( WriteDiskItem( 'Group Reduced Connectivity Matrix', 'GIS image' ) ),
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
        profiles.append( WriteDiskItem( 'Gyrus Connectivity Matrix', 'Matrix sparse' ).findValue( { 'protocol': proto, 'study': study, 'texture': texture, 'gyrus': gyrus }, subject.attributes() ) )
      return profiles
  def linkProfiles( self, dummy ):
    if self.individual_matrix_sparse and self.group is not None:
      profiles = []
      i = 0
      for p in self.individual_matrix_sparse:
        atts = dict( self.group.hierarchyAttributes() )
        atts[ 'study' ] = self.individual_matrix_sparse[i].get( 'study' )
        atts[ 'texture' ] = self.texture_out
        atts[ 'gyrus' ] = self.individual_matrix_sparse[i].get( 'gyrus' )
        atts[ 'subject' ] = self.individual_matrix_sparse[i].get( 'subject' )
        profiles.append( WriteDiskItem( 'Group Reduced Connectivity Matrix', 'GIS image' ).findValue( atts ) )
        i += 1
      return profiles
  self.linkParameters( 'individual_matrix_sparse', ( 'group', 'study_name', 'texture_in', 'patch_label' ), linkIndividualProfiles )
  self.linkParameters( 'filtered_watershed', ( 'group', 'patch_label', 'texture_out' ) )
  self.linkParameters( 'connectivity_matrix_reduced', ( 'group','individual_matrix_sparse', 'texture_out') , linkProfiles )
  self.linkParameters( 'vertex_index', 'individual_matrix_sparse')
  self.signature['individual_matrix_sparse'].userLevel = 2

def execution ( self, context ):
  context.write( 'starting step 3.8 : Connectivity matrix to targets from matrix... ' )
  '''
  Connectivity Matrices reduction according to a parcellated white mesh texture.
  The reduced connectivity profiles of all subjects are normalized using L2 norm.
  '''
  registerClass('minf_2.0', Subject, 'Subject')
  groupOfSubjects = readMinf(self.group.fullPath())

  context.write( 'Reducing connectivity matrices.' )
  
  listReducedMatrix = []
  n = 0
  g = 0
  for matrix in self.individual_matrix_sparse:
    print '--------------------------------'
    print n
    print matrix
    print self.vertex_index[n]
    print self.gyri_segmentation[g]
    print self.connectivity_matrix_reduced[n]
    print '--------------------------------'
    context.system( "testConnMatrixToTargetsFromMatrix",
      '-mesh', self.average_mesh,
      '-connmatrixfile', matrix,
      '-connfmt', 'binar_sparse',
      '-targetregionstex', self.filtered_watershed,
      '-seedregionstex', self.gyri_segmentation[g],
      '-seedlabel', self.patch_label,
      '-connmatrix', self.connectivity_matrix_reduced[n],
      '-type', 'seedVertex_to_targets',
      '-seedvertexindex', self.vertex_index[n],
      '-normalize', 1,
    )
    listReducedMatrix.append( self.connectivity_matrix_reduced[n] )
    n += 1
    if len(self.gyri_segmentation) == 1:
      g = 0
    else:
      g += 1
  listReducedMatrix = self.connectivity_matrix_reduced
  context.write( 'OK' )