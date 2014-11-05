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

# BrainVisa module
from brainvisa.processes import *

# System module
import warnings

# Plot aims module
try:
    from soma import aims
except:
    warnings.warn("Please make sure that aims module is installed.")

name = "Remove Internal Connections"
userLevel = 2

# Argument declaration
signature = Signature(
    "patch_connectivity_profile", ReadDiskItem(
        "Gyrus Connectivity Profile", "Aims texture formats"),
    "white_mesh", ReadDiskItem("Mesh", "Aims mesh formats"),
    "gyri_texture", ReadDiskItem("Label Texture", "Aims texture formats"),
    "patch", Integer(),
    "normed_connectivity_profile", WriteDiskItem(
        "Normed Connectivity Profile", "Aims texture formats"),
)


def initialization(self):
    """Provides default values and link of parameters
    """
    self.linkParameters("white_mesh", "patch_connectivity_profile")
    self.linkParameters(
        "normed_connectivity_profile", "patch_connectivity_profile")

    self.setOptional("patch")
    self.signature["white_mesh"].userLevel = 2
    

def execution(self, context):
    """remove internals connections of patch
    """
    # provides the patch name
    if self.patch is not None:
        patch = self.patch  # keep internal connections, put 0
    else:
        patch = os.path.basename(
            os.path.dirname(os.path.dirname(os.path.dirname(
                self.patch_connectivity_profile.fullPath()))))
        patch = patch.strip("G")

    # remove internals connections
    mask = aims.read(self.gyri_texture.fullPath())
    pcp = aims.read(self.patch_connectivity_profile.fullPath())
    maskarr = mask[0].arraydata()
    pcparr = pcp[0].arraydata()
    for i in xrange(pcp[0].nItem()):
        pcparr[maskarr == int(patch)] = 0

    # the profile is normalized
    dividende_coef = pcparr.max()
    if dividende_coef > 0:
        z = 1. / dividende_coef
        pcparr *= z
    aims.write(pcp, self.normed_connectivity_profile.fullPath())