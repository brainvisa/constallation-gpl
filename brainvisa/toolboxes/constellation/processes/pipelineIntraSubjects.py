from brainvisa.processes import *

def validation():
  try:
    import roca
  except:
    raise ValidationError( 'module roca is not here.' )

name = 'Freesurfer BrainVisa Intra pipeline'
userLevel = 2

signature = Signature(
  'RawT1Image',      ReadDiskItem('Raw T1 MRI', getAllFormats() ),
  'subset_of_tract', ReadDiskItem( 'Fascicles bundles', 'Aims bundles' ),
  'diff_to_anat_transform', ReadDiskItem( 'Transformation matrix', 'Transformation matrix' ),
  'patch_label',     Integer(),
  'study_name', String(),
  'texture_name', String(),
   
)

def initialization( self ):
  
  eNode = SerialExecutionNode( self.name, parameterized=self )
  
  ### Brainvisa Freesurfer pipeline complete
  eNode.addChild( 'FreeSurferPipeline',
                  ProcessExecutionNode( 'freesurferPipelineComplete',
                  optional = 1 ) )  
                  
  eNode.addDoubleLink( 'FreeSurferPipeline.RawT1Image', 
                       'RawT1Image' )
  
  #### Gyri Texture Cleaning
  #eNode.addChild( 'CleaningTexture',
                  #ProcessExecutionNode( 'gyriTextureCleaning',
                  #optional = 1 ) )
  
  #eNode.addDoubleLink( 'CleaningTexture.gyri_segmentation', 
                       #'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatTex.Gyri' )
                       
  #eNode.addDoubleLink( 'CleaningTexture.white_mesh', 
                       #'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatenate.BothWhite' )

  ### 01
  eNode.addChild( 'step01',
                  ProcessExecutionNode( 'selectFibersfromMesh',
                  optional = 1 ) )

  eNode.addDoubleLink( 'step01.study_name',
                       'study_name' )

  eNode.addDoubleLink( 'step01.texture_name',
                       'texture_name' )

  eNode.addDoubleLink( 'step01.subset_of_tract',
                       'subset_of_tract' )

  eNode.addDoubleLink( 'step01.diff_to_anat_transform',
                       'diff_to_anat_transform' )

  eNode.addDoubleLink( 'step01.gyri_segmentation',
                       'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatTex.Gyri' )

  eNode.addDoubleLink( 'step01.white_mesh',
                       'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatenate.BothWhite' )
  
  ### Filtering per gyrus
  eNode.addChild( 'PrepareTracts',
                  ProcessExecutionNode( 'filteringPerGyrus',
                  optional = 1 ) )
  
  eNode.addDoubleLink( 'PrepareTracts.reorganized_subset_of_tract', 
                       'step01.reorganized_subsets_of_tracts' )
  
  eNode.addDoubleLink( 'PrepareTracts.gyri_segmentation', 
                       'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatTex.Gyri' )
  
  eNode.addDoubleLink( 'PrepareTracts.patch_label',
                       'patch_label' )
  
  ### Tracts reorganisation per length
  eNode.addChild( 'TractsReorganisation',
                  ProcessExecutionNode( 'regroupFibersFromLength',
                  optional = 1 ) )
                  
  eNode.addDoubleLink( 'TractsReorganisation.gyrus_tracts_MeshClosestPoint',
                       'PrepareTracts.gyrus_tracts_MeshClosestPoint' )
  
  ### Length filtering
  eNode.addChild( 'LengthFiltering',
                  ProcessExecutionNode( 'selectFibersFromLength',
                  optional = 1 ) )
  
  eNode.addDoubleLink( 'LengthFiltering.tracts_by_length_MeshClosestPoint',
                       'TractsReorganisation.tracts_by_length_MeshClosestPoint' )
  
  ### Tracts Merging/Gyrus tracts oversampling 
  eNode.addChild( 'ConnectivityCortexMatrix',
                  ProcessExecutionNode( 'bundlesFusionOversampled',
                  optional = 1 ) )
                  
  eNode.addDoubleLink( 'ConnectivityCortexMatrix.length_filtered_tracts_MeshIntersectPoint',
                       'LengthFiltering.length_filtered_tracts_MeshIntersectPoint' )
                  
  ### Connectivity Matrix  Smooothed
  eNode.addChild( 'Smoothing',
                  ProcessExecutionNode( 'connectivityMatrixToAllCortex',
                  optional = 1 ) )
  
  eNode.addDoubleLink( 'Smoothing.oversampled_tracts_MeshIntersectPoint',
                       'ConnectivityCortexMatrix.oversampled_tracts_MeshIntersectPoint' )
                       
  eNode.addDoubleLink( 'Smoothing.gyri_segmentation',
                       'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatTex.Gyri' )
                       
  eNode.addDoubleLink( 'Smoothing.white_mesh',
                       'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatenate.BothWhite' )
                       
  eNode.addDoubleLink( 'Smoothing.diff_to_anat_transform',
                       'step01.diff_to_anat_transform' )
  
  ### Sum Sparse Matrix
  eNode.addChild( 'Sum',
                  ProcessExecutionNode( 'sumSparseMatrix',
                  optional = 1 ) )
                  
  eNode.addDoubleLink( 'Sum.connectivity_matrix_MeshClosestPoint',
                       'Smoothing.connectivity_matrix_MeshClosestPoint' )
                       
  
  ### Mean Connectivity Profile Computing intraSubjects
  eNode.addChild( 'ProfileComputing',
                  ProcessExecutionNode( 'meanConnectivityProfileTextureIntraSubjects',
                  optional = 1 ) )
  
  eNode.addDoubleLink( 'ProfileComputing.connectivity_matrix_full',
                       'Sum.connectivity_matrix_full' )
                                     
  eNode.addDoubleLink( 'ProfileComputing.gyri_segmentation',
                       'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatTex.Gyri' )
                       
  eNode.addDoubleLink( 'ProfileComputing.white_mesh',
                       'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatenate.BothWhite' )
  
  ### Mean Connectivity Profile Thresholding IntraSubjects 
  eNode.addChild( 'ProfileThresholding',
                  ProcessExecutionNode( 'connectivityMatrixToAllCortexIntraSubjects',
                  optional = 1 ) )
                  
  eNode.addDoubleLink( 'ProfileThresholding.connectivity_matrix_full',
                       'ProfileComputing.connectivity_matrix_full' )
  
  ### Mean Connectivity Profile Norm/Smooth IntraSubjects  
  eNode.addChild( 'ProfileNormalization',
                  ProcessExecutionNode( 'normedSmoothedMeanConnectivityProfileIntraSubjects',
                  optional = 1 ) )
                  
  eNode.addDoubleLink( 'ProfileNormalization.gyrus_mean_connectivity_profile',
                       'ProfileComputing.gyrus_mean_connectivity_profile' )
                                       
  eNode.addDoubleLink( 'ProfileNormalization.gyri_segmentation',
                       'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatTex.Gyri' )
  
  eNode.addDoubleLink( 'ProfileNormalization.white_mesh',
                       'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatenate.BothWhite' )
  
  ### Compute watershed IntraSubjects  
  eNode.addChild( 'Watershed',
                  ProcessExecutionNode( 'watershedOnNormedSmoothedIntraSubjects',
                  optional = 1 ) )
                  
  eNode.addDoubleLink( 'Watershed.norm_mean_connectivity_profile',
                       'ProfileNormalization.norm_mean_connectivity_profile' )
                       
  eNode.addDoubleLink( 'Watershed.white_mesh',
                       'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatenate.BothWhite' )
                  
  ### Connectivity Matrix to Bassins IntraSubjects  
  eNode.addChild( 'ConnectivityMatrixToBassins',
                  ProcessExecutionNode( 'filteredWatershedOnNormedSmoothedIntraSubjects',
                  optional = 1 ) )
  
  eNode.addDoubleLink( 'ConnectivityMatrixToBassins.connectivity_matrix_full',
                       'ProfileThresholding.connectivity_matrix_full' )
                       
  eNode.addDoubleLink( 'ConnectivityMatrixToBassins.white_mesh',
                       'Watershed.white_mesh' )
                       
  eNode.addDoubleLink( 'ConnectivityMatrixToBassins.gyri_segmentation',
                       'ProfileNormalization.gyri_segmentation')
  
  # 14 - Connectivity Matrix to Watershed Basins IntraSubjects
  
  eNode.addChild( 'ConnectivityMatrixWatershedToBassins',
                  ProcessExecutionNode( 'connectivityMatrixToWatershedBassins',
                  optional = 1 ) )
  
  eNode.addDoubleLink( 'ConnectivityMatrixWatershedToBassins.connectivity_matrix_full', 
                       'ConnectivityMatrixToBassins.connectivity_matrix_full' )
                       
  eNode.addDoubleLink( 'ConnectivityMatrixWatershedToBassins.white_mesh',
                       'ConnectivityMatrixToBassins.white_mesh' ) 
                       
  eNode.addDoubleLink( 'ConnectivityMatrixWatershedToBassins.gyri_segmentation',
                       'ConnectivityMatrixToBassins.gyri_segmentation' )
  
  ### Clustering IntraSubjects 
  eNode.addChild( 'ClusteringIntrasubject',
                  ProcessExecutionNode( 'ClusteringIntrasubject',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ClusteringIntraSubjects.connectivity_matrix_reduced',
                       'ConnectivityMatrixWatershedToBassins.connectivity_matrix_reduced' )
        
  eNode.addDoubleLink( 'ClusteringIntraSubjects.gyri_segmentation',
                       'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatTex.Gyri' )

  eNode.addDoubleLink( 'ClusteringIntraSubjects.white_mesh',
                       'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatenate.BothWhite' )
                       
  self.setExecutionNode( eNode )
  
  
  
  
