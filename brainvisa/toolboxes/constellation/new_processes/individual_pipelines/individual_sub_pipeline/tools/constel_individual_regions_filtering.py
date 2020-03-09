###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################


# ---------------------------Imports-------------------------------------------

# System module
from __future__ import absolute_import
import numpy
import six

# Axon python API modules
from brainvisa.processes import Choice
from brainvisa.processes import Signature
from brainvisa.processes import OpenChoice
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError

# Soma module
from soma import aims
from soma.path import find_in_path

# Package import
try:
    from constel.lib.utils.texturetools import remove_labels
    from constel.lib.utils.filetools import read_file, select_ROI_number
except ImportError:
    raise ValidationError("Please make sure that constel module is installed.")


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constelConnectionDensityTexture"):
        raise ValidationError(
            "constelConnectionDensityTexture is not contained in PATH"
            "environnement variable or please make sure that constel module "
            "is installed.")


# ---------------------------Header--------------------------------------------


name = "Individual Regions Filtering"
userLevel = 2

signature = Signature(
    # --inputs--
    "complete_matrix_smoothed", ReadDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "no",
                            "intersubject": "no",
                            "individual": "yes"}),
    "reduced_individual_profile", ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "yes",
                            "roi_filtered": "no",
                            "intersubject": "no",
                            "step_time": "no",
                            "measure": "no"}),
    "regions_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),
    "individual_white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),
    "regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "region", OpenChoice(),

    # --outputs--
    "sum_vertices_patch", WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "no",
                            "roi_filtered": "no",
                            "intersubject": "no",
                            "step_time": "no",
                            "measure": "sum"}),
    "duplication_value_patch", WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "no",
                            "roi_filtered": "no",
                            "intersubject": "no",
                            "step_time": "no",
                            "measure": "spread"}),
    "filtered_reduced_individual_profile", WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "yes",
                            "roi_filtered": "yes",
                            "intersubject": "no",
                            "step_time": "no",
                            "measure": "no"}),
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters
    """
    # default value
    self.regions_nomenclature = self.signature[
        "regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def reset_label(self, dummy):
        """This callback reads the ROIs nomenclature and proposes them in the
        signature 'region' of process.
        It also resets the region parameter to default state after
        the nomenclature changes.
        """
        current = self.region
        self.setValue('region', current, True)
        if self.regions_nomenclature is not None:
            s = [("Select a region in this list", None)]
            # temporarily set a value which will remain valid
            self.region = s[0][1]
            s += read_file(
                self.regions_nomenclature.fullPath(), mode=2)
            self.signature["region"].setChoices(*s)
            if isinstance(self.signature["region"], OpenChoice):
                self.signature["region"] = Choice(*s)
                self.changeSignature(self.signature)
            if current not in s:
                self.setValue("region", s[0][1], True)
            else:
                self.setValue("region", current, True)

    def link_matrix2ROI(self, dummy):
        """Define the attribut 'region' from fibertracts pattern for
        the signature 'region'.
        """
        if self.complete_matrix_smoothed is not None:
            s = str(self.complete_matrix_smoothed.get("gyrus"))
            name = self.signature["region"].findValue(s)
        return name

    self.linkParameters(None,
                        "regions_nomenclature",
                        reset_label)
    self.linkParameters("region",
                        "complete_matrix_smoothed",
                        link_matrix2ROI)
    self.linkParameters("reduced_individual_profile",
                        "complete_matrix_smoothed")
    self.linkParameters("sum_vertices_patch",
                        "complete_matrix_smoothed")
    self.linkParameters("duplication_value_patch",
                        "complete_matrix_smoothed")
    self.linkParameters("filtered_reduced_individual_profile",
                        "complete_matrix_smoothed")


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constelConnectionDensityTexture'.

    Compute reduced connectivity matrix
    """
    # selects the ROI label corresponding to ROI name
    label_number = select_ROI_number(self.regions_nomenclature.fullPath(),
                                     self.region)

    context.system("constelConnectionDensityTexture",
                   "-mesh", self.individual_white_mesh,
                   "-connmatrixfile", self.complete_matrix_smoothed,
                   "-targetregionstex", self.reduced_individual_profile,
                   "-seedregionstex", self.regions_parcellation,
                   "-seedlabel", label_number,
                   "-type", "oneSeedRegion_to_targets",
                   "-outconntex", self.sum_vertices_patch,
                   "-outconntargets", self.duplication_value_patch,
                   "-normalize", 1)

    fibers_by_basins = aims.read(self.duplication_value_patch.fullPath())
    basins = aims.read(self.reduced_individual_profile.fullPath())

    # TO DO: assorted improvements??? (it is not clear yet...)
    labelsToRemove_ar = fibers_by_basins[0].arraydata()
    watershedTargets_fibersThreshold = 95
    threshPercent = watershedTargets_fibersThreshold / 100.
    labels = labelsToRemove_ar.copy()
    labels_sort = labels.argsort()
    labelsToRemove_list = labelsToRemove_ar.tolist()
    labelsToRemove_list = sorted(labelsToRemove_list, reverse=True)
    labelsToRemove_ar = numpy.asarray(labelsToRemove_list)
    labelsSort_CumSum = labelsToRemove_ar.cumsum()
    invsort_labelsToRemove = numpy.where(labelsSort_CumSum > threshPercent)[0]
    invlabels_toRemove = labels.size - 1 - invsort_labelsToRemove
    labelsToRemove_ar = labels_sort[invlabels_toRemove]
    labelsToRemove_ar = labelsToRemove_ar + 1
    labelsToRemove_list = labelsToRemove_ar.tolist()
    sup10percentConn_labels = numpy.where(labels > 0.1)[0] + 1

    for sup10percent_label_i in six.moves.xrange(sup10percentConn_labels.size):
        sup10percent_label = sup10percentConn_labels[sup10percent_label_i]
        if labelsToRemove_list.count(sup10percent_label) != 0:
            labelsToRemove_list.remove(sup10percent_label)

    # Min Vertex number checking:
    labelsWithSizeToSmallToRemove_list = []
    for label in labelsWithSizeToSmallToRemove_list:
        if labelsToRemove_list.count(label) == 0:
            labelsToRemove_list.append(label)

    filteredWatershedBasins_tex = remove_labels(
        basins, labelsToRemove_list)
    aims.write(filteredWatershedBasins_tex,
               self.filtered_reduced_individual_profile.fullPath())
