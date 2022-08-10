###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

from __future__ import absolute_import
from brainvisa.data.neuroDiskItems import createFormatList

include("diffusion")

Format("Sparse Matrix", "f|*.imas")

createFormatList("Aims matrix formats",
                 ("gz compressed NIFTI-1 image",
                  "NIFTI-1 image",
                  "GIS Image"))


FileType("Nomenclature ROIs File", "Text file")


#----------------------------Fiber tracts--------------------------------------
FileType("Filtered Fascicles Bundles", "Fascicles bundles")
FileType("Fiber weights", "Text file")


#----------------------------Connectivity matrix-------------------------------
FileType("Matrix", "Any type")
FileType("Connectivity Matrix", "Matrix",
         ["Sparse Matrix", "GIS image", "gz compressed NIFTI-1 image",
          "NIFTI-1 image"])


#----------------------------Mask texture--------------------------------------
FileType("Mask Texture", "Label Texture")


#----------------------------Connectivity profile texture----------------------
FileType("Connectivity Profile Texture", "Texture")


#----------------------------Connectivity ROI texture--------------------------
FileType("Connectivity ROI Texture", "ROI Texture")

#----------------------------Silhouette--------------------------
FileType("Clustering Silhouette", "Text File")

#----------------------------Colors dictionary--------------------------
FileType("Colors dictionary", "Text File")
