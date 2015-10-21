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
    - the parameters of a process (Signature),
    - the parameters initialization
    - the linked parameters
* executes the command 'constelConnectionDensityTexture'

Main dependencies: axon python API, soma-base, constel

Author: Sandrine Lefranc, 2015
"""

#----------------------------Imports-------------------------------------------

# python module
import numpy

# axon python API module
from brainvisa.processes import ValidationError, Signature, ReadDiskItem, \
    WriteDiskItem, OpenChoice, Choice

# Soma-base module
from soma.path import find_in_path
from soma import aims

# constel module
try:
    import constel.lib.texturetools as tt
    from constel.lib.utils.files import read_file, select_ROI_number
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


name = "Filtering Watershed"
userLevel = 2

signature = Signature(
    # inputs
    "complete_connectivity_matrix", ReadDiskItem(
        "Connectivity Matrix", "Matrix sparse",
        requiredAttributes={"ends_labelled":"mixed",
                            "reduced":"No",
                            "dense":"No",
                            "intersubject":"No"}),
    "watershed", ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect":"Yes",
                            "roi_filtered":"No",
                            "averaged":"No",
                            "intersubject":"No",
                            "step_time":"No"}),
        
    "ROIs_segmentation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side":"both", "vertex_corr":"Yes"}),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "ROIs_nomenclature", ReadDiskItem("Nomenclature ROIs File", "Text File"),
    "ROI", OpenChoice(),

    #outputs
    "sum_vertices_patch", WriteDiskItem(
        "Measures Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"measure": "sum"}),
    "duplication_value_patch", WriteDiskItem(
        "Measures Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"measure": "spread"}),
    "filtered_watershed", WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect":"Yes",
                            "roi_filtered":"Yes",
                            "averaged":"No",
                            "intersubject":"No",
                            "step_time":"No"}),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters
    """
    # default value
    self.ROIs_nomenclature = self.signature["ROIs_nomenclature"].findValue({})

    def link_roi(self, dummy):
        """Reads the ROIs nomenclature and proposes them in the signature 'ROI'
        of process.
        """
        if self.ROIs_nomenclature is not None:
            s = ["Select a ROI in this list"]
            s += read_file(self.ROIs_nomenclature.fullPath(), mode=2)
            self.signature["ROI"].setChoices(*s)
            if isinstance(self.signature['ROI'], OpenChoice):
                self.signature["ROI"] = Choice(*s)
                self.changeSignature(self.signature)

    def link_matrix2ROI(self, dummy):
        """Define the attribut 'ROI' from fibertracts pattern for the
        signature 'ROI'.
        """
        if self.complete_connectivity_matrix is not None:
            s = str(self.complete_connectivity_matrix.get("gyrus"))
            name = self.signature["ROI"].findValue(s)
        return name

    self.linkParameters("ROI", "ROIs_nomenclature", link_roi)
    self.linkParameters(
        "ROI", "complete_connectivity_matrix", link_matrix2ROI)
    self.linkParameters("watershed", "complete_connectivity_matrix")
    self.linkParameters("sum_vertices_patch", "complete_connectivity_matrix")
    self.linkParameters(
        "duplication_value_patch", "complete_connectivity_matrix")
    self.linkParameters("filtered_watershed", "complete_connectivity_matrix")


#----------------------------Main program--------------------------------------


def execution(self, context):
    """ Compute reduced connectivity matrix
    """
   
    # selects the ROI label corresponding to ROI name
    ROIlabel = select_ROI_number(self.ROIs_nomenclature.fullPath(), self.ROI)

    context.system("constelConnectionDensityTexture",
                   "-mesh", self.white_mesh,
                   "-connmatrixfile", self.complete_connectivity_matrix,
                   "-targetregionstex", self.watershed,
                   "-seedregionstex", self.ROIs_segmentation,
                   "-seedlabel", ROIlabel,
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
    aims.write(
        filteredWatershedBasins_tex, self.filtered_watershed.fullPath())
