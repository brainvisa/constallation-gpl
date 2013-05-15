from brainvisa.processes import *

def validation():
  try:
    import constel
  except:
    raise ValidationError( 'constellation module is not here.' )

name = 'Freesurfer BrainVisa + Constellation Inter pipeline'
userLevel = 2


#signature = Signature(
  #'list_of_subjects',ListOf ( ReadDiskItem("Subject", 'Directory') ),
  ##'group_definition_FS', ReadDiskItem('Group definition', 'XML' ),
  ##'group_definition_BV', ReadDiskItem('Group definition', 'XML' ),
  #'gyri_segmentation', ReadDiskItem( 'BothResampledGyri', 'Texture' ),
#)

#def initialization( self ):

  #eNode = SerialExecutionNode( self.name, parameterized=self )

  #### Average Mesh FreeSurfer
  ##eNode.addChild( 'average01',
                  ##ProcessExecutionNode( 'freesurferCreateGroup',
                  ##optional = 1 ) )

  ##eNode.addDoubleLink( 'average01.list_of_subjects',
                       ##'list_of_subjects' )

  ##eNode.addDoubleLink( 'average01.group_definition',
                       ##'group_definition_FS' )

  ##eNode.addChild( 'average02',
                  ##ProcessExecutionNode( 'freesurferMeanMesh',
                  ##optional = 1 ) )

  ##eNode.addDoubleLink( 'average02.group',
                       ##'average01.group_definition' )

  #### Create of group BrainVisa
  ##eNode.addChild( 'groupBV',
                  ##ProcessExecutionNode( 'createGroup',
                  ##optional = 1 ) )

  ##eNode.addDoubleLink( 'groupBV.list_of_subjects',
                       ##'list_of_subjects' )

  ##eNode.addDoubleLink( 'groupBV.group_definition',
                       ##'group_definition_BV' )
  
  ### 01 Surface With Enough Connections Creation InterSubjects
  #eNode.addChild( 'meanProfileInter',
                  #ProcessExecutionNode( 'surfaceWithEnoughConnectionsCreation',
                  #optional = 1 ) )
  
  #eNode.addDoubleLink( 'meanProfileInter.group',
                       #'groupBV.group_definition' )
  
  ### 02 Combine All Subjects Mean Conectivity Profile
  #eNode.addChild( 'combineMeanInter',
                  #ProcessExecutionNode( 'combineAllSubjectsMeanConnProfile',
                  #optional = 1 ) )
  
  #eNode.addDoubleLink( 'combineMeanInter.group',
                       #'meanProfileInter.group' )
  
  ### 03 Thresholding Average Mean Connectivity Profile
  #eNode.addChild( 'meanInter',
                  #ProcessExecutionNode( 'thresholdingAverageMeanConnectivityProfile',
                  #optional = 1 ) )
  
  #eNode.addDoubleLink( 'meanInter.mean_connectivity_profile_texture_mask',
                       #'meanProfileInter.mean_connectivity_profile_texture_mask' )
                       
  #eNode.addDoubleLink( 'meanInter.mean_connectivity_profile_all',
                       #'combineMeanInter.mean_connectivity_profile_all' )
  
  ### 04 Watershed On Normed Smoothed InterSubjects
  #eNode.addChild( 'watershedInter',
                  #ProcessExecutionNode( 'watershedInterSubjects',
                  #optional = 1 ) )
                  
  #eNode.addDoubleLink( 'watershedInter.average_mesh',
                       #'average02.BothAverageMesh' )
  
  #eNode.addDoubleLink( 'watershedInter.normed_thresholded_mean_connectivity_profile',
                       #'meanInter.norm_thresholded_mean_connectivity_profile' )
  
  ### 05 Connectivity Matrix to Watershed Bassins InterSubjects
  #eNode.addChild( 'connMatrixBasinInter',
                  #ProcessExecutionNode( 'ConnectivityMatrixToBassinsInterSubjects',
                  #optional = 1 ) )

  #eNode.addDoubleLink( 'connMatrixBasinInter.group',
                       #'combineMeanInter.group' )

  #eNode.addDoubleLink( 'connMatrixBasinInter.average_mesh',
                       #'watershedInter.average_mesh' )
                       
  #eNode.addDoubleLink( 'connMatrixBasinInter.gyri_segmentation',
                       #'gyri_segmentation' )
                       
  #eNode.addDoubleLink( 'connMatrixBasinInter.filtered_watershed_basins',
                       #'watershedInter.filtered_watershed_basins' )
  
  ### 06 Clustering InterSubjects
  #eNode.addChild( 'clusteringInter',
                  #ProcessExecutionNode( 'ClusteringInterSubjects',
                  #optional = 1 ) )

  #eNode.addDoubleLink( 'clusteringInter.group',
                       #'connMatrixBasinInter.group' )


  #eNode.addDoubleLink( 'clusteringInter.average_mesh',
                       #'connMatrixBasinInter.average_mesh' )

  #eNode.addDoubleLink( 'clusteringInter.gyri_segmentation',
                       #'connMatrixBasinInter.gyri_segmentation' )
  
  #self.setExecutionNode( eNode )
  