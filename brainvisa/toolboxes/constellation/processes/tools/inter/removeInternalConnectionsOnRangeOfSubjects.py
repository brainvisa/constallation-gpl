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


# Plot constel module
def validation():
    try:
        import soma.aims
    except:
        raise ValidationError(
            "Please make sure that aims module is installed.")

name = "Normed Connectivity Profile of Group"
userLevel = 2

# Argument declaration
signature = Signature(
    "mask", ReadDiskItem("Avg Connectivity Mask", "Aims texture formats"),
    "connectivity_profiles", ReadDiskItem(
        "Avg Connectivity Profile", "Aims texture formats"),
    "thresholded_connectivity_profile", WriteDiskItem(
        "Avg Thresholded Connectivity Profile", "Aims texture formats"),
    "normed_connectivity_profile", WriteDiskItem(
        "Avg Normed Connectivity Profile", "Aims texture formats"),)


# Default values
def initialization(self):
    self.linkParameters("connectivity_profiles", "mask")
    self.linkParameters(
        "thresholded_connectivity_profile", "connectivity_profiles")
    self.linkParameters(
        "normed_connectivity_profile", "thresholded_connectivity_profile")


def execution(self, context):
    """
    """
    mask = aims.read(self.mask.fullPath())
    meanConnectivityProfileTex = aims.read(
        self.connectivity_profiles.fullPath())
    for i in xrange(meanConnectivityProfileTex[0].nItem()):
        if mask[0][i] == 0:
            meanConnectivityProfileTex[0][i] = 0
    aims.write(meanConnectivityProfileTex,
               self.thresholded_connectivity_profile.fullPath())

    tex = aims.read(self.thresholded_connectivity_profile.fullPath())
    tex_ar = tex[0].arraydata()
    max_connections_nb = tex_ar.max()
    if max_connections_nb > 0:
        z = 1./max_connections_nb
        for i in xrange(tex[0].nItem()):
            value = tex[0][i]
            tex[0][i] = z*value
    aims.write(tex, self.normed_connectivity_profile.fullPath())