###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

# Axon python API modules
from brainvisa.processes import *
from soma.path import find_in_path

# constel module
from constel.lib.texturetools import identify_patch_number

# Plot constel module
def validation():
    """This function is executed at BrainVisa startup when the process is loaded.

    It checks some conditions for the process to be available.
    """
    if not find_in_path("constelConnectionDensityTexture"):
        raise ValidationError(
            "Please make sure that constel module is installed.")

name = "Reduced Connectivity Matrix"
userLevel = 2

# Argument declaration
signature = Signature(
    "complete_connectivity_matrix", ReadDiskItem(
        "Gyrus Connectivity Matrix", "Matrix sparse"),
    "filtered_watershed", ReadDiskItem(
        "Filtered Watershed", "Aims texture formats"),
    "white_mesh", ReadDiskItem("Mesh", "Aims mesh formats"),
    "gyri_texture", ReadDiskItem("Label Texture", "Aims texture formats"),
    "reduced_connectivity_matrix", WriteDiskItem(
        "Reduced Connectivity Matrix", "GIS image"),
)


# Default value
def initialization(self):
    """Provides default values and link of parameters"""
    self.linkParameters("filtered_watershed", "complete_connectivity_matrix")
    self.linkParameters("reduced_connectivity_matrix", "filtered_watershed")


def execution(self, context):
    """ Compute reduced connectivity matrix M(target regions, patch vertices)
    """
    # provides the patch name
    patch = identify_patch_number(self.complete_connectivity_matrix.fullPath())

    # M(target regions, patch vertices)
    context.system("constelConnectionDensityTexture",
                   "-mesh", self.white_mesh,
                   "-connmatrixfile", self.complete_connectivity_matrix,
                   "-targetregionstex", self.filtered_watershed,
                   "-seedregionstex", str(self.gyri_texture),
                   "-seedlabel", patch,
                   "-type", "seedVertex_to_targets",
                   "-connmatrix", self.reduced_connectivity_matrix,
                   "-normalize", 1,
                   "-verbose", 1)
