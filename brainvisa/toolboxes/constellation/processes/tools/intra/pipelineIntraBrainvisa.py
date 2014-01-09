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
  eNode.addChild( 'Oversampler',
                  ProcessExecutionNode( 'fiberOversampler',
                  optional = 1 ) )

  eNode.addDoubleLink( 'Oversampler.filtered_length_distant_fibers',
                       'Filter.subsets_of_distant_fibers' )

  ### Connectivity Matrix
  eNode.addChild( 'ConnectivityMatrix',
                  ProcessExecutionNode( 'createConnectivityMatrix',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ConnectivityMatrix.oversampled_distant_fibers',
                       'Oversampler.oversampled_distant_fibers' )

  eNode.addDoubleLink( 'ConnectivityMatrix.filtered_length_fibers_near_cortex',
                       'Filter.subsets_of_fibers_near_cortex' )

  #eNode.ConnectivityMatrix.removeLink( 'gyri_texture',
                              #'oversampled_tracts_distantFibers' )

  eNode.addDoubleLink( 'ConnectivityMatrix.gyri_texture',
                       'gyri_texture' )
                       
  eNode.addDoubleLink( 'ConnectivityMatrix.white_mesh',
                       'white_mesh' )
                       
  eNode.addDoubleLink( 'ConnectivityMatrix.dw_to_t1',
                       'Filter.dw_to_t1' )

  ### Sum Sparse Matrix
  eNode.addChild( 'Smoothing',
                  ProcessExecutionNode( 'sumSparseMatrix',
                  optional = 1 ) )

  eNode.addDoubleLink( 'Smoothing.matrix_of_fibers_near_cortex',
                       'ConnectivityMatrix.matrix_of_fibers_near_cortex' )

  eNode.addDoubleLink( 'Smoothing.white_mesh',
                       'white_mesh' )

  eNode.addDoubleLink( 'Smoothing.gyri_texture',
                       'gyri_texture' )
                       
  eNode.addDoubleLink( 'Smoothing.gyrus',
                       'gyrus' )

  eNode.addDoubleLink( 'Smoothing.smoothing',
                       'smoothing' )

  ### Mean Connectivity Profile
  eNode.addChild( 'MeanProfile',
                  ProcessExecutionNode( 'createMeanConnectivityProfile',
                  optional = 1 ) )

  eNode.addDoubleLink( 'MeanProfile.complete_connectivity_matrix',
                       'Smoothing.complete_connectivity_matrix' )

  eNode.addDoubleLink( 'MeanProfile.gyri_texture',
                       'gyri_texture' )

  ### Normed Smoothed Mean Connectivity Profile
  eNode.addChild( 'InternalConnections',
                  ProcessExecutionNode( 'removeInternalConnections',
                  optional = 1 ) )

  eNode.addDoubleLink( 'InternalConnections.patch_connectivity_profile',
                       'MeanProfile.patch_connectivity_profile' )

  eNode.addDoubleLink( 'InternalConnections.gyri_texture',
                       'gyri_texture' )
                       
  eNode.addDoubleLink( 'InternalConnections.white_mesh',
                       'white_mesh' )

  ### Watershed
  eNode.addChild( 'Watershed',
                  ProcessExecutionNode( 'watershedReflectingConnectionsToGyrus',
                  optional = 1 ) )

  eNode.addDoubleLink( 'Watershed.normed_connectivity_profile',
                       'InternalConnections.normed_connectivity_profile' )

  eNode.addDoubleLink( 'Watershed.white_mesh',
                       'white_mesh' )

  ### Filtered Watershed
  eNode.addChild( 'FilteringWatershed',
                  ProcessExecutionNode( 'filteringWatershed',
                  optional = 1 ) )

  eNode.addDoubleLink( 'FilteringWatershed.watershed',
                       'Watershed.watershed' )
  
  eNode.addDoubleLink( 'FilteringWatershed.complete_connectivity_matrix',
                       'MeanProfile.complete_connectivity_matrix' )

  eNode.addDoubleLink( 'FilteringWatershed.gyri_texture',
                       'gyri_texture')

  eNode.addDoubleLink( 'FilteringWatershed.white_mesh',
                       'white_mesh' )

  # Reduced Connectivity Matrix

  eNode.addChild( 'ReducedMatrix',
                  ProcessExecutionNode( 'createReducedConnectivityMatrix',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ReducedMatrix.complete_connectivity_matrix',
                       'FilteringWatershed.complete_connectivity_matrix' )

  eNode.addDoubleLink( 'ReducedMatrix.gyri_texture',
                       'gyri_texture' )
                       
  eNode.addDoubleLink( 'ReducedMatrix.white_mesh',
                       'white_mesh' )

  ### Clustering
  eNode.addChild( 'ClusteringIntraSubjects',
                  ProcessExecutionNode( 'ClusteringIntrasubject',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ClusteringIntraSubjects.reduced_connectivity_matrix',
                       'ReducedMatrix.reduced_connectivity_matrix' )

  eNode.addDoubleLink( 'ClusteringIntraSubjects.gyri_texture',
                       'gyri_texture' )

  eNode.addDoubleLink( 'ClusteringIntraSubjects.white_mesh',
                       'white_mesh' )

  self.setExecutionNode( eNode )