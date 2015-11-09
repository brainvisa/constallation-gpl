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
* this process

Main dependencies: Axon python API, Soma-base, constel

Author: sandrine.lefranc@cea.fr
"""


#----------------------------Imports-------------------------------------------


# axon python API module
from brainvisa.processes import Signature, ReadDiskItem, WriteDiskItem, \
    ValidationError, String

# soma-base module
from soma.path import find_in_path

# constel module
try:
    from constel.lib.utils.files import select_ROI_number
except:
    pass


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constelMeanConnectivityProfileFromMatrix"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


#----------------------------Header--------------------------------------------


name = "Mean Individual Profile From Smoothed Matrix"
userLevel = 2

signature = Signature(
    # --inputs--
    "complete_individual_matrix", ReadDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "mixed",
                            "reduced": "No",
                            "dense": "No",
                            "intersubject": "No"}),
    "ROIs_nomenclature", ReadDiskItem("Nomenclature ROIs File", "Text File"),
    "ROI", String(),
    "ROIs_segmentation", ReadDiskItem("ROI Texture", "Aims texture formats",
                                      requiredAttributes={"side": "both",
                                                          "vertex_corr": "Yes"}),
    # --ouputs--
    "mean_individual_profile", WriteDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"normed": "No",
                            "thresholded": "No",
                            "averaged": "No",
                            "intersubject": "No"}),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters"""
    # default value
    self.ROIs_nomenclature = self.signature["ROIs_nomenclature"].findValue({})

    def link_matrix2ROI(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'ROI'.
        """
        if self.complete_individual_matrix is not None:
            s = str(self.complete_individual_matrix.get("gyrus"))
            name = self.signature["ROI"].findValue(s)
        return name

    # link of parameters for autocompletion
    self.linkParameters("ROI", "complete_individual_matrix", link_matrix2ROI)
    self.linkParameters("mean_individual_profile",
                        "complete_individual_matrix")


#----------------------------Main program--------------------------------------


def execution(self, context):
    """Compute the connectivity profile from connectivity matrix
    """
    # selects the ROI label corresponding to ROI name
    ROIlabel = select_ROI_number(self.ROIs_nomenclature.fullPath(), self.ROI)

    context.system("constelMeanConnectivityProfileFromMatrix",
                   "-connfmt", "binar_sparse",
                   "-connmatrixfile", self.complete_individual_matrix,
                   "-outconntex", self.mean_individual_profile,
                   "-seedregionstex", self.ROIs_segmentation,
                   "-seedlabel", ROIlabel,
                   "-type", "seed_mean_connectivity_profile",
                   "-normalize", 0,
                   "-verbose", 1)
