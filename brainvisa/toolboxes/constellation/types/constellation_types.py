# -*- coding: utf-8 -*-

include( 'diffusion' )

Format( 'Matrix sparse', "f|*.imas" )

# Bundles
FileType( 'Bundles selection', 'Fascicles bundles' )
FileType( 'Fibers Near Cortex', 'Bundles selection' )
FileType( 'Very OutSide Fibers Of Cortex', 'Bundles selection' )
FileType( 'Oversampled Fibers', 'Bundles selection' )

# File
FileType( 'Full Clustering Result', 'Text file' )
FileType( 'Gyrus Clustering Result', 'Text file' )
FileType( 'Group Clustering Results', 'Text file' )

# Volume
FileType( 'Connectivity Matrix Volume', '3D volume' )
FileType( 'Group Connectivity Matrix Volume', 'Connectivity Matrix Volume' )

FileType( 'Patch Connectivity Matrix', 'Connectivity Matrix Volume' )
FileType( 'Reduced Connectivity Matrix', 'Connectivity Matrix Volume' )

FileType( 'Group Reduced Connectivity Matrix', 'Group Connectivity Matrix Volume' )
FileType( 'Group Matrix', 'Group Connectivity Matrix Volume' )

FileType( 'Connectivity Matrix Fibers Near Cortex', 'Any type', 'Matrix sparse' )
FileType( 'Connectivity Matrix Outside Fibers Of Cortex', 'Any type', 'Matrix sparse' )
FileType( 'Gyrus Connectivity Matrix', 'Any type', 'Matrix sparse' )

# Connectivity matrix (texture)
FileType( 'Connectivity Profile Texture', 'Label Texture' )
FileType( 'Connectivity Profile Selection', 'Connectivity Profile Texture' )
FileType( 'Group Connectivity Profile Texture',  'Connectivity Profile Texture' )
FileType( 'Avg Connectivity Profile Texture',  'Connectivity Profile Texture' )

FileType( 'Normed Connectivity Profile', 'Connectivity Profile Texture' )
FileType( 'Thresholded Connectivity Profile', 'Connectivity Profile Texture' )
FileType( 'Gyrus Connectivity Profile', 'Connectivity Profile Texture' )

FileType( 'Connectivity Profile Fibers Near Cortex', 'Connectivity Profile Selection' )
FileType( 'Connectivity Profile Outside Fibers Of Cortex', 'Connectivity Profile Selection' )

FileType( 'Group Normed Connectivity Profile', 'Group Connectivity Profile Texture' )
FileType( 'Avg Connectivity Mask', 'Avg Connectivity Profile Texture' )
FileType( 'Avg Connectivity Profile', 'Avg Connectivity Profile Texture' )
FileType( 'Avg Thresholded Connectivity Profile', 'Avg Connectivity Profile Texture' )
FileType( 'Avg Normed Connectivity Profile', 'Avg Connectivity Profile Texture' )

# Watershed (texture)
FileType( 'ROI Texture', 'Label Texture' )
FileType( 'Watershed Texture', 'ROI Texture' )
FileType( 'Watershed Measures', 'ROI Texture' )
FileType( 'Avg Watershed Texture', 'ROI Texture' )

FileType( 'Filtered Watershed', 'ROI Texture' )
FileType( 'Sum Values From Region', 'Watershed Measures' )
FileType( 'Spread Value On Region', 'Watershed Measures' )

FileType( 'Avg Watershed Texture', 'ROI Texture' )
FileType( 'Avg Filtered Watershed', 'Avg Watershed Texture' )

# Clustering (texture)
FileType( 'Clustering Texture', 'Label Texture' )
FileType( 'Group Clustering Texture', 'Clustering Texture' )

FileType( 'Clustering Time', 'Clustering Texture' )
FileType( 'Clustering kOpt', 'Clustering Texture' )
FileType( 'Clustering Silhouette Time', 'Clustering Texture' )
FileType( 'Patch Clustering Time', 'Clustering Texture' )
FileType( 'Clustering Vertex Silhouette Time', 'Clustering Texture' )

FileType( 'Group Clustering Time', 'Group Clustering Texture' )
FileType( 'Group Clustering Kopt', 'Group Clustering Texture' )
FileType( 'Group Clustering Silhouette', 'Group Clustering Texture' )
