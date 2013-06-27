# -*- coding: utf-8 -*-

include( 'diffusion' )

Format( 'Matrix sparse', "f|*.imas" )

# Filtered tracts
FileType( 'Gyrus Length Interval Tracts Fibers Near Cortex', 'Fascicles bundles' )
FileType( 'Gyrus Length Interval Tracts Distant Fibers', 'Fascicles bundles' )
FileType( 'Gyrus Oversampled Length Interval Tracts Distant Fibers', 'Fascicles bundles' )

FileType( 'Vertex Index', 'Text file' )
FileType( 'Full Clustering Result', 'Text file' )
FileType( 'Gyrus Clustering Result', 'Text file' )
FileType( 'Group Clustering Results', 'Text file' )

# Connectivity matrix
FileType( 'Gyrus Connectivity Profile', 'Label Texture' )
FileType( 'Patch Connectivity Matrix', '3D volume' )
FileType( 'Normed Connectivity Profile', 'Label Texture' )
FileType( 'Group Normed Connectivity Profile', 'Label Texture' )
FileType( 'Thresholded Connectivity Profile', 'Label Texture' )

FileType( 'Gyrus Connectivity Matrix Fibers Near Cortex', 'Any type', 'Matrix sparse' )
FileType( 'Gyrus Connectivity Matrix Distant Fibers', 'Any type', 'Matrix sparse' )
FileType( 'Gyrus Connectivity Profile Fibers Near Cortex', 'Label Texture' )
FileType( 'Gyrus Connectivity Profile Distant Fibers', 'Label Texture' )
FileType( 'Gyrus Connectivity Matrix', 'Any type', 'Matrix sparse' )

# Clustering
FileType( 'Watershed', 'Label Texture' )
FileType( 'Averaged Watershed', 'Label Texture' )
FileType( 'Filtered Watershed', 'Label Texture' )
FileType( 'Reduced Connectivity Matrix', '3D volume' )
FileType( 'Gyrus Watershed Bassins Fiber Nb Mesh', 'Label Texture' )
FileType( 'Gyrus Watershed Bassins Fiber Nb', 'Label Texture' )
FileType( 'Patch Clustering Kmedoids Time', 'Label Texture' )
FileType( 'Patch Clustering Vertex Silhouette Width Time', 'Label Texture' )
FileType( 'Patch Clustering Silhouette Width Time', 'Label Texture' )
FileType( 'Clustering Texture', 'Label Texture' )
FileType( 'Clustering Time', 'Clustering Texture' )
FileType( 'Clustering kOpt', 'Clustering Texture' )
FileType( 'Mean Connectivity Profile Mask', 'Label Texture' ),
FileType( 'Averaged Connectivity Profile', 'Label Texture' ),
FileType( 'Averaged Normed Connectivity Profile', 'Label Texture' ),
FileType( 'Group Reduced Connectivity Matrix', '3D volume' )
FileType( 'Averaged Filtered Watershed', 'Label Texture' )
FileType( 'Averaged Thresholded Connectivity Profile', 'Label Texture' )
FileType( 'Group Matrix', '3D volume' )
FileType( 'Group Clustering Kopt', 'Label Texture' )
FileType( 'Group Clustering Time', 'Label Texture' )
FileType( 'Group Clustering Silhouette', 'Label Texture' )
