# -*- coding: utf-8 -*-
from brainvisa.processes import *
from brainvisa.group_utils import Subject
from soma.minf.api import registerClass, readMinf
from soma.path import find_in_path

def validation():
  if not find_in_path('constelInterSubjectClustering.py'):
    raise ValidationError( 'constellation module is not here.' )

name = 'Clustering of Group'
userLevel = 2

signature = Signature(
  'study_name', String(),
  'texture_ind', String(),
  'texture_group', String(),
  'patch_label', Integer(),
  'smoothing', Float(),
  'group', ReadDiskItem('Group definition', 'XML' ),
  'study', Choice( 'Average', 'Concatenate' ),
  'reduced_connectivity_matrix', ListOf( 
                               ReadDiskItem( 'Group Reduced Connectivity Matrix', 
                                             'GIS image' ) ),
  'gyri_texture', ListOf( 
                       ReadDiskItem( 'FreesurferResampledBothParcellationType', 
                                     'Aims texture formats' ) ),
  'average_mesh', ReadDiskItem( 'BothAverageBrainWhite', 
                                'BrainVISA mesh formats' ),
  #'areaMin_threshold', Integer(),
  'kmax', Integer(),
  'group_matrix', WriteDiskItem( 'Group Matrix', 'GIS image'),
  #'clustering_silhouette', ListOf( WriteDiskItem( 'Group Clustering Silhouette', 'BrainVISA texture formats' ) ),
  'clustering_time', ListOf( WriteDiskItem( 'Group Clustering Time', 
                                            'BrainVISA texture formats' ) ),
  #'clustering_Kopt', ListOf( WriteDiskItem( 'Group Clustering Kopt', 'BrainVISA texture formats' ) ),
  #'clustering_results', WriteDiskItem( 'Group Clustering Results', 'Text file' ),
)

def initialization ( self ):
  #self.areaMin_threshold = 400
  self.kmax = 10
  self.study = 'Average'
  def linkIndividual( self, dummy ):
    if self.group is not None:
      registerClass('minf_2.0', Subject, 'Subject')
      groupOfSubjects = readMinf(self.group.fullPath())
      profiles = []
      for subject in groupOfSubjects:
        atts = dict( self.group.hierarchyAttributes() )
        atts[ 'study' ] = self.study_name
        atts[ 'texture' ] = self.texture_group
        atts[ 'gyrus' ] = 'G' + str(self.patch_label)
        atts['smoothing'] = 'smoothing' + str(self.smoothing)
        profiles.append( ReadDiskItem( 'Group Reduced Connectivity Matrix', 
                         'GIS image' ).findValue( subject.attributes(), atts ) )
      return profiles
  def linkMatrix( self, dummy ):
    if self.group is not None:
      atts = dict( self.group.hierarchyAttributes() )
      atts[ 'study' ] = self.study_name
      atts[ 'texture' ] = self.texture_group
      atts[ 'gyrus' ] = 'G' + str(self.patch_label)
      atts['smoothing'] = 'smoothing' + str(self.smoothing)
      filename = self.signature['group_matrix'].findValue( atts )
      return filename
  def linkClustering(self, dummy):
    if self.reduced_connectivity_matrix and self.group is not None:
      if self.study == 'Average':
        atts = dict( self.group.hierarchyAttributes() )
        atts['subject'] = 'avgSubject'
        atts[ 'study' ] = self.study_name
        atts[ 'texture' ] = self.texture_group
        atts[ 'gyrus' ] = 'G' + str(self.patch_label)
        atts['smoothing'] = 'smoothing' + str(self.smoothing)
        print atts
        return self.signature[ 'clustering_time' ].findValue( atts )
      elif self.study == 'Concatenate':
        registerClass('minf_2.0', Subject, 'Subject')
        groupOfSubjects = readMinf(self.group.fullPath())
        profiles = []
        for subject in groupOfSubjects:
          atts = dict( self.group.hierarchyAttributes() )
          atts['subject'] = self.reduced_connectivity_matrix
          atts[ 'study' ] = self.study_name
          atts[ 'texture' ] = self.texture_group
          atts[ 'gyrus' ] = 'G' + str(self.patch_label)
          atts['smoothing'] = 'smoothing' + str(self.smoothing)
          profiles.append( ReadDiskItem('Group Clustering Time', 
                           'BrainVISA texture formats').findValue( atts ) )
        return profiles
  #self.signature['reduced_connectivity_matrix'].userLevel = 2
  self.linkParameters( 'reduced_connectivity_matrix', ('group', 'study_name', 
                       'texture_group', 'patch_label', 'smoothing'), linkIndividual )
  self.linkParameters( 'group_matrix', ('group', 'study_name', 'texture_group', 
                       'patch_label', 'smoothing' ), linkMatrix )
  self.linkParameters( 'clustering_time', ('group', 'study_name', 
                       'reduced_connectivity_matrix', 'texture_group', 'patch_label', 
                       'smoothing'), linkClustering )
  #self.linkParameters( 'clustering_time', 'clustering_silhouette' )
  #self.linkParameters( 'clustering_Kopt', 'clustering_time' )
  #self.linkParameters( 'clustering_results', 'group_matrix' )

def execution ( self, context ):
  context.write( '--> Clustering inter subjects...' )
  '''
  The gyrus vertices connectivity profiles of all the subjects are concatenated into a big matrix. The clustering is performed with the classical kmedoids algorithm and the Euclidean distance between profiles as dissimilarity measure.
  '''
  registerClass('minf_2.0', Subject, 'Subject')
  groupOfSubjects = readMinf(self.group.fullPath())

  patch_label = os.path.basename( os.path.basename( os.path.basename( 
                os.path.dirname( os.path.dirname( 
                self.reduced_connectivity_matrix[0].fullPath() ) ) ) ) )
  patch_label = patch_label.strip('G')
  patch_label = self.patch_label
  context.write(patch_label)
  args = []
  for x in self.reduced_connectivity_matrix:
    args += [ '-m', x ]
  args += [ '-o', self.group_matrix, '-s', self.study ]
  context.system('python', find_in_path( 'constelCalculateGroupMatrix.py' ),
   *args
  )
  
  #Rclustering_filename = os.path.join( os.path.dirname( mainPath ), 'R', 'clustering', 'kmedoids.R' )

  cmd_args = []
  for t in self.clustering_time:
    cmd_args += [ '-p', t ]
  #for k in self.clustering_Kopt:
    #cmd_args += [ '-q', k ]
  #for s in self.clustering_silhouette:
    #cmd_args += [ '-o', s ]
  for y in self.gyri_texture:
    cmd_args += [ '-t', y ]
  #cmd_args += [ '-m', self.average_mesh, '-l', patch_label, '-a', self.areaMin_threshold, '-s',
#self.study, '-g', self.group_matrix, '-x', self.clustering_results, '-r', Rclustering_filename ]
  cmd_args += [ '-m', self.average_mesh, '-l', patch_label, '-s', self.study, 
                '-g',self.group_matrix, '-a', self.kmax ]
  context.system( 'python', find_in_path('constelInterSubjectClustering.py'),
    *cmd_args
  )
  context.write( 'Done' )