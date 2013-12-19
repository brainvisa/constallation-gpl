from brainvisa.processes import *

def validation():
  try:
    import constel
  except:
    raise ValidationError( 'constellation module is not here.' )


name = 'Brainvisa Constellation Intra pipeline'
userLevel = 2

signature = Signature(
            'study', String(),
          'texture', String(),
            'gyrus', String(),
         'database', Choice(),
          'subject', ReadDiskItem( 'subject', 'directory' ),
     'gyri_texture', ReadDiskItem( 'FreesurferResampledBothParcellationType', 'Aims texture formats' ),
       'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
        'smoothing', Float(),
)

def initialization( self ):
  databases=[h.name for h in neuroHierarchy.hierarchies() if h.fso.name == 'brainvisa-3.2.0']
  self.signature['database'].setChoices(*databases)
  if len( databases ) != 0:
    self.database=databases[0]
  else:
    self.signature[ 'database' ] = OpenChoice()
 
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
  eNode.addDoubleLink( 'Filter.database',
                       'database' )
  eNode.addDoubleLink( 'Filter.subject',
                       'subject' )
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
                       'Filter.dw_to_t1' )

  ### Sum Sparse Matrix
  eNode.addChild( 'Sum',
                  ProcessExecutionNode( 'sumSparseMatrix',
                  optional = 1 ) )

  eNode.addDoubleLink( 'Sum.matrix_fibersNearCortex',
                       'Smoothing.matrix_fibersNearCortex' )

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

  eNode.addDoubleLink( 'ProfileComputing.complete_connectivity_matrix',
                       'Sum.complete_connectivity_matrix' )

  eNode.addDoubleLink( 'ProfileComputing.gyri_texture',
                       'gyri_texture' )

  ### Normed Smoothed Mean Connectivity Profile
  eNode.addChild( 'ProfileNormalization',
                  ProcessExecutionNode( 'removeInternalConnections',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ProfileNormalization.patch_connectivity_profile',
                       'ProfileComputing.patch_connectivity_profile' )

  eNode.addDoubleLink( 'ProfileNormalization.gyri_texture',
                       'gyri_texture' )
                       
  eNode.addDoubleLink( 'ProfileNormalization.white_mesh',
                       'white_mesh' )

  ### Watershed
  eNode.addChild( 'Watershed',
                  ProcessExecutionNode( 'watershedReflectingConnectionsToGyrus',
                  optional = 1 ) )

  eNode.addDoubleLink( 'Watershed.normed_connectivity_profile',
                       'ProfileNormalization.normed_connectivity_profile' )

  eNode.addDoubleLink( 'Watershed.white_mesh',
                       'white_mesh' )

  ### Filtered Watershed
  eNode.addChild( 'ConnectivityMatrixToBassins',
                  ProcessExecutionNode( 'filteringWatershed',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ConnectivityMatrixToBassins.complete_connectivity_matrix',
                       'ProfileComputing.complete_connectivity_matrix' )

  eNode.addDoubleLink( 'ConnectivityMatrixToBassins.gyri_texture',
                       'gyri_texture')

  eNode.addDoubleLink( 'ConnectivityMatrixToBassins.white_mesh',
                       'white_mesh' )

  # Reduced Connectivity Matrix

  eNode.addChild( 'ConnectivityMatrixWatershedToBassins',
                  ProcessExecutionNode( 'createReducedConnectivityMatrix',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ConnectivityMatrixWatershedToBassins.complete_connectivity_matrix',
                       'ConnectivityMatrixToBassins.complete_connectivity_matrix' )

  eNode.addDoubleLink( 'ConnectivityMatrixWatershedToBassins.gyri_texture',
                       'gyri_texture' )
                       
  eNode.addDoubleLink( 'ConnectivityMatrixWatershedToBassins.white_mesh',
                       'white_mesh' )

  ### Clustering
  eNode.addChild( 'ClusteringIntraSubjects',
                  ProcessExecutionNode( 'ClusteringIntrasubject',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ClusteringIntraSubjects.reduced_connectivity_matrix',
                       'ConnectivityMatrixWatershedToBassins.reduced_connectivity_matrix' )

  eNode.addDoubleLink( 'ClusteringIntraSubjects.gyri_texture',
                       'gyri_texture' )

  eNode.addDoubleLink( 'ClusteringIntraSubjects.white_mesh',
                       'white_mesh' )

  self.setExecutionNode( eNode )