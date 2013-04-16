# -*- coding: utf-8 -*-
from brainvisa.processes import *
from brainvisa.group_utils import Subject
from soma.minf.api import registerClass, readMinf
from soma.path import find_in_path

def validation():
  try:
    import roca
  except:
    raise ValidationError( 'module roca is not here.' )

name = '06 - Clustering of Group'
userLevel = 2

signature = Signature(
                 'study_name', String(),
                 'texture_in', String(),
                'texture_out', String(),
                'patch_label', Integer(),
                      'group', ReadDiskItem('Group definition', 'XML' ),
  'individual_reduced_matrix', ListOf( ReadDiskItem( 'Group Reduced Connectivity Matrix', 'GIS image' ) ),
          'gyri_segmentation', ListOf( ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ) ),
               'average_mesh', ReadDiskItem( 'BothAverageBrainWhite', 'BrainVISA mesh formats' ),
          'areaMin_threshold', Integer(),
               'vertex_index', ListOf( ReadDiskItem( 'Vertex Index', 'Text file' ) ),
                      'study', Choice( 'Average', 'Concatenate' ),

           'group_matrix', WriteDiskItem( 'Group Matrix', 'GIS image'),
  'clustering_silhouette', ListOf( WriteDiskItem( 'Group Clustering Silhouette', 'Aims texture formats' ) ),
        'clustering_time', ListOf( WriteDiskItem( 'Group Clustering Time', 'Aims texture formats' ) ),
        'clustering_Kopt', ListOf( WriteDiskItem( 'Group Clustering Kopt', 'Aims texture formats' ) ),
     'clustering_results', WriteDiskItem( 'Group Clustering Results', 'Text file' ),
)

def initialization ( self ):
  self.areaMin_threshold = 400
  self.study = 'Average'
  def linkIndividual( self, dummy ):
    if self.group is not None:
      registerClass('minf_2.0', Subject, 'Subject')
      groupOfSubjects = readMinf(self.group.fullPath())
      profiles = []
      for subject in groupOfSubjects:
        atts = dict( self.group.hierarchyAttributes() )
        atts[ 'study' ] = self.study_name
        atts[ 'texture' ] = self.texture_out
        atts[ 'gyrus' ] = 'G' + str(self.patch_label)
        profiles.append( ReadDiskItem( 'Group Reduced Connectivity Matrix', 'GIS image' ).findValue( subject.attributes(), atts ) )
      return profiles
  def linkTxt( self, dummy ):
    if self.group is not None:
      registerClass('minf_2.0', Subject, 'Subject')
      groupOfSubjects = readMinf(self.group.fullPath())
      vertexf = []
      for subject in groupOfSubjects:
        proto = 'subjects'
        study = self.study_name
        texture = self.texture_in
        gyrus = 'G' + str(self.patch_label)
        vertexf.append( ReadDiskItem( 'Vertex Index', 'Text file' ).findValue( { 'protocol': proto, 'study': study, 'texture': texture, 'gyrus': gyrus }, subject.attributes() ) )
      return vertexf
  def linkMatrix( self, dummy ):
    if self.group is not None:
      atts = dict( self.group.hierarchyAttributes() )
      atts[ 'study' ] = self.study_name
      atts[ 'texture' ] = self.texture_out
      atts[ 'gyrus' ] = 'G' + str(self.patch_label)
      print atts
      filename = self.signature['group_matrix'].findValue( atts )
      return filename
  #self.signature['individual_reduced_matrix'].userLevel = 2
  self.linkParameters( 'individual_reduced_matrix', 'group', linkIndividual )
  self.linkParameters( 'vertex_index', ('group', 'study_name', 'texture_in', 'patch_label' ), linkTxt )
  self.linkParameters( 'group_matrix', ('group', 'study_name', 'texture_out', 'patch_label' ), linkMatrix )
  self.linkParameters( 'clustering_silhouette', 'individual_reduced_matrix' )
  self.linkParameters( 'clustering_time', 'clustering_silhouette' )
  self.linkParameters( 'clustering_Kopt', 'clustering_time' )
  self.linkParameters( 'clustering_results', 'group_matrix' )

def execution ( self, context ):
  context.write( '--> Clustering inter subjects...' )
  '''
  The gyrus vertices connectivity profiles of all the subjects are concatenated into a big matrix. The clustering is performed with the classical kmedoids algorithm and the Euclidean distance between profiles as dissimilarity measure.
  '''
  registerClass('minf_2.0', Subject, 'Subject')
  groupOfSubjects = readMinf(self.group.fullPath())

  patch_label = os.path.basename( os.path.dirname( os.path.dirname( self.individual_reduced_matrix[0].fullPath() ) ) )
  patch_label = patch_label.strip('G')
  context.write(patch_label)
  args = []
  for x in self.individual_reduced_matrix:
    args += [ '-m', x ]
  args += [ '-o', self.group_matrix, '-s', self.study ]
  context.system('python', find_in_path( 'calculateMatrixGroup.py' ),
   *args
  )
  
  Rclustering_filename = os.path.join( os.path.dirname( mainPath ), 'R', 'clustering', 'kmedoids.R' )

  cmd_args = []
  for t in self.clustering_time:
    cmd_args += [ '-p', t ]
  for k in self.clustering_Kopt:
    cmd_args += [ '-q', k ]
  for s in self.clustering_silhouette:
    cmd_args += [ '-o', s ]
  for y in self.gyri_segmentation:
    cmd_args += [ '-t', y ]
  for v in self.vertex_index:
    cmd_args += [ '-v', v ]
  cmd_args += [ '-m', self.average_mesh, '-l', patch_label, '-a', self.areaMin_threshold, '-s', self.study, '-g', self.group_matrix, '-x', self.clustering_results, '-r', Rclustering_filename ]
  context.system( 'python', find_in_path('clusteringIntersubjects.py'),
    *cmd_args
  )

  context.write( 'OK' )