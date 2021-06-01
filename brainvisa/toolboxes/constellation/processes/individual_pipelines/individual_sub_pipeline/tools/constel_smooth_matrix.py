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
from brainvisa.processes import Boolean
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import OpenChoice
from brainvisa.processes import Choice
from brainvisa.processes import ValidationError
from brainvisa.data import neuroHierarchy

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
        from constel.lib.utils.filetools import select_ROI_number
        from constel.lib.utils.matrixtools import replace_negative_values
        from constel.lib.utils.filetools import read_nomenclature_file
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ---------------------------Header--------------------------------------------


name = "Smoothing of the Individual Matrix."
userLevel = 2

signature = Signature(
    "regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File", section="Nomenclature"),

    "region", OpenChoice(section="Study parameters"),
    # --inputs--
    "complete_individual_matrix", ReadDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "no",
                            "intersubject": "no"},
        section="Input matrix"),

    "individual_white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"},
        section="Freesurfer data"),

    "regions_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"},
        section="Freesurfer data"),

    "smoothing", Float(section="Options"),

    # --outputs--
    "complete_matrix_smoothed", WriteDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "no",
                            "intersubject": "no"},
        section="Smoothed matrix"),
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters"""

    from constel.lib.utils.filetools import read_nomenclature_file

    # default values
    self.smoothing = 3.
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

    def reset_label(self, dummy):
        """Read and/or reset the region parameter.

        This callback reads the labels nomenclature and proposes them in the
        signature 'region' of process.
        It also resets the region parameter to default state after
        the nomenclature changes.
        """
        current = self.region
        self.setValue("region", current, True)
        if self.regions_nomenclature is not None:
            s = [("Select a region in this list", None)]
            # temporarily set a value which will remain valid
            self.region = s[0][1]
            s += read_nomenclature_file(
                self.regions_nomenclature.fullPath(), mode=2)
            self.signature["region"].setChoices(*s)
            if isinstance(self.signature["region"], OpenChoice):
                self.signature["region"] = Choice(*s,
                                                  section="Study parameters")
                self.changeSignature(self.signature)
            if current not in s:
                self.setValue("region", s[0][1], True)
            else:
                self.setValue("region", current, True)

    # link of parameters for autocompletion
    self.linkParameters(None,
                        "regions_nomenclature",
                        reset_label)
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
    from constel.lib.utils.filetools import select_ROI_number
    from constel.lib.utils.matrixtools import replace_negative_values
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
