from brainvisa.processes import *

def validation():
  try:
    import roca
  except:
    raise ValidationError( 'module roca is not here.' )


name = 'Brainvisa Intra pipeline'
userLevel = 2

signature = Signature(
  'reorganized_subset_of_tract', ReadDiskItem( 'Gyri Regrouped Subset of Tracts', 'Aims bundles' ),
            'gyri_segmentation', ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ),
                   'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
       'diff_to_anat_transform', ReadDiskItem( 'Transformation matrix', 'Transformation matrix' ),
                  'patch_label', Integer(),
                       'smooth', Float(),
)

def initialization( self ):

  eNode = SerialExecutionNode( self.name, parameterized=self )

  ### 02/03 - Filtering per gyrus
  eNode.addChild( 'PrepareTracts',
                  ProcessExecutionNode( 'filteringPerGyrus',
                  optional = 1 ) )

  eNode.addDoubleLink( 'PrepareTracts.reorganized_subset_of_tract',
                       'reorganized_subset_of_tract' )
                       
  eNode.addDoubleLink( 'PrepareTracts.gyri_segmentation',
                       'gyri_segmentation' )
                       
  eNode.addDoubleLink( 'PrepareTracts.patch_label',
                       'patch_label' )

  ### 04 - Regroup Fibers From Length
  eNode.addChild( 'TractsReorganisation',
                  ProcessExecutionNode( 'regroupFibersFromLength',
                  optional = 1 ) )

  eNode.addDoubleLink( 'TractsReorganisation.gyrus_tracts_MeshClosestPoint',
                       'PrepareTracts.gyrus_tracts_MeshClosestPoint' )

  ### 05 - Select Fibers From Length
  eNode.addChild( 'LengthFiltering',
                  ProcessExecutionNode( 'selectFibersFromLength',
                  optional = 1 ) )

  eNode.addDoubleLink( 'LengthFiltering.tracts_by_length_MeshClosestPoint',
                       'TractsReorganisation.tracts_by_length_MeshClosestPoint' )

  ## Delete Intermediate Fibers
  eNode.addChild( 'deleteTracts',
                  ProcessExecutionNode( 'removeUnnecessaryBundles',
                  optional = 1,
                  selected = 0 ) )

  eNode.addDoubleLink( 'deleteTracts.reorganized_subset_of_tract',
                       'PrepareTracts.reorganized_subset_of_tract' )

  eNode.addDoubleLink( 'deleteTracts.patch_label',
                       'patch_label' )

  ### 06 - Bundles Fusion Oversampled
  eNode.addChild( 'ConnectivityCortexMatrix',
                  ProcessExecutionNode( 'fiberOversampler',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ConnectivityCortexMatrix.length_filtered_tracts_MeshIntersectPoint',
                       'LengthFiltering.length_filtered_tracts_MeshIntersectPoint' )

  ### 07 - Connectivity Matrix  Smooothed
  eNode.addChild( 'Smoothing',
                  ProcessExecutionNode( 'createConnectivityMatrix',
                  optional = 1 ) )

  eNode.addDoubleLink( 'Smoothing.oversampled_tracts_MeshIntersectPoint',
                       'ConnectivityCortexMatrix.oversampled_tracts_MeshIntersectPoint' )

  eNode.addDoubleLink( 'Smoothing.length_filtered_tracts_MeshClosestPoint',
                       'LengthFiltering.length_filtered_tracts_MeshClosestPoint' )

  #eNode.Smoothing.removeLink( 'gyri_segmentation',
                              #'oversampled_tracts_MeshIntersectPoint' )

  eNode.addDoubleLink( 'Smoothing.gyri_segmentation',
                       'gyri_segmentation' )
                       
  eNode.addDoubleLink( 'Smoothing.white_mesh',
                       'white_mesh' )
                       
  eNode.addDoubleLink( 'Smoothing.diff_to_anat_transform',
                       'diff_to_anat_transform' )

  ### 08 - Sum Sparse Matrix
  eNode.addChild( 'Sum',
                  ProcessExecutionNode( 'sumSparseMatrix',
                  optional = 1 ) )

  eNode.addDoubleLink( 'Sum.connectivity_matrix_MeshClosestPoint',
                       'Smoothing.connectivity_matrix_MeshClosestPoint' )

  eNode.addDoubleLink( 'Sum.white_mesh',
                       'white_mesh' )

  eNode.addDoubleLink( 'Sum.gyri_segmentation',
                       'gyri_segmentation' )
                       
  eNode.addDoubleLink( 'Sum.patch_label',
                       'patch_label' )

  eNode.addDoubleLink( 'Sum.smooth',
                       'smooth' )

  ### 09 - Mean Connectivity Profile Texture intraSubjects
  eNode.addChild( 'ProfileComputing',
                  ProcessExecutionNode( 'createMeanConnectivityProfile',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ProfileComputing.connectivity_matrix_full',
                       'Sum.connectivity_matrix_full' )

  eNode.addDoubleLink( 'ProfileComputing.gyri_segmentation',
                       'gyri_segmentation' )

  ### 11 - Normed Smoothed Mean Connectivity Profile IntraSubjects
  eNode.addChild( 'ProfileNormalization',
                  ProcessExecutionNode( 'removeInternalConnections',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ProfileNormalization.gyrus_mean_connectivity_profile',
                       'ProfileComputing.gyrus_mean_connectivity_profile' )

  eNode.addDoubleLink( 'ProfileNormalization.gyri_segmentation',
                       'gyri_segmentation' )
                       
  eNode.addDoubleLink( 'ProfileNormalization.white_mesh',
                       'white_mesh' )

  ### 12 - Watershed On Normed Smoothed IntraSubjects
  eNode.addChild( 'Watershed',
                  ProcessExecutionNode( 'watershedReflectingConnectionsToGyrus',
                  optional = 1 ) )

  eNode.addDoubleLink( 'Watershed.norm_mean_connectivity_profile',
                       'ProfileNormalization.norm_mean_connectivity_profile' )

  eNode.addDoubleLink( 'Watershed.white_mesh',
                       'white_mesh' )

  ### 13 - Filtered Watershed On Normed Smoothed IntraSubjects
  eNode.addChild( 'ConnectivityMatrixToBassins',
                  ProcessExecutionNode( 'filteringWatershed',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ConnectivityMatrixToBassins.connectivity_matrix_full',
                       'ProfileComputing.connectivity_matrix_full' )

  eNode.addDoubleLink( 'ConnectivityMatrixToBassins.gyri_segmentation',
                       'gyri_segmentation')

  eNode.addDoubleLink( 'ConnectivityMatrixToBassins.white_mesh',
                       'white_mesh' )

  # 14 - Connectivity Matrix to Watershed Basins IntraSubjects

  eNode.addChild( 'ConnectivityMatrixWatershedToBassins',
                  ProcessExecutionNode( 'createReducedConnectivityMatrix',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ConnectivityMatrixWatershedToBassins.connectivity_matrix_full',
                       'ConnectivityMatrixToBassins.connectivity_matrix_full' )

  eNode.addDoubleLink( 'ConnectivityMatrixWatershedToBassins.gyri_segmentation',
                       'gyri_segmentation' )
                       
  eNode.addDoubleLink( 'ConnectivityMatrixWatershedToBassins.white_mesh',
                       'white_mesh' )

  ### 15 - Clustering IntraSubjects
  eNode.addChild( 'ClusteringIntraSubjects',
                  ProcessExecutionNode( 'ClusteringIntrasubject',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ClusteringIntraSubjects.connectivity_matrix_reduced',
                       'ConnectivityMatrixWatershedToBassins.connectivity_matrix_reduced' )

  eNode.addDoubleLink( 'ClusteringIntraSubjects.gyri_segmentation',
                       'gyri_segmentation' )

  eNode.addDoubleLink( 'ClusteringIntraSubjects.white_mesh',
                       'white_mesh' )

  self.setExecutionNode( eNode )