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
* define a Brainvisa process.
* executes the command 'constelConnectionDensityTexture'.

Main dependencies: axon python API, soma, constel

Author: Sandrine Lefranc, 2015
"""

# ---------------------------Imports-------------------------------------------


# axon python API modules
from brainvisa.processes import Signature, ReadDiskItem, ValidationError, \
    WriteDiskItem, String, Boolean
from soma.path import find_in_path

# constel modules
try:
    from constel.lib.utils.filetools import select_ROI_number
    from constel.lib.utils.matrixtools import save_normalization
except:
    pass


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constelConnectionDensityTexture"):
        raise ValidationError(
            "constelConnectionDensityTexture is not contained in PATH"
            "environnement variable or please make sure that constellation "
            "is installed.")


# ---------------------------Header--------------------------------------------


name = "Reduced Individual Matrix From Filtered Reduced Profile"
userLevel = 2

signature = Signature(
    # --inputs--
    "complete_matrix_smoothed", ReadDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "no",
                            "intersubject": "no",
                            "individual": "yes"}),
    "filtered_reduced_individual_profile", ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "yes",
                            "roi_filtered": "yes",
                            "intersubject": "no",
                            "step_time": "no",
                            "measure": "no"}),
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "cortical_region", String(),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),
    "cortical_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),

    # --outputs--
    "reduced_individual_matrix", WriteDiskItem(
        "Connectivity Matrix", "Aims matrix formats",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "yes",
                            "intersubject": "no",
                            "individual": "yes"}),
    "normalize", Boolean(),
)


# ---------------------------Function--------------------------------------


def initialization(self):
    """Provides default value and link of parameters"""
    # default value
    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})
    self.normalize = True

    def link_matrix2label(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'cortical_region'.
        """
        if self.complete_matrix_smoothed is not None:
            s = str(self.complete_matrix_smoothed.get("gyrus"))
            return s

    # link of parameters for autocompletion
    self.linkParameters("filtered_reduced_individual_profile",
                        "complete_matrix_smoothed")
    self.linkParameters("cortical_region",
                        "complete_matrix_smoothed",
                        link_matrix2label)
    self.linkParameters("reduced_individual_matrix",
                        "filtered_reduced_individual_profile")


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """ Compute reduced connectivity matrix M(target regions, patch vertices)
    """
    # selects the ROI label corresponding to ROI name
    label_number = select_ROI_number(
        self.cortical_regions_nomenclature.fullPath(), self.cortical_region)

    # normalization of the reduced matrix
    if self.normalize:
        norm = 1
    else:
        norm = 0

    # M(target regions, patch vertices)
    context.system(
        "constelConnectionDensityTexture",
        "-mesh", self.white_mesh,
        "-connmatrixfile", self.complete_matrix_smoothed,
        "-targetregionstex", self.filtered_reduced_individual_profile,
        "-seedregionstex", str(self.cortical_parcellation),
        "-seedlabel", label_number,
        "-type", "seedVertex_to_targets",
        "-connmatrix", self.reduced_individual_matrix,
        "-normalize", norm,
        "-verbose", 1
        )

    # save the normalization values
    if not self.normalize:
        save_normalization(self.reduced_individual_matrix.fullPath())
