# -*- coding: utf-8 -*-
include( 'diffusion' )

insert( '{protocol}/{subject}/diffusion/{acquisition}/{analysis}/{tracking_session}',
  'connectivity_parcellation', SetContent(
    '{study}', SetContent(
      '{texture}', SetContent(
        'IntraClusteringResultsFull', SetType( 'Full Clustering Result' ),
          '{gyrus}', SetContent(
            'VertexIndex', SetType( 'Vertex Index' ),
              'filteredTracts', SetContent(
                '<subject>_<texture>_<gyrus>_distantFibers_{minlengthoffibersOut}to500mm_oversampled', SetType( 'Gyrus Oversampled Length Interval Tracts Distant Fibers' ),
                '<subject>_<texture>_<gyrus>_fibersNearCortex_{minlengthoffibersIn}to500mm', SetType( 'Gyrus Length Interval Tracts Fibers Near Cortex' ),
                '<subject>_<texture>_<gyrus>_distantFibers_{minlengthoffibersOut}to500mm', SetType( 'Gyrus Length Interval Tracts Distant Fibers' ),
              ),
    
              'matrix', SetContent(
                '<subject>_<texture>_<gyrus>_connectivityMatrix_fibersNearCortex', SetType( 'Gyrus Connectivity Matrix Fibers Near Cortex' ),
                '<subject>_<texture>_<gyrus>_connectivityMatrix_distantFibers', SetType( 'Gyrus Connectivity Matrix Distant Fibers' ),
                '<subject>_<texture>_<gyrus>_meanConnectivityProfile_fibersNearCortex', SetType( 'Gyrus Connectivity Profile Fibers Near Cortex' ),
                '<subject>_<texture>_<gyrus>_meanConnectivityProfile_distantFibers', SetType( 'Gyrus Connectivity Profile Distant Fibers' ),
                '<subject>_<texture>_<gyrus>_connectivityMatrix', SetType( 'Gyrus Connectivity Matrix' ),
              ),
  
              'clustering', SetContent(
                '<subject>_<texture>_<gyrus>_meanConnectivityProfile', SetType( 'Gyrus Connectivity Profile' ),
                '<subject>_<texture>_<gyrus>_thresholdedMeanConnectivityProfile', SetType( 'Thresholded Connectivity Profile' ),
                '<subject>_<texture>_<gyrus>_normedMeanConnectivityProfile', SetType( 'Normed Connectivity Profile' ),
                '<subject>_<texture>_<gyrus>_sumValuesFromRegion', SetType( 'Gyrus Watershed Bassins Fiber Nb Mesh'),
                '<subject>_<texture>_<gyrus>_spreadValueOnRegion', SetType( 'Gyrus Watershed Bassins Fiber Nb'),
                '<subject>_<texture>_<gyrus>_watershed', SetType( 'Watershed'),
                '<subject>_<texture>_<gyrus>_filteredWatershed', SetType( 'Filtered Watershed' ),
                '<subject>_<texture>_<gyrus>_reducedConnectivityMatrix', SetType( 'Reduced Connectivity Matrix'),
                '<subject>_<texture>_<gyrus>_patchClusteringKmedoidsTime', SetType( 'Patch Clustering Kmedoids Time' ),
                '<subject>_<texture>_<gyrus>_patchClusteringSilhouetteWidthTime', SetType( 'Patch Clustering Silhouette Width Time' ),
                '<subject>_<texture>_<gyrus>_patchClusteringVertexSilhouetteWidthTime', SetType( 'Patch Clustering Vertex Silhouette Width Time' ),
                '<subject>_<texture>_<gyrus>_clusteringKopt', SetType( 'Clustering kOpt' ),
                '<subject>_<texture>_<gyrus>_clusteringTime', SetType( 'Clustering Time' ),
                '<subject>_<texture>_<gyrus>_patchConnectivityMatrix', SetType( 'Patch Connectivity Matrix' ),
                '<subject>_<texture>_<gyrus>_IntraClusteringResults', SetType( 'Gyrus Clustering Result' ),
              ),
          ),
      ),
    ),
  ),
)
 
insert( '{protocol}/group_analysis/{group_of_subjects}',
  'connectivity_clustering', SetContent(
    '{study}', SetContent(
      '{texture}', SetContent(
        '<group_of_subjects>_<study>_<texture>_clusteringResults', SetType( 'Group Clustering Results' ),
          '{gyrus}', SetContent(
            '<group_of_subjects>_<study>_<texture>_<gyrus>_mask', SetType( 'Mean Connectivity Profile Mask' ),
            '<group_of_subjects>_<study>_<texture>_<gyrus>_meanConnectivityProfile', SetType( 'Averaged Connectivity Profile' ),
            '<group_of_subjects>_<study>_<texture>_<gyrus>_thresholdedMeanConnectivityProfile', SetType( 'Averaged Thresholded Connectivity Profile' ),
            '<group_of_subjects>_<study>_<texture>_<gyrus>_normedMeanConnectivityProfile', SetType( 'Averaged Normed Connectivity Profile' ),
            '<group_of_subjects>_<study>_<texture>_<gyrus>_watershed', SetType( 'Averaged Watershed'),
            '<group_of_subjects>_<study>_<texture>_<gyrus>_filteredWatershed', SetType( 'Averaged Filtered Watershed' ),
            '<group_of_subjects>_<study>_<texture>_<gyrus>_matrix', SetType( 'Group Matrix' ),
            
            '{subject}', SetContent(
              '<group_of_subjects>_<study>_<texture>_<gyrus>_<subject>_ConnectivityProfile_nb_normed', SetType( 'Group Normed Connectivity Profile' ),
              '<group_of_subjects>_<study>_<texture>_<gyrus>_<subject>_reducedMatrix', SetType( 'Group Reduced Connectivity Matrix'),
              '<group_of_subjects>_<study>_<texture>_<gyrus>_<subject>_clusteringKopt', SetType( 'Group Clustering Kopt' ),
              '<group_of_subjects>_<study>_<texture>_<gyrus>_<subject>_clusteringTime', SetType( 'Group Clustering Time' ),
              '<group_of_subjects>_<study>_<texture>_<gyrus>_<subject>_clusteringSilhouette', SetType( 'Group Clustering Silhouette' ),
            ),
          ),
      ),
    ),
  ),
)
