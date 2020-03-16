###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################


# ---------------------------Imports-------------------------------------------


# Axon python API module
from __future__ import absolute_import
from brainvisa.processes import Float
from brainvisa.processes import String
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError

# Soma module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    cmd = "AimsSparseMatrixSmoothing"
    if not find_in_path(cmd):  # checks command
        raise ValidationError(
            "'{0}' is not contained in PATH environnement variable. "
            "Please make sure that AIMS C++ library is installed.".format(cmd))
    try:
        from constel.lib.utils.filetools import select_ROI_number,\
            replace_negative_values
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")


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
    "regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "region", String(),
    "regions_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),
    "individual_white_mesh", ReadDiskItem(
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
    self.regions_nomenclature = self.signature[
        "regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_matrix2label(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'region'.
        """
        if self.complete_individual_matrix is not None:
            s = str(self.complete_individual_matrix.get("gyrus"))
            name = self.signature["region"].findValue(s)
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
    self.linkParameters("region",
                        "complete_individual_matrix",
                        link_matrix2label)
    self.linkParameters("complete_matrix_smoothed",
                        "complete_individual_matrix",
                        link_matrix)


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'AimsSparseMatrixSmoothing'.

    Smoothing of the individual matrix."""
    from constel.lib.utils.filetools import select_ROI_number,\
        replace_negative_values
    # selects the label number corresponding to label name
    label_number = select_ROI_number(self.regions_nomenclature.fullPath(),
                                     self.region)

    # matrix smoothing: -s in millimetres
    context.system("AimsSparseMatrixSmoothing",
                   "-i", self.complete_individual_matrix,
                   "-m", self.individual_white_mesh,
                   "-o", self.complete_matrix_smoothed,
                   "-s", self.smoothing,
                   "-l", self.regions_parcellation,
                   "-p", label_number)

    replace_negative_values(self.complete_individual_matrix.fullPath())
