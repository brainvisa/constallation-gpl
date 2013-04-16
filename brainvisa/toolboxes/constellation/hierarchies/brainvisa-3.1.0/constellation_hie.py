# -*- coding: utf-8 -*-
include( 'diffusion' )

insert( '{protocol}/{subject}/diffusion/{acquisition}/{analysis}/{tracking_session}',
  'connectivity_parcellation', SetContent(
    '{study}', SetContent(
      '{texture}', SetContent(
        '<subject>_<texture>_{trackingfileindex}_{maxnumberoffile}', SetType(  'Gyri Regrouped Subset of Tracts' ),
        '<subject>_<texture>_{trackingfileindex}_{maxnumberoffile}_bundlesNames', SetType(  'Bundles Name List associated to One Subset of Tracts' ),
        '<subject>_<texture>_trash_{trackingfileindex}_{maxnumberoffile}', SetType(  'Gyri Trash Subset of Tracts' ),
        'IntraClusteringResultsFull', SetType( 'Full Clustering Result' ),
          '{gyrus}', SetContent(
            'VertexIndex', SetType( 'Vertex Index' ),
              'filteredTracts', SetContent(
                '<subject>_<texture>_<gyrus>_MeshClosestPoint_regroupFromLength_5%', SetType( 'Gyrus Tracts Mesh Closest Point 5%' ),
                '<subject>_<texture>_<gyrus>_MeshIntersectPoint_regroupFromLength_5%', SetType( 'Gyrus Tracts Mesh Intersect Point 5%' ),
                '<subject>_<texture>_<gyrus>_MeshClosestPoint_60to500mm_20%', SetType( 'Gyrus Length Interval Tracts Mesh Closest Point 20%' ),
                '<subject>_<texture>_<gyrus>_MeshIntersectPoint_20to500mm_20%', SetType( 'Gyrus Length Interval Tracts Mesh Intersect Point 20%' ),
                '<subject>_<texture>_<gyrus>_MeshIntersectPoint_20to500mm_oversampled', SetType( 'Gyrus Oversampled Length Interval Tracts Mesh Intersect Point' ),
                '<subject>_<texture>_<gyrus>_MeshClosestPoint_{trackingfileindex}_{maxnumberoffile}', SetType( 'Gyrus Subset of Tracts Mesh Closest Point' ),
                '<subject>_<texture>_<gyrus>_MeshIntersectPoint_{trackingfileindex}_{maxnumberoffile}', SetType( 'Gyrus Subset of Tracts Mesh Intersect Point' ),
                '<subject>_<texture>_<gyrus>_MeshClosestPoint_full', SetType( 'Gyrus Tracts Mesh Closest Point' ),
                '<subject>_<texture>_<gyrus>_MeshIntersectPoint_full', SetType( 'Gyrus Tracts Mesh Intersect Point' ),
                '<subject>_<texture>_<gyrus>_MeshClosestPoint_fiberslength', SetType( 'List of Fibers Length Mesh Closest Point' ),
                '<subject>_<texture>_<gyrus>_MeshIntersectPoint_fiberslength', SetType( 'List of Fibers Length Mesh Intersect Point' ),
                '<subject>_<texture>_<gyrus>_MeshClosestPoint_regroupFromLength', SetType( 'Gyrus Regrouped By Length Tracts Mesh Closest Point' ),
                '<subject>_<texture>_<gyrus>_MeshIntersectPoint_regroupFromLength', SetType( 'Gyrus Regrouped By Length Tracts Mesh Intersect Point' ),
                '<subject>_<texture>_<gyrus>_MeshClosestPoint_60to500mm', SetType( 'Gyrus Length Interval Tracts Mesh Closest Point' ),
                '<subject>_<texture>_<gyrus>_MeshIntersectPoint_20to500mm', SetType( 'Gyrus Length Interval Tracts Mesh Intersect Point' ),
                '<subject>_<texture>_<gyrus>_AllFiber_regroupFromLength', SetType( 'One FreeSurfer Gyrus Length Interval Tracts To All Cortex' ),
              ),
    
              'matrix', SetContent(
                'connMatrixMeshClosestPoint', SetType( 'Gyrus Connectivity Matrix Mesh Closest Point' ),
                'connMatrixMeshIntersectPoint', SetType( 'Gyrus Connectivity Matrix Mesh Intersect Point' ),
                'meanConnProfileMeshClosestPoint', SetType( 'Gyrus Connectivity Profile Mesh Closest Point' ),
                'meanConnProfileMeshIntersectPoint', SetType( 'Gyrus Connectivity Profile Mesh Intersect Point' ),
                'connectivity_matrix', SetType( 'Gyrus Connectivity Matrix' ),
              ),
  
              'clustering', SetContent(
                'meanConnectivityProfile_<gyrus>_<study>', SetType( 'Gyrus Connectivity Profile' ),
                'thresholdedByPatchMeanConnectivityProfile_<gyrus>_<study>', SetType( 'Thresholded Connectivity Profile' ),
                'normMeanConnectivityProfile_<gyrus>_<study>', SetType( 'Normed Connectivity Profile' ),
                'watershedBasinsFiberNb_mesh_<gyrus>_<study>', SetType( 'Gyrus Watershed Bassins Fiber Nb Mesh'),
                'watershedBasinsFiberNb_<gyrus>_<study>', SetType( 'Gyrus Watershed Bassins Fiber Nb'),
                'watershedOnMeanConnectivityProfile_<gyrus>_<study>', SetType( 'Watershed'),
                'filteredWatershedBasins_<gyrus>_<study>', SetType( 'Filtered Watershed' ),
                'reducedConnectivityMatrix_<gyrus>_<study>', SetType( 'Reduced Connectivity Matrix'),
                'patchClusteringKmedoidsTime_<gyrus>_<study>', SetType( 'Patch Clustering Kmedoids Time' ),
                'patchClusteringSilhouetteWidthTime_<gyrus>_<study>', SetType( 'Patch Clustering Silhouette Width Time' ),
                'patchClusteringVertexSilhouetteWidthTime_<gyrus>_<study>', SetType( 'Patch Clustering Vertex Silhouette Width Time' ),
                'clusteringKopt_<gyrus>_<study>', SetType( 'Clustering kOpt' ),
                'clusteringTime_<gyrus>_<study>', SetType( 'Clustering Time' ),
                'patchConnectivityMatrix_<gyrus>_<study>', SetType( 'Patch Connectivity Matrix' ),
                'IntraClusteringResults_<gyrus>', SetType( 'Gyrus Clustering Result' ),
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
