# -*- coding: utf-8 -*-

include( 'diffusion' )

Format( 'Matrix sparse', "f|*.imas" )

# Filtered tracts
FileType( 'Gyri Regrouped Subset of Tracts', 'Fascicles bundles' )
FileType( 'Gyrus Subset of Tracts Mesh Closest Point', 'Fascicles bundles' )
FileType( 'Gyrus Subset of Tracts Mesh Intersect Point', 'Fascicles bundles' )
FileType( 'Gyrus Tracts Mesh Closest Point', 'Fascicles bundles' )
FileType( 'Gyrus Tracts Mesh Intersect Point', 'Fascicles bundles' )
FileType( 'Gyrus Regrouped By Length Tracts Mesh Closest Point', 'Fascicles bundles' )
FileType( 'Gyrus Regrouped By Length Tracts Mesh Intersect Point', 'Fascicles bundles' )
FileType( 'Gyrus Length Interval Tracts Mesh Closest Point', 'Fascicles bundles' )
FileType( 'Gyrus Length Interval Tracts Mesh Intersect Point', 'Fascicles bundles' )
FileType( 'Gyrus Tracts Mesh Closest Point 5%', 'Fascicles bundles' )
FileType( 'Gyrus Tracts Mesh Intersect Point 5%', 'Fascicles bundles' )
FileType( 'Gyrus Length Interval Tracts Mesh Closest Point 20%', 'Fascicles bundles' )
FileType( 'Gyrus Length Interval Tracts Mesh Intersect Point 20%', 'Fascicles bundles' )
FileType( 'One FreeSurfer Gyrus Length Interval Tracts To All Cortex', 'Fascicles bundles' )
FileType( 'Gyrus Oversampled Length Interval Tracts Mesh Intersect Point', 'Fascicles bundles' )
FileType( 'Gyri Trash Subset of Tracts', 'Fascicles bundles' )

FileType( 'Vertex Index', 'Text file' )
FileType( 'Full Clustering Result', 'Text file' )
FileType( 'Gyrus Clustering Result', 'Text file' )
FileType( 'Group Clustering Results', 'Text file' )
FileType( 'Bundles Name List associated to One Subset of Tracts', 'Text file' )
FileType( 'List of Fibers Length Mesh Closest Point', 'Text file' )
FileType( 'List of Fibers Length Mesh Intersect Point', 'Text file' )

# Connectivity matrix
FileType( 'One Gyrus Connectivity Matrix Not In Mesh', 'Any type', 'Matrix sparse' )
FileType( 'One Gyrus Connectivity Matrix Near Cortex', 'Any type', 'Matrix sparse' )
FileType( 'One Gyrus Connectivity Matrix All Cortex', 'Any type', 'Matrix sparse' )
FileType( 'Connectivity Matrix All Cortex', 'Any type', 'Matrix sparse' )
FileType( 'One Gyrus Connectivity Matrix Near Cortex Texture', 'BothResampledGyri' )
FileType( 'One Gyrus Connectivity Matrix Not In Mesh Texture', 'BothResampledGyri' )
FileType( 'Gyrus Connectivity Profile', 'BothResampledGyri' )
FileType( 'Patch Connectivity Matrix', '3D volume' )
FileType( 'Normed Connectivity Profile', 'BothResampledGyri' )
FileType( 'Group Normed Connectivity Profile', 'BothResampledGyri' )
FileType( 'Thresholded Connectivity Profile', 'BothResampledGyri' )

FileType( 'Gyrus Connectivity Matrix Mesh Closest Point', 'Any type', 'Matrix sparse' )
FileType( 'Gyrus Connectivity Matrix Mesh Intersect Point', 'Any type', 'Matrix sparse' )
FileType( 'Gyrus Connectivity Profile Mesh Closest Point', 'BothResampledGyri' )
FileType( 'Gyrus Connectivity Profile Mesh Intersect Point', 'BothResampledGyri' )
FileType( 'Gyrus Connectivity Matrix', 'Any type', 'Matrix sparse' )

# Clustering 
FileType( 'One Gyrus Vertex Indexes In Cortex Mesh', 'Text file' )
FileType( 'One Gyrus Smoothed Mean Connectivity Profile Thresholded By Gyrus Texture', 'BothResampledGyri' )
FileType( 'Watershed', 'BothResampledGyri' )
FileType( 'Averaged Watershed', 'BothResampledGyri' )
FileType( 'Filtered Watershed', 'BothResampledGyri' )
FileType( 'Reduced Connectivity Matrix', '3D volume' )
FileType( 'Gyrus Watershed Bassins Fiber Nb Mesh', 'BothResampledGyri' )
FileType( 'Gyrus Watershed Bassins Fiber Nb', 'BothResampledGyri' )
FileType( 'Patch Clustering Kmedoids Time', 'BothResampledGyri' )
FileType( 'patch Clustering Vertex Silhouette Width Time', 'BothResampledGyri' )
FileType( 'Patch Clustering Silhouette Width Time', 'BothResampledGyri' )
FileType( 'Clustering Time', 'BothResampledGyri' )
FileType( 'Clustering kOpt', 'BothResampledGyri' )
FileType( 'Mean Connectivity Profile Mask', 'BothResampledGyri' ),
FileType( 'Averaged Connectivity Profile', 'BothResampledGyri' ),
FileType( 'thresh AllSubjects', 'BothResampledGyri' ),
FileType( 'Averaged Normed Connectivity Profile', 'BothResampledGyri' ),
FileType( 'smoothNorm AllSubjects', 'BothResampledGyri' ),
FileType( 'Group Reduced Connectivity Matrix', '3D volume' )
FileType( 'Averaged Filtered Watershed', 'BothResampledGyri' )
FileType( 'Averaged Thresholded Connectivity Profile', 'BothResampledGyri' )
FileType( 'Group Matrix', '3D volume' )
FileType( 'Group Clustering Kopt', 'BothResampledGyri' )
FileType( 'Group Clustering Time', 'BothResampledGyri' )
FileType( 'Group Clustering Silhouette', 'BothResampledGyri' )

#group
#FileType( 'Brainvisa Group definition', 'Group definition', 'XML')
#FileType( 'Connectivity Inter Clustering Time', 'BothResampledGyri' )
#FileType( 'Connectivity Optimal Inter Clustering', 'BothResampledGyri' )
#FileType( 'Clustering Silhouette Width Inter Time', 'BothResampledGyri' )
#FileType( 'Mean connectivity profile normed', 'BothResampledGyri' )
#FileType( 'Average Inter Clustering Time', 'BothResampledGyri' )
#FileType( 'Average Optimal Inter Clustering', 'BothResampledGyri' )
#FileType( 'Average Inter Time', 'BothResampledGyri' )
#FileType( 'Clustering Vertex Silhouette Width Inter Time', 'BothResampledGyri' )
