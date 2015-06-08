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


# Plot constel module
def validation():
    """This function is executed at BrainVisa startup when the process is loaded.

    It checks some conditions for the process to be available.
    """
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
    "connectivity_profile", ReadDiskItem(
        "Avg Connectivity Profile", "Aims texture formats"),
    "thresholded_connectivity_profile", WriteDiskItem(
        "Avg Thresholded Connectivity Profile", "Aims texture formats"),
    "normed_connectivity_profile", WriteDiskItem(
        "Avg Normed Connectivity Profile", "Aims texture formats"),)


def initialization(self):
    """Provides default values and link of parameters"""
    self.linkParameters("connectivity_profile", "mask")
    self.linkParameters(
        "thresholded_connectivity_profile", "connectivity_profile")
    self.linkParameters(
        "normed_connectivity_profile", "thresholded_connectivity_profile")


def execution(self, context):
    """
    """
    mask = aims.read(self.mask.fullPath())
    meanConnectivityProfileTex = aims.read(
        self.connectivity_profile.fullPath())
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
