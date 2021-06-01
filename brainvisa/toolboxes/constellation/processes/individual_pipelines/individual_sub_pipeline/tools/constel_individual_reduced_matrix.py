###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################


# ---------------------------Imports-------------------------------------------


# Axon python API modules
from __future__ import absolute_import
from brainvisa.processes import String
from brainvisa.processes import Boolean
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError
from brainvisa.processes import OpenChoice
from brainvisa.processes import Choice
from brainvisa.data import neuroHierarchy

# Soma module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constelConnectionDensityTexture"):
        raise ValidationError(
            "constelConnectionDensityTexture is not contained in PATH"
            "environnement variable or please make sure that constellation "
            "is installed.")
    try:
        from constel.lib.utils.filetools import select_ROI_number
        from constel.lib.utils.matrixtools import save_normalization
        from constel.lib.utils.filetools import read_nomenclature_file
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ---------------------------Header--------------------------------------------


name = "Reduced Individual Matrix From Filtered Reduced Profile"
userLevel = 2

signature = Signature(
    "regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File", section="Nomenclature"),

    "region", OpenChoice(section="Study parameters"),

    # --inputs--
    "complete_matrix_smoothed", ReadDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "no",
                            "intersubject": "no",
                            "individual": "yes"},
        section="Inputs"),
    "filtered_reduced_individual_profile", ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "yes",
                            "roi_filtered": "yes",
                            "intersubject": "no",
                            "step_time": "no",
                            "measure": "no"},
        section="Inputs"),

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

    "normalize", Boolean(section="Options"),
    "erase_smoothed_matrix", Boolean(section="Options"),

    # --outputs--
    "reduced_individual_matrix", WriteDiskItem(
        "Connectivity Matrix", "Aims matrix formats",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "yes",
                            "intersubject": "no",
                            "individual": "yes"},
        section="Reduced matrix"),
)


# ---------------------------Function--------------------------------------


def initialization(self):
    """Provides default value and link of parameters"""
    # default value
    self.regions_nomenclature = self.signature[
        "regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})
    self.normalize = True
    self.erase_smoothed_matrix = True

    def reset_label(self, dummy):
        """Read and/or reset the region parameter.

        This callback reads the labels nomenclature and proposes them in the
        signature 'region' of process.
        It also resets the region parameter to default state after
        the nomenclature changes.
        """
        from constel.lib.utils.filetools import read_nomenclature_file
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

    def link_matrix2label(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'region'.
        """
        if self.complete_matrix_smoothed is not None:
            s = str(self.complete_matrix_smoothed.get("gyrus"))
            return s

    # link of parameters for autocompletion
    self.linkParameters(None,
                        "regions_nomenclature",
                        reset_label)
    self.linkParameters("filtered_reduced_individual_profile",
                        "complete_matrix_smoothed")
    self.linkParameters("region",
                        "complete_matrix_smoothed",
                        link_matrix2label)
    self.linkParameters("reduced_individual_matrix",
                        "filtered_reduced_individual_profile")


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """ Compute reduced connectivity matrix M(target regions, patch vertices)
    """
    from constel.lib.utils.filetools import select_ROI_number
    from constel.lib.utils.matrixtools import save_normalization
    # selects the ROI label corresponding to ROI name
    label_number = select_ROI_number(self.regions_nomenclature.fullPath(),
                                     self.region)

    # normalization of the reduced matrix
    if self.normalize:
        norm = 1
    else:
        norm = 0

    # M(target regions, patch vertices)
    context.system(
        "constelConnectionDensityTexture",
        "-mesh", self.individual_white_mesh,
        "-connmatrixfile", self.complete_matrix_smoothed,
        "-targetregionstex", self.filtered_reduced_individual_profile,
        "-seedregionstex", str(self.regions_parcellation),
        "-seedlabel", label_number,
        "-type", "seedVertex_to_targets",
        "-connmatrix", self.reduced_individual_matrix,
        "-normalize", norm,
        "-verbose", 1)

    # save the normalization values
    if not self.normalize:
        save_normalization(self.reduced_individual_matrix.fullPath())

    if self.erase_smoothed_matrix:
        self.complete_matrix_smoothed.eraseFiles(remove_from_database=True)
