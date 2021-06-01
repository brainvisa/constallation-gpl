###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################


# --------------------------Imports-------------------------------------------


# Axon python API module
from __future__ import absolute_import
from brainvisa.processes import String
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError
from brainvisa.processes import Boolean
from brainvisa.processes import OpenChoice
from brainvisa.processes import Choice
from brainvisa.data import neuroHierarchy

# Soma module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    cmd = "constelMeanConnectivityProfileFromMatrix"
    if not find_in_path(cmd):
        raise ValidationError(
            "'{0}' is not contained in PATH environnement variable. "
            "Please make sure that constel package is installed.".format(cmd))
    try:
        from constel.lib.utils.filetools import select_ROI_number
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")

# ---------------------------Header--------------------------------------------


name = "Mean Individual Profile From Smoothed Matrix"
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
        section="Smoothed matrix"),

    "regions_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"},
        section="Freesurfer data"),

    "erase_smoothed_matrix", Boolean(section="Options"),

    # --ouputs--
    "mean_individual_profile", WriteDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"ends_labelled": "all",
                            "normed": "no",
                            "intersubject": "no"},
        section="Mean profile"),
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters"""
    from constel.lib.utils.filetools import read_nomenclature_file

    # default value
    self.erase_smoothed_matrix = True
    self.regions_nomenclature = self.signature[
        "regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_matrix2label(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'region'.
        """
        if self.complete_matrix_smoothed is not None:
            s = str(self.complete_matrix_smoothed.get("gyrus"))
            name = self.signature["region"].findValue(s)
        return name

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
                        "complete_matrix_smoothed",
                        link_matrix2label)
    self.linkParameters("mean_individual_profile",
                        "complete_matrix_smoothed")


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constelMeanConnectivityProfileFromMatrix'.

    Compute the connectivity profile (no normalize) from connectivity matrix.
    """
    from constel.lib.utils.filetools import select_ROI_number
    # selects the label number corresponding to label name
    label_number = select_ROI_number(self.regions_nomenclature.fullPath(),
                                     self.region)

    context.system("constelMeanConnectivityProfileFromMatrix",
                   "-connfmt", "binar_sparse",
                   "-connmatrixfile", self.complete_matrix_smoothed,
                   "-outconntex", self.mean_individual_profile,
                   "-seedregionstex", self.regions_parcellation,
                   "-seedlabel", label_number,
                   "-type", "seed_mean_connectivity_profile",
                   "-normalize", 0,
                   "-verbose", 1)

    if self.erase_smoothed_matrix:
        self.complete_matrix_smoothed.eraseFiles(remove_from_database=True)
