###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

"""
This script does the following:
* defines a Brainvisa process
    - the signature of the inputs/ouputs,
    - the initialization (by default) of the inputs,
    - the interlinkages between inputs/outputs.
* executes the command 'constelConnectionDensityTexture': the individual
  regions profile is computed.

Main dependencies: axon python API, soma, constel

Author: Sandrine Lefranc, 2015
"""

#----------------------------Imports-------------------------------------------

# python module
import numpy

# axon python API module
from brainvisa.processes import ValidationError, Signature, ReadDiskItem, \
    WriteDiskItem, OpenChoice, Choice

# soma- module
from soma.path import find_in_path
from soma import aims

# constel module
try:
    import constel.lib.utils.texturetools as tt
    from constel.lib.utils.filetools import read_file, select_ROI_number
except:
    pass


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constelConnectionDensityTexture"):
        raise ValidationError(
            "constelConnectionDensityTexture is not contained in PATH"
            "environnement variable or please make sure that constel module "
            "is installed.")


#----------------------------Header--------------------------------------------


name = "Individual Regions Filtering"
userLevel = 2

signature = Signature(
    # --inputs--
    "complete_individual_matrix", ReadDiskItem(
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
    "cortical_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "cortical_region", OpenChoice(),

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


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters
    """
    # default value
    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def reset_label(self, dummy):
        """This callback reads the ROIs nomenclature and proposes them in the
        signature 'cortical_region' of process.
        It also resets the cortical_region parameter to default state after
        the nomenclature changes.
        """
        current = self.cortical_region
        self.setValue('cortical_region', current, True)
        if self.cortical_regions_nomenclature is not None:
            s = [("Select a cortical_region in this list", None)]
            # temporarily set a value which will remain valid
            self.cortical_region = s[0][1]
            s += read_file(
                self.cortical_regions_nomenclature.fullPath(), mode=2)
            self.signature["cortical_region"].setChoices(*s)
            if isinstance(self.signature["cortical_region"], OpenChoice):
                self.signature["cortical_region"] = Choice(*s)
                self.changeSignature(self.signature)
            if current not in s:
                self.setValue("cortical_region", s[0][1], True)
            else:
                self.setValue("cortical_region", current, True)

    def link_matrix2ROI(self, dummy):
        """Define the attribut 'cortical_region' from fibertracts pattern for
        the signature 'cortical_region'.
        """
        if self.complete_individual_matrix is not None:
            s = str(self.complete_individual_matrix.get("gyrus"))
            name = self.signature["cortical_region"].findValue(s)
        return name

    self.linkParameters(None, "cortical_regions_nomenclature", reset_label)
    self.linkParameters("cortical_region", "complete_individual_matrix",
                        link_matrix2ROI)
    self.linkParameters("reduced_individual_profile",
                        "complete_individual_matrix")
    self.linkParameters("sum_vertices_patch", "complete_individual_matrix")
    self.linkParameters("duplication_value_patch",
                        "complete_individual_matrix")
    self.linkParameters("filtered_reduced_individual_profile",
                        "complete_individual_matrix")


#----------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constelConnectionDensityTexture'.

    Compute reduced connectivity matrix
    """
    # selects the ROI label corresponding to ROI name
    label_number = select_ROI_number(
        self.cortical_regions_nomenclature.fullPath(), self.cortical_region)

    context.system("constelConnectionDensityTexture",
                   "-mesh", self.white_mesh,
                   "-connmatrixfile", self.complete_individual_matrix,
                   "-targetregionstex", self.reduced_individual_profile,
                   "-seedregionstex", self.cortical_parcellation,
                   "-seedlabel", label_number,
                   "-type", "oneSeedRegion_to_targets",
                   "-outconntex", self.sum_vertices_patch,
                   "-outconntargets", self.duplication_value_patch,
                   "-normalize", 1)

    fibersNbByWatershedBasinsTarget_tex = aims.read(
        self.duplication_value_patch.fullPath())
    subjectWatershedBasins_tex = aims.read(
        self.reduced_individual_profile.fullPath())

    # TO DO: assorted improvements??? (it is not clear yet...)
    labelsToRemove_ar = fibersNbByWatershedBasinsTarget_tex[0].arraydata()
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
    aims.write(filteredWatershedBasins_tex,
               self.filtered_reduced_individual_profile.fullPath())
