###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

# Axon python API module
from brainvisa.processes import *
from soma.path import find_in_path

# constel module
from constel.lib.texturetools import identify_patch_number


# Plot contel
def validation():
    """This function is executed at BrainVisa startup when the process is loaded.

    It checks some conditions for the process to be available.
    """
    if not find_in_path("constelConnectivityMatrix"):
        raise ValidationError(
            "Please make sure that constel module is installed.")

name = "Connectivity Matrix"
userLevel = 2

# Argument declaration
signature = Signature(
    "oversampled_distant_fibers", ReadDiskItem(
        "Oversampled Fibers", "Aims readable bundles formats"),
    "filtered_length_fibers_near_cortex", ReadDiskItem(
        "Fibers Near Cortex", "Aims readable bundles formats"),
    "white_mesh", ReadDiskItem("Mesh", "Aims mesh formats"),
    "gyri_texture", ReadDiskItem("Label Texture", "Aims texture formats"),
    "dw_to_t1", ReadDiskItem(
        "Transformation matrix", "Transformation matrix"),
    "matrix_of_distant_fibers", WriteDiskItem(
        "Connectivity Matrix Outside Fibers Of Cortex", "Matrix sparse"),
    "matrix_of_fibers_near_cortex", WriteDiskItem(
        "Connectivity Matrix Fibers Near Cortex", "Matrix sparse"),
    "profile_of_fibers_near_cortex", WriteDiskItem(
        "Connectivity Profile Fibers Near Cortex", "Gifti file"),
    "profile_of_distant_fibers", WriteDiskItem(
        "Connectivity Profile Outside Fibers Of Cortex",
        "Gifti file"),
)


def initialization(self):
    """Provides default values and link of parameters"""
    self.linkParameters(
        "filtered_length_fibers_near_cortex", "oversampled_distant_fibers")
    self.linkParameters(
        "matrix_of_distant_fibers", "oversampled_distant_fibers")
    self.linkParameters(
        "matrix_of_fibers_near_cortex", "matrix_of_distant_fibers")
    self.linkParameters(
        "profile_of_distant_fibers", "matrix_of_distant_fibers")
    self.linkParameters(
        "profile_of_fibers_near_cortex", "matrix_of_fibers_near_cortex")
    self.signature["profile_of_fibers_near_cortex"].userLevel = 2
    self.signature["profile_of_distant_fibers"].userLevel = 2

def execution(self, context):
    """Computes two connectivity matrices.

    (1) case 1: computes connectivity matrix for distant fibers of cortex
                one end only of fibers is identified
    (2) case 2:computes connectivity matrix for fibers near cortex
               both ends of fibers are well identified
    """
    # provides the patch name
    patch = identify_patch_number(self.oversampled_distant_fibers.fullPath())

    # case 1
    # this command is mostly concerned with fibers leaving the brain stem
    context.system("constelConnectivityMatrix",
                   "-bundles", self.oversampled_distant_fibers,
                   "-connmatrix", self.matrix_of_distant_fibers,
                   "-matrixcompute", "meshintersectionpoint",
                   "-dist", 0.0,  # no smoothing
                   "-wthresh", 0.001,
                   "-distmax", 5.0,
                   "-seedregionstex", self.gyri_texture,
                   "-outconntex", self.profile_of_distant_fibers,
                   "-mesh", self.white_mesh,
                   "-type", "seed_mean_connectivity_profile",
                   "-trs", self.dw_to_t1,
                   "-seedlabel", patch,
                   "-normalize", 0,
                   "-verbose", 1)

    # case 2
    context.system("constelConnectivityMatrix",
                   "-bundles", self.filtered_length_fibers_near_cortex,
                   "-connmatrix", self.matrix_of_fibers_near_cortex,
                   "-dist", 0.0,  # no smoothing
                   "-seedregionstex", self.gyri_texture,
                   "-outconntex", self.profile_of_fibers_near_cortex,
                   "-mesh", self.white_mesh,
                   "-type", "seed_mean_connectivity_profile",
                   "-trs", self.dw_to_t1,
                   "-seedlabel", patch,
                   "-normalize", 0,
                   "-verbose", 1)
