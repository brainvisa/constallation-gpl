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
from soma.path import find_in_path


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
    "patch", Integer(),
    "reduced_connectivity_matrix", WriteDiskItem(
        "Reduced Connectivity Matrix", "GIS image"),
)


# Default value
def initialization(self):
    self.setOptional("patch")

    def linkMatrix(self, dummy):
        if self.complete_connectivity_matrix is not None:
            attrs = dict(
                self.complete_connectivity_matrix.hierarchyAttributes())
            attrs["smoothing"] = "smooth" + str(
                self.complete_connectivity_matrix.get("smoothing"))
            filename = self.signature["filtered_watershed"].findValue(attrs)
            return filename
    self.linkParameters(
        "filtered_watershed", "complete_connectivity_matrix", linkMatrix)
    self.linkParameters("white_mesh", "complete_connectivity_matrix")
    self.linkParameters("reduced_connectivity_matrix", "filtered_watershed")
    self.signature["white_mesh"].userLevel = 2


def execution(self, context):
    """ Compute reduced connectivity matrix M(target regions, patch vertices)
    """
    # provides the patch name
    if self.patch is not None:
        patch = self.patch
    else:
        patch = os.path.dirname(os.path.basename(
            os.path.dirname(os.path.dirname(
                self.complete_connectivity_matrix.fullPath()))))
        patch = patch.strip("G")

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