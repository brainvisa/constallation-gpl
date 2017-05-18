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
* execute the command 'AimsSparseMatrixSmoothing'.

Main dependencies: axon python API, soma, constel
"""

# ---------------------------Imports-------------------------------------------


# axon python API module
from brainvisa.processes import Float
from brainvisa.processes import String
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError

# soma.path module
from soma.path import find_in_path

# constel modules
try:
    from constel.lib.utils.filetools import select_ROI_number
    from constel.lib.utils.matrixtools import replace_negative_values
except:
    pass


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    cmd_name = "AimsSparseMatrixSmoothing"
    if not find_in_path(cmd_name):  # checks command
        raise ValidationError(
            "'{0}' is not contained in PATH environnement variable. "
            "Please make sure that aims is installed.".format(cmd_name))


# ---------------------------Header--------------------------------------------


name = "Smoothing of the Individual Matrix."
userLevel = 2

signature = Signature(
    # --inputs--
    "complete_individual_matrix", ReadDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "no",
                            "intersubject": "no"}),
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "cortical_region", String(),
    "cortical_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),
    "smoothing", Float(),

    # --outputs--
    "complete_matrix_smoothed", WriteDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "no",
                            "intersubject": "no"}),
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters"""

    # default values
    self.smoothing = 3.0
    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_matrix2label(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'cortical_region'.
        """
        if self.complete_individual_matrix is not None:
            s = str(self.complete_individual_matrix.get("gyrus"))
            name = self.signature["cortical_region"].findValue(s)
        return name

    def link_matrix(self, dummy):
        """Define the attribut 'smoothing' from input parameter for the
        signature 'complete_matrix_smoothed'.
        """
        if self.complete_individual_matrix is not None:
            attrs = dict(self.complete_individual_matrix.hierarchyAttributes())
            attrs["smoothing"] = str(self.smoothing)
        filename = self.signature[
                "complete_matrix_smoothed"].findValue(attrs)
        return filename

    # link of parameters for autocompletion
    self.linkParameters("cortical_region",
                        "complete_individual_matrix",
                        link_matrix2label)
    self.linkParameters("complete_matrix_smoothed",
                        "complete_individual_matrix",
                        link_matrix)


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'AimsSparseMatrixSmoothing'.

    Smoothing of the individual matrix."""
    # selects the label number corresponding to label name
    label_number = select_ROI_number(
        self.cortical_regions_nomenclature.fullPath(), self.cortical_region)

    # matrix smoothing: -s in millimetres
    context.system("AimsSparseMatrixSmoothing",
                   "-i", self.complete_individual_matrix,
                   "-m", self.white_mesh,
                   "-o", self.complete_individual_matrix,
                   "-s", self.smoothing,
                   "-l", self.cortical_parcellation,
                   "-p", label_number)

    replace_negative_values(self.complete_individual_matrix.fullPath())
