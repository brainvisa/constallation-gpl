# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path
from brainvisa.group_utils import Subject
from soma.minf.api import registerClass, readMinf
from soma.functiontools import partial

def validation():
  if not find_in_path( 'constelConnectionDensityTexture' ):
    raise ValidationError( 'constellation module is not here.' )

name = 'Reduced Connectivity Matrix'
userLevel = 2

signature = Signature(
  'study_name', String(),
  'texture_ind', String(),
  'texture_group', String(),
  'patch_label', Integer(),
  'smoothing', Float(),
  'group', ReadDiskItem('Group definition', 'XML' ),
  'filtered_watershed', ReadDiskItem( 'Avg Filtered Watershed', 
                                      'Aims texture formats' ),
  'complete_connectivity_matrix', ListOf( 
                                  ReadDiskItem( 'Gyrus Connectivity Matrix', 
                                                'Matrix sparse' ) 
                                  ),
  'average_mesh', ReadDiskItem( 'BothAverageBrainWhite', 
                                'BrainVISA mesh formats' ),
  'gyri_texture', ListOf( 
                       ReadDiskItem( 'FreesurferResampledBothParcellationType', 
                                     'Aims texture formats' ) ),
  'reduced_connectivity_matrix', ListOf( 
                                 WriteDiskItem( 'Group Reduced Connectivity Matrix',
                                                'GIS image' ) ),
)

def linkGyri( self, key, value ):
  if self.gyri_texture:
    eNode = self.executionNode()
    isnode = [ x == key for x in eNode.childrenNames() ]
    ind = isnode.index( True )
    if len( self.gyri_texture ) <= ind:
      ind = len( self.gyri_texture ) - 1
    return self.gyri_texture[ ind ]


def afterChildAddedCallback( self, parent, key, child ):
  # Set default values
  child.removeLink( 'filtered_watershed', 'complete_connectivity_matrix' )
  child.removeLink( 'reduced_connectivity_matrix', 'filtered_watershed' )

  child.signature[ 'filtered_watershed' ] \
    = parent.signature[ 'filtered_watershed' ]
  child.signature[ 'white_mesh' ] = parent.signature[ 'average_mesh' ]
  child.signature[ 'reduced_connectivity_matrix' ] \
    = WriteDiskItem( 'Group Reduced Connectivity Matrix', 'GIS image' )

  child.gyrus = parent.patch_label
  child.smoothing = parent.smoothing
  child.filtered_watershed = parent.filtered_watershed
  child.white_mesh = parent.average_mesh

  print 'key:', key
  print 'self:', self
  print 'parent:', parent
  print 'child:', child
  ## Add link between eNode.ListOf_Input_3dImage and pNode.Input_3dImage
  parent.addLink( key + '.filtered_watershed', 'filtered_watershed' )
  parent.addLink( key + '.gyrus', 'patch_label' )
  #parent.addLink( key + '.smoothing', 'smoothing' )
  parent.addLink( key + '.white_mesh', 'average_mesh' )
  parent.addLink( key + '.gyri_texture', 'gyri_texture',
    partial( self.linkGyri, key ) )


def beforeChildRemovedCallback( self, parent, key, child ):
  parent.removeLink( key + '.filtered_watershed', 'filtered_watershed' )
  parent.removeLink( key + '.gyrus', 'patch_label' )
  #parent.removeLink( key + '.smoothing', 'smoothing' )
  parent.removeLink( key + '.white_mesh', 'average_mesh' )
  parent.remove( key + '.gyri_texture', 'gyri_texture' )


def initialization ( self ):
  def linkIndividualMatrices( self, dummy ):
    if self.group is not None:
      registerClass('minf_2.0', Subject, 'Subject')
      groupOfSubjects = readMinf(self.group.fullPath())
      profiles = []
      for subject in groupOfSubjects:
        study = self.study_name
        texture = self.texture_ind
        gyrus = 'G' + str(self.patch_label)
        smoothing = 'smoothing' + str(self.smoothing)
        profile = ReadDiskItem( 'Gyrus Connectivity Matrix', 
                                'Matrix sparse' ).findValue( { 'study': study, 
                                'texture': texture, 'gyrus': gyrus, 
                                'smoothing' : smoothing }, 
                                subject.attributes() 
                              )
        if profile is not None:
          profiles.append( profile )
      return profiles
  def linkProfiles( self, dummy ):
    if self.complete_connectivity_matrix and self.group is not None:
      profiles = []
      for p in self.complete_connectivity_matrix:
        if p is None:
          continue
        atts = dict( self.group.hierarchyAttributes() )
        atts[ 'study' ] = p.get( 'study' )
        atts[ 'texture' ] = self.texture_group
        atts[ 'gyrus' ] = p.get( 'gyrus' )
        atts[ 'subject' ] = p.get( 'subject' )
        profiles.append( WriteDiskItem( 'Group Reduced Connectivity Matrix', 
                                        'GIS image' ).findValue( atts ) )
      return profiles
  def linkWatershed( self, dummy ):
    if self.group is not None and self.patch_label and self.texture_group \
        and self.study_name:
      atts = self.group.hierarchyAttributes()
      atts[ 'texture' ] = self.texture_group
      atts[ 'gyrus' ] = 'G' + str(self.patch_label)
      atts[ 'study' ] = self.study_name
      atts[ 'smoothing' ] = 'smoothing' + str(self.smoothing)
      return ReadDiskItem( 'Averaged Filtered Watershed', 
                           'Aims texture formats' ).findValue( atts )
  def linkMesh( self, dummy ):
    if self.group is not None:
      atts = { 'freesurfer_group_of_subjects' : 
               self.group.get( 'group_of_subjects' ) }
      return self.signature[ 'average_mesh' ].findValue( atts )

  self.linkParameters( 'complete_connectivity_matrix', ( 'group', 
                       'study_name', 'texture_ind', 'patch_label', 
                       'smoothing' ), linkIndividualMatrices 
                     )
  self.linkParameters( 'filtered_watershed', ( 'group', 'patch_label', 
                       'texture_group', 'study_name', 'smoothing' ), 
                       linkWatershed 
                     )
  self.linkParameters( 'reduced_connectivity_matrix', ( 'group', 
                       'complete_connectivity_matrix', 'texture_group'), 
                       linkProfiles 
                     )
  self.linkParameters( 'average_mesh', 'group', linkMesh )
  self.signature['complete_connectivity_matrix'].userLevel = 2

  eNode = ParallelExecutionNode( 'Reduced_connectivity_matrix',
                                 parameterized = self,
                                 possibleChildrenProcesses = [ 'createReducedConnectivityMatrix' ],
                                 notify = True )
  self.setExecutionNode( eNode )

  # Add callback to warn about child add and remove
  eNode.afterChildAdded.add(\
    ExecutionNode.MethodCallbackProxy( self.afterChildAddedCallback ) )
  eNode.beforeChildRemoved.add(\
    ExecutionNode.MethodCallbackProxy( self.beforeChildRemovedCallback ) )
  #eNode.afterChildRemoved.add(\
    #ExecutionNode.MethodCallbackProxy( self.afterChildRemovedCallback ) )

  # Add links to refresh child nodes when main lists are modified
  eNode.addLink( None,
                 'complete_connectivity_matrix',
                 partial( brainvisa.processes.mapValuesToChildrenParameters,
                          eNode,
                          eNode,
                          'complete_connectivity_matrix',
                          'complete_connectivity_matrix',
                          defaultProcess = 'createReducedConnectivityMatrix',
                          name='createReducedConnectivityMatrix' ) )

  eNode.addLink( None,
                 'reduced_connectivity_matrix',
                 partial( brainvisa.processes.mapValuesToChildrenParameters,
                          eNode,
                          eNode,
                          'reduced_connectivity_matrix',
                          'reduced_connectivity_matrix',
                          defaultProcess = 'createReducedConnectivityMatrix',
                          name='createReducedConnectivityMatrix' ) )

  #eNode.addLink( None,
                 #'gyri_texture',
                 #partial( brainvisa.processes.mapValuesToChildrenParameters,
                          #eNode,
                          #eNode,
                          #'gyri_texture',
                          #'gyri_texture',
                          #defaultProcess = 'createReducedConnectivityMatrix',
                          #name='createReducedConnectivityMatrix' ) )

