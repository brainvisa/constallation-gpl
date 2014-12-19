############################################################################
#  This software and supporting documentation are distributed by
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
############################################################################

# BrainVisa modules
from brainvisa.processes import *
from soma.path import find_in_path


# Plot aims module
def validation():
    if not find_in_path("AimsMeshWatershed.py"):
        raise ValidationError(
            "Please make sure that aims module is installed.")

name = "Watershed"
userLevel = 2

# Argument declaration
signature = Signature(
    "normed_connectivity_profile", ReadDiskItem(
        "Normed Connectivity Profile", "Aims texture formats"),
    "white_mesh", ReadDiskItem("Mesh", "Aims mesh formats"),
    "watershed", WriteDiskItem("Watershed Texture", "Aims texture formats"),
)


def initialization(self):
    """Provides default values and link of parameters
    """
    self.linkParameters("white_mesh", "normed_connectivity_profile")
    self.linkParameters("watershed", "normed_connectivity_profile")
    self.signature["white_mesh"].userLevel = 3


def execution(self, context):
    """ Watershed is computed providing a set of target regions
    """
    commandMeshWatershedProcessing = [
        sys.executable, find_in_path("AimsMeshWatershed.py"),
        "-i", self.normed_connectivity_profile,
        "-m", self.white_mesh,
        "-k", 10,
        "-q", 0.05,
        "-z", "or",
        "-t", 0.05,
        "-o", self.watershed]
    context.system(*commandMeshWatershedProcessing)