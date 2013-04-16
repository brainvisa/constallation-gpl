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
FileType( 'Gyrus Connectivity Profile', 'Label Texture' )
FileType( 'Patch Connectivity Matrix', '3D volume' )
FileType( 'Normed Connectivity Profile', 'Label Texture' )
FileType( 'Group Normed Connectivity Profile', 'Label Texture' )
FileType( 'Thresholded Connectivity Profile', 'Label Texture' )

FileType( 'Gyrus Connectivity Matrix Mesh Closest Point', 'Any type', 'Matrix sparse' )
FileType( 'Gyrus Connectivity Matrix Mesh Intersect Point', 'Any type', 'Matrix sparse' )
FileType( 'Gyrus Connectivity Profile Mesh Closest Point', 'Label Texture' )
FileType( 'Gyrus Connectivity Profile Mesh Intersect Point', 'Label Texture' )
FileType( 'Gyrus Connectivity Matrix', 'Any type', 'Matrix sparse' )

# Clustering 
FileType( 'One Gyrus Vertex Indexes In Cortex Mesh', 'Text file' )
FileType( 'One Gyrus Smoothed Mean Connectivity Profile Thresholded By Gyrus Texture', 'Label Texture' )
FileType( 'Watershed', 'Label Texture' )
FileType( 'Averaged Watershed', 'Label Texture' )
FileType( 'Filtered Watershed', 'Label Texture' )
FileType( 'Reduced Connectivity Matrix', '3D volume' )
FileType( 'Gyrus Watershed Bassins Fiber Nb Mesh', 'Label Texture' )
FileType( 'Gyrus Watershed Bassins Fiber Nb', 'Label Texture' )
FileType( 'Patch Clustering Kmedoids Time', 'Label Texture' )
FileType( 'patch Clustering Vertex Silhouette Width Time', 'Label Texture' )
FileType( 'Patch Clustering Silhouette Width Time', 'Label Texture' )
FileType( 'Clustering Time', 'Label Texture' )
FileType( 'Clustering kOpt', 'Label Texture' )
FileType( 'Mean Connectivity Profile Mask', 'Label Texture' ),
FileType( 'Averaged Connectivity Profile', 'Label Texture' ),
FileType( 'thresh AllSubjects', 'Label Texture' ),
FileType( 'Averaged Normed Connectivity Profile', 'Label Texture' ),
FileType( 'smoothNorm AllSubjects', 'Label Texture' ),
FileType( 'Group Reduced Connectivity Matrix', '3D volume' )
FileType( 'Averaged Filtered Watershed', 'Label Texture' )
FileType( 'Averaged Thresholded Connectivity Profile', 'Label Texture' )
FileType( 'Group Matrix', '3D volume' )
FileType( 'Group Clustering Kopt', 'Label Texture' )
FileType( 'Group Clustering Time', 'Label Texture' )
FileType( 'Group Clustering Silhouette', 'Label Texture' )

#group
#FileType( 'Brainvisa Group definition', 'Group definition', 'XML')
#FileType( 'Connectivity Inter Clustering Time', 'Label Texture' )
#FileType( 'Connectivity Optimal Inter Clustering', 'Label Texture' )
#FileType( 'Clustering Silhouette Width Inter Time', 'Label Texture' )
#FileType( 'Mean connectivity profile normed', 'Label Texture' )
#FileType( 'Average Inter Clustering Time', 'Label Texture' )
#FileType( 'Average Optimal Inter Clustering', 'Label Texture' )
#FileType( 'Average Inter Time', 'Label Texture' )
#FileType( 'Clustering Vertex Silhouette Width Inter Time', 'Label Texture' )
