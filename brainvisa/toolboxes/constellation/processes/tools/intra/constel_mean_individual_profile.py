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
* define a Brainvisa process
* execute the command 'constelMeanConnectivityProfileFromMatrix'.

Main dependencies: axon python API, soma, constel

Author: Sandrine Lefranc, 2015
"""


# --------------------------Imports-------------------------------------------


# axon python API module
from brainvisa.processes import String
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError

# soma module
from soma.path import find_in_path

# constel module
try:
    from constel.lib.utils.filetools import select_ROI_number
except:
    pass


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constelMeanConnectivityProfileFromMatrix"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ---------------------------Header--------------------------------------------


name = "Mean Individual Profile From Smoothed Matrix"
userLevel = 2

signature = Signature(
    # --inputs--
    "complete_matrix_smoothed", ReadDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "no",
                            "intersubject": "no",
                            "individual": "yes"}),
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "cortical_region", String(),
    "cortical_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    # --ouputs--
    "mean_individual_profile", WriteDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"ends_labelled": "all",
                            "normed": "no",
                            "intersubject": "no"}),
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters"""
    # default value
    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_matrix2label(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'cortical_region'.
        """
        if self.complete_matrix_smoothed is not None:
            s = str(self.complete_matrix_smoothed.get("gyrus"))
            name = self.signature["cortical_region"].findValue(s)
        return name

    # link of parameters for autocompletion
    self.linkParameters("cortical_region",
                        "complete_matrix_smoothed",
                        link_matrix2label)
    self.linkParameters("mean_individual_profile",
                        "complete_matrix_smoothed")


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constelMeanConnectivityProfileFromMatrix'.

    Compute the connectivity profile (no normalize) from connectivity matrix.
    """
    # selects the label number corresponding to label name
    label_number = select_ROI_number(
        self.cortical_regions_nomenclature.fullPath(), self.cortical_region)

    context.system("constelMeanConnectivityProfileFromMatrix",
                   "-connfmt", "binar_sparse",
                   "-connmatrixfile", self.complete_matrix_smoothed,
                   "-outconntex", self.mean_individual_profile,
                   "-seedregionstex", self.cortical_parcellation,
                   "-seedlabel", label_number,
                   "-type", "seed_mean_connectivity_profile",
                   "-normalize", 0,
                   "-verbose", 1)
