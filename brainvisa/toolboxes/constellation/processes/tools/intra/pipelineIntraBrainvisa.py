from brainvisa.processes import *

def validation():
  try:
    import constel
  except:
    raise ValidationError( 'constellation module is not here.' )


name = 'Brainvisa Intra pipeline'
userLevel = 2

signature = Signature(
  #'reorganized_subset_of_tract', ReadDiskItem( 'Gyri Regrouped Subset of Tracts', 'Aims bundles' ),
            'study', String(),
          'texture', String(),
            'gyrus', String(),
          'subject', ReadDiskItem( 'subject', 'directory' ),
  'subset_of_tract', ReadDiskItem( 'Fascicles bundles', 'Aims bundles' ),
     'gyri_texture', ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ),
       'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
         'dw_to_t1', ReadDiskItem( 'Transformation matrix', 'Transformation matrix' ),
        'smoothing', Float(),
)

def initialization( self ):

  eNode = SerialExecutionNode( self.name, parameterized=self )

  ### Bundles Fitering
  eNode.addChild( 'Filter',
                  ProcessExecutionNode( 'bundlesFiltering',
                  optional = 1 ) )

  eNode.addDoubleLink( 'Filter.study',
                       'study' )
  eNode.addDoubleLink( 'Filter.texture',
                       'texture' )
  eNode.addDoubleLink( 'Filter.gyrus',
                       'gyrus' )
  eNode.addDoubleLink( 'Filter.subject',
                       'subject' )
  eNode.addDoubleLink( 'Filter.subset_of_tract',
                       'subset_of_tract' )
  eNode.addDoubleLink( 'Filter.gyri_texture',
                       'gyri_texture' )

  ### Bundles Oversampled
  eNode.addChild( 'ConnectivityCortexMatrix',
                  ProcessExecutionNode( 'fiberOversampler',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ConnectivityCortexMatrix.length_filtered_tracts_distantFibers',
                       'Filter.subsets_of_tracts_distantFibers' )

  ### Connectivity Matrix
  eNode.addChild( 'Smoothing',
                  ProcessExecutionNode( 'createConnectivityMatrix',
                  optional = 1 ) )

  eNode.addDoubleLink( 'Smoothing.oversampled_tracts_distantFibers',
                       'ConnectivityCortexMatrix.oversampled_tracts_distantFibers' )

  eNode.addDoubleLink( 'Smoothing.length_filtered_tracts_fibersNearCortex',
                       'Filter.subsets_of_tracts_FibersNearCortex' )

  #eNode.Smoothing.removeLink( 'gyri_texture',
                              #'oversampled_tracts_distantFibers' )

  eNode.addDoubleLink( 'Smoothing.gyri_texture',
                       'gyri_texture' )
                       
  eNode.addDoubleLink( 'Smoothing.white_mesh',
                       'white_mesh' )
                       
  eNode.addDoubleLink( 'Smoothing.dw_to_t1',
                       'dw_to_t1' )

  ### Sum Sparse Matrix
  eNode.addChild( 'Sum',
                  ProcessExecutionNode( 'sumSparseMatrix',
                  optional = 1 ) )

  eNode.addDoubleLink( 'Sum.connectivity_matrix_fibersNearCortex',
                       'Smoothing.connectivity_matrix_fibersNearCortex' )

  eNode.addDoubleLink( 'Sum.white_mesh',
                       'white_mesh' )

  eNode.addDoubleLink( 'Sum.gyri_texture',
                       'gyri_texture' )
                       
  eNode.addDoubleLink( 'Sum.gyrus',
                       'gyrus' )

  eNode.addDoubleLink( 'Sum.smoothing',
                       'smoothing' )

  ### Mean Connectivity Profile
  eNode.addChild( 'ProfileComputing',
                  ProcessExecutionNode( 'createMeanConnectivityProfile',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ProfileComputing.connectivity_matrix_full',
                       'Sum.connectivity_matrix_full' )

  eNode.addDoubleLink( 'ProfileComputing.gyri_texture',
                       'gyri_texture' )

  ### Normed Smoothed Mean Connectivity Profile
  eNode.addChild( 'ProfileNormalization',
                  ProcessExecutionNode( 'removeInternalConnections',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ProfileNormalization.gyrus_connectivity_profile',
                       'ProfileComputing.gyrus_connectivity_profile' )

  eNode.addDoubleLink( 'ProfileNormalization.gyri_texture',
                       'gyri_texture' )
                       
  eNode.addDoubleLink( 'ProfileNormalization.white_mesh',
                       'white_mesh' )

  ### Watershed
  eNode.addChild( 'Watershed',
                  ProcessExecutionNode( 'watershedReflectingConnectionsToGyrus',
                  optional = 1 ) )

  eNode.addDoubleLink( 'Watershed.norm_connectivity_profile',
                       'ProfileNormalization.norm_connectivity_profile' )

  eNode.addDoubleLink( 'Watershed.white_mesh',
                       'white_mesh' )

  ### Filtered Watershed
  eNode.addChild( 'ConnectivityMatrixToBassins',
                  ProcessExecutionNode( 'filteringWatershed',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ConnectivityMatrixToBassins.connectivity_matrix_full',
                       'ProfileComputing.connectivity_matrix_full' )

  eNode.addDoubleLink( 'ConnectivityMatrixToBassins.gyri_texture',
                       'gyri_texture')

  eNode.addDoubleLink( 'ConnectivityMatrixToBassins.white_mesh',
                       'white_mesh' )

  # Reduced Connectivity Matrix

  eNode.addChild( 'ConnectivityMatrixWatershedToBassins',
                  ProcessExecutionNode( 'createReducedConnectivityMatrix',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ConnectivityMatrixWatershedToBassins.connectivity_matrix_full',
                       'ConnectivityMatrixToBassins.connectivity_matrix_full' )

  eNode.addDoubleLink( 'ConnectivityMatrixWatershedToBassins.gyri_texture',
                       'gyri_texture' )
                       
  eNode.addDoubleLink( 'ConnectivityMatrixWatershedToBassins.white_mesh',
                       'white_mesh' )

  ### Clustering
  eNode.addChild( 'ClusteringIntraSubjects',
                  ProcessExecutionNode( 'ClusteringIntrasubject',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ClusteringIntraSubjects.connectivity_matrix_reduced',
                       'ConnectivityMatrixWatershedToBassins.connectivity_matrix_reduced' )

  eNode.addDoubleLink( 'ClusteringIntraSubjects.gyri_texture',
                       'gyri_texture' )

  eNode.addDoubleLink( 'ClusteringIntraSubjects.white_mesh',
                       'white_mesh' )

  self.setExecutionNode( eNode )



#### 02/03 - Filtering per gyrus
#eNode.addChild( 'PrepareTracts',
                #ProcessExecutionNode( 'filteringPerGyrus',
                #optional = 1 ) )
#eNode.addDoubleLink( 'PrepareTracts.reorganized_subset_of_tract',
                     #'reorganized_subset_of_tract' )
#eNode.addDoubleLink( 'PrepareTracts.gyri_texture',
                     #'gyri_texture' )
#eNode.addDoubleLink( 'PrepareTracts.gyrus',
                     #'gyrus' )
#### 04 - Regroup Fibers From Length
#eNode.addChild( 'TractsReorganisation',
                #ProcessExecutionNode( 'regroupFibersFromLength',
                #optional = 1 ) )
#eNode.addDoubleLink( 'TractsReorganisation.gyrus_tracts_fibersNearCortex',
                     #'PrepareTracts.gyrus_tracts_fibersNearCortex' )
#### 05 - Select Fibers From Length
#eNode.addChild( 'LengthFiltering',
                #ProcessExecutionNode( 'selectFibersFromLength',
                #optional = 1 ) )
#eNode.addDoubleLink( 'LengthFiltering.tracts_by_length_fibersNearCortex',
                     #'TractsReorganisation.tracts_by_length_fibersNearCortex' )
### Delete Intermediate Fibers
#eNode.addChild( 'deleteTracts',
                #ProcessExecutionNode( 'removeUnnecessaryBundles',
                #optional = 1,
                #selected = 0 ) )
#eNode.addDoubleLink( 'deleteTracts.reorganized_subset_of_tract',
                     #'PrepareTracts.reorganized_subset_of_tract' )
#eNode.addDoubleLink( 'deleteTracts.gyrus',
                     #'gyrus' )