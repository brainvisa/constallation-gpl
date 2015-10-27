###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

include("diffusion")


FileType("Nomenclature ROIs File", "Text file")


#----------------------------Fiber tracts--------------------------------------
FileType("Filtered Fascicles Bundles", "Fascicles bundles")


#----------------------------Connectivity matrix-------------------------------
FileType("Matrix", "Any type")
FileType("Connectivity Matrix", "Matrix")


#----------------------------Mask texture--------------------------------------
FileType("Mask Texture", "Texture")


#----------------------------Connectivity profile texture----------------------
FileType("Connectivity Profile Texture", "Texture")
FileType("Filtered Connectivity Profile Texture", "Connectivity Profile Texture")


#----------------------------Connectivity ROI texture--------------------------
FileType("Connectivity ROI Texture", "ROI Texture")
FileType("Measures Connectivity ROI Texture", "Connectivity ROI Texture")
