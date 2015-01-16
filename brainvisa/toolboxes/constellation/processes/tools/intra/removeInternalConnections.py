###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

# BrainVisa module
from brainvisa.processes import *
from soma.path import find_in_path

name = "Remove Internal Connections"
userLevel = 2

# Argument declaration
signature = Signature(
    "patch_connectivity_profile", ReadDiskItem(
        "Gyrus Connectivity Profile", "Aims texture formats"),
    "gyri_texture", ReadDiskItem("Label Texture", "Aims texture formats"),
    "normed_connectivity_profile", WriteDiskItem(
        "Normed Connectivity Profile", "Aims texture formats"),
    "keep_internal_connections", Boolean(),
)


def initialization(self):
    """Provides default values and link of parameters
    """
    self.keep_internal_connections = False
    self.linkParameters(
        "normed_connectivity_profile", "patch_connectivity_profile")


def execution(self, context):
    """
    STEP 1/2: Remove internals connections of patch.
    STEP 2/2: The profile is normalized. 
    """
    args = []
    args += ["-p", self.patch_connectivity_profile,
             "-g", self.gyri_texture,
             "-n", self.normed_connectivity_profile]

    if not self.keep_internal_connections:
        args += ["-q", self.keep_internal_connections]
    else:
        args += ["-c", self.keep_internal_connections]

    context.system(sys.executable,
                   find_in_path("constelRemoveInternalConnections.py"),
                   *args)
