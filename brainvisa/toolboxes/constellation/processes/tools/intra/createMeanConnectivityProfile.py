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
    if not find_in_path("constelMeanConnectivityProfileFromMatrix"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


name = "Mean Connectivity Profile"
userLevel = 2

# Argument declaration
signature = Signature(
    "complete_connectivity_matrix", ReadDiskItem(
        "Gyrus Connectivity Matrix", "Matrix sparse"),
    "gyri_texture", ReadDiskItem("Label Texture", "Aims texture formats"),
    "patch_connectivity_profile", WriteDiskItem(
        "Gyrus Connectivity Profile", "GIFTI file"),
)


def initialization(self):
    """Provides default values and link of parameters"""
    self.linkParameters("patch_connectivity_profile",
                        "complete_connectivity_matrix")


def execution(self, context):
    """Compute the connectivity profile from connectivity matrix
    """
    # provides the patch name
    patch = identify_patch_number(self.complete_connectivity_matrix.fullPath())

    context.system("constelMeanConnectivityProfileFromMatrix",
                   "-connfmt", "binar_sparse",
                   "-connmatrixfile", self.complete_connectivity_matrix,
                   "-outconntex", self.patch_connectivity_profile,
                   "-seedregionstex", self.gyri_texture,
                   "-seedlabel", patch,
                   "-type", "seed_mean_connectivity_profile",
                   "-normalize", 0,
                   "-verbose", 1)
