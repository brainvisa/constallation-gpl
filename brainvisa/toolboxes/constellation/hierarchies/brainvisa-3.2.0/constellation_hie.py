# -*- coding: utf-8 -*-
include( 'diffusion' )

insert( '{center}/{subject}/diffusion/{acquisition}/{analysis}/{tracking_session}',
  'connectivity_parcellation', SetContent(

   '{study}', SetContent(

      '{texture}', SetContent(
        'IntraClusteringResultsFull', SetType( 'Full Clustering Result' ),

          '{gyrus}', SetContent(
            'VertexIndex', SetType( 'Vertex Index' ),
            
              'filteredTracts', SetContent(
                '<subject>_<texture>_<gyrus>_outsideFibersOfCortex_{minlengthoffibersOut}to500mm_oversampled', SetType( 'Oversampled Fibers' ),
                '<subject>_<texture>_<gyrus>_fibersNearCortex_{minlengthoffibersIn}to500mm', SetType( 'Fibers Near Cortex' ),
                '<subject>_<texture>_<gyrus>_outsideFibersOfCortex_{minlengthoffibersOut}to500mm', SetType( 'Very OutSide Fibers Of Cortex' ),
              ),
    
              'matrix', SetContent(
                '<subject>_<texture>_<gyrus>_connectivityMatrix_fibersNearCortex', SetType( 'Connectivity Matrix Fibers Near Cortex' ),
                '<subject>_<texture>_<gyrus>_connectivityMatrix_outsideFibersOfCortex', SetType( 'Connectivity Matrix Outside Fibers Of Cortex' ),
                '<subject>_<texture>_<gyrus>_meanConnectivityProfile_fibersNearCortex', SetType( 'Connectivity Profile Fibers Near Cortex' ),
                '<subject>_<texture>_<gyrus>_meanConnectivityProfile_outsideFibersOfCortex', SetType( 'Connectivity Profile Outside Fibers Of Cortex' ),
                '<subject>_<texture>_<gyrus>_connectivityMatrix', SetType( 'Gyrus Connectivity Matrix' ),
              ),
  
              'clustering', SetContent(
                '<subject>_<texture>_<gyrus>_meanConnectivityProfile', SetType( 'Gyrus Connectivity Profile' ),
                '<subject>_<texture>_<gyrus>_thresholdedMeanConnectivityProfile', SetType( 'Thresholded Connectivity Profile' ),
                '<subject>_<texture>_<gyrus>_normedMeanConnectivityProfile', SetType( 'Normed Connectivity Profile' ),
                '<subject>_<texture>_<gyrus>_sumValuesFromRegion', SetType( 'Sum Values From Region'),
                '<subject>_<texture>_<gyrus>_spreadValueOnRegion', SetType( 'Spread Value On Region'),
                '<subject>_<texture>_<gyrus>_watershed', SetType( 'Watershed Texture'),
                '<subject>_<texture>_<gyrus>_filteredWatershed', SetType( 'Filtered Watershed' ),
                '<subject>_<texture>_<gyrus>_reducedConnectivityMatrix', SetType( 'Reduced Connectivity Matrix'),
                '<subject>_<texture>_<gyrus>_patchClusteringKmedoidsTime', SetType( 'Patch Clustering Time' ),
                '<subject>_<texture>_<gyrus>_patchClusteringSilhouetteWidthTime', SetType( 'Clustering Silhouette Time' ),
                '<subject>_<texture>_<gyrus>_patchClusteringVertexSilhouetteWidthTime', SetType( 'Clustering Vertex Silhouette Time' ),
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
 
insert( '{center}/group_analysis/{group_of_subjects}',
  'connectivity_clustering', SetContent(

    '{study}', SetContent(
    
      '{texture}', SetContent(
        '<group_of_subjects>_<study>_<texture>_clusteringResults', SetType( 'Group Clustering Results' ),
        
          '{gyrus}', SetContent(
            '<group_of_subjects>_<study>_<texture>_<gyrus>_mask', SetType( 'Avg Connectivity Mask' ),
            '<group_of_subjects>_<study>_<texture>_<gyrus>_meanConnectivityProfile', SetType( 'Avg Connectivity Profile' ),
            '<group_of_subjects>_<study>_<texture>_<gyrus>_thresholdedMeanConnectivityProfile', SetType( 'Avg Thresholded Connectivity Profile' ),
            '<group_of_subjects>_<study>_<texture>_<gyrus>_normedMeanConnectivityProfile', SetType( 'Avg Normed Connectivity Profile' ),
            '<group_of_subjects>_<study>_<texture>_<gyrus>_watershed', SetType( 'Avg Watershed Texture'),
            '<group_of_subjects>_<study>_<texture>_<gyrus>_filteredWatershed', SetType( 'Avg Filtered Watershed' ),
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
