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

# Axon python API modules
from brainvisa.processes import *

# Soma-base module
from soma.path import find_in_path
from soma import aims

# Sytem module
import numpy as np
import warnings

# Plot constel modules
try:
    import constel.lib.texturetools as tt
except:
    warnings.warn("Please make sure that constellation module is installed.")


# Plot constel module
def validation():
    """This function is executed at BrainVisa startup when the process is loaded.

    It checks some conditions for the process to be available.
    """
    if not find_in_path("constelConnectionDensityTexture"):
        raise ValidationError(
            "Please make sure that constel module is installed.")

name = "Filtering Watershed"
userLevel = 2

# Argument declaration
signature = Signature(
    "complete_connectivity_matrix", ReadDiskItem(
        "Gyrus Connectivity Matrix", "Matrix sparse"),
    "watershed", ReadDiskItem("Watershed Texture", "Aims texture formats"),
    "gyri_texture", ReadDiskItem(
        "FreesurferResampledBothParcellationType", "Aims texture formats"),
    "white_mesh", ReadDiskItem("AimsBothWhite", "Aims mesh formats"),
    "patch", Integer(),
    "sum_vertices_patch", WriteDiskItem(
        "Sum Values From Region", "Aims texture formats"),
    "duplication_value_patch", WriteDiskItem(
        "Spread Value On Region", "Aims texture formats"),
    "filtered_watershed", WriteDiskItem(
        "Filtered Watershed", "Aims texture formats"),
)


def initialization(self):
    """Provides default values and link of parameters
    """
    def link_watershed(self, dummy):
        if self.complete_connectivity_matrix is not None:
            attrs = dict(
                self.complete_connectivity_matrix.hierarchyAttributes())
            attrs["smoothing"] = "smooth" + str(
                self.complete_connectivity_matrix.get("smoothing"))
            filename = self.signature["watershed"].findValue(attrs)
            return filename

    self.linkParameters(
        "watershed", "complete_connectivity_matrix", link_watershed)
    self.linkParameters("sum_vertices_patch", "complete_connectivity_matrix")
    self.linkParameters(
        "duplication_value_patch", "complete_connectivity_matrix")
    self.linkParameters("filtered_watershed", "complete_connectivity_matrix")

    self.setOptional("patch")
    self.signature["white_mesh"].userLevel = 3


def execution(self, context):
    """ Compute reduced connectivity matrix
    """
    # provides the patch name
    if self.patch is not None:
        patch = self.patch
    else:
        patch = os.path.dirname(
            os.path.basename(os.path.dirname(os.path.dirname(
                self.complete_connectivity_matrix.fullPath()))))
        patch = patch.strip("G")

    context.system("constelConnectionDensityTexture",
                   "-mesh", self.white_mesh,
                   "-connmatrixfile", self.complete_connectivity_matrix,
                   "-targetregionstex", self.watershed,
                   "-seedregionstex", self.gyri_texture,
                   "-seedlabel", patch,
                   "-type", "oneSeedRegion_to_targets",
                   "-outconntex", self.sum_vertices_patch,
                   "-outconntargets", self.duplication_value_patch,
                   "-normalize", 1)
    fibersNbByWatershedBasinsTarget_tex = aims.read(
        self.duplication_value_patch.fullPath())
    subjectWatershedBasins_tex = aims.read(self.watershed.fullPath())

    # TO DO: assorted improvements??? (it is not clear yet...)
    labelsToRemove_ar = fibersNbByWatershedBasinsTarget_tex[0].arraydata()
    watershedTargets_fibersThreshold = 95
    threshPercent = watershedTargets_fibersThreshold / 100.
    labels = labelsToRemove_ar.copy()
    labels_sort = labels.argsort()
    labelsToRemove_list = labelsToRemove_ar.tolist()
    labelsToRemove_list = sorted(labelsToRemove_list, reverse=True)
    labelsToRemove_ar = np.asarray(labelsToRemove_list)
    labelsSort_CumSum = labelsToRemove_ar.cumsum()
    invsort_labelsToRemove = np.where(labelsSort_CumSum > threshPercent)[0]
    invlabels_toRemove = labels.size - 1 - invsort_labelsToRemove
    labelsToRemove_ar = labels_sort[invlabels_toRemove]
    labelsToRemove_ar = labelsToRemove_ar + 1
    labelsToRemove_list = labelsToRemove_ar.tolist()
    sup10percentConn_labels = np.where(labels > 0.1)[0] + 1

    for sup10percent_label_i in xrange(sup10percentConn_labels.size):
        sup10percent_label = sup10percentConn_labels[sup10percent_label_i]
        if labelsToRemove_list.count(sup10percent_label) != 0:
            labelsToRemove_list.remove(sup10percent_label)

    # Min Vertex number checking:
    labelsWithSizeToSmallToRemove_list = []
    for label in labelsWithSizeToSmallToRemove_list:
        if labelsToRemove_list.count(label) == 0:
            labelsToRemove_list.append(label)

    filteredWatershedBasins_tex = tt.remove_labels(
        subjectWatershedBasins_tex, labelsToRemove_list)
    aims.write(
        filteredWatershedBasins_tex, self.filtered_watershed.fullPath())