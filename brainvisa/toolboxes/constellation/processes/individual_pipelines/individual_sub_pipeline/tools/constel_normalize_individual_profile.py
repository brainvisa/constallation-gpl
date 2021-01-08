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
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError
from brainvisa.processes import OpenChoice
from brainvisa.processes import Choice
from brainvisa.processes import String
from brainvisa.processes import ListOf


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    try:
        from constel.lib.utils.filetools import read_nomenclature_file,\
            select_ROI_number
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ---------------------------Header--------------------------------------------


name = "Mean Individual Profile Normalization"
userLevel = 2

signature = Signature(
    "regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File", section="Nomenclature"),

    "region", String(section="Study parameters"),

    # --inputs--
    "mean_individual_profile", ReadDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"ends_labelled": "all",
                            "normed": "no",
                            "intersubject": "no"},
        section="Mean profile"),

    "regions_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"},
        section="Freesurfer data"),

    "keep_regions", ListOf(OpenChoice(), section="Options"),

    # --outputs--
    "normed_individual_profile", WriteDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"ends_labelled": "all",
                            "normed": "yes",
                            "intersubject": "no"},
        section="Normed profile"),
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters.
    """
    from constel.lib.utils.filetools import read_nomenclature_file
    # default value
    self.regions_nomenclature = self.signature[
        "regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_keep_regions(self, dummy):
        """
        """
        if self.regions_nomenclature is not None:
            s = []
            s += read_nomenclature_file(
                self.regions_nomenclature.fullPath(), mode=2)
            self.signature["keep_regions"] = ListOf(Choice(*s),
                                                    section="Options")
            self.changeSignature(self.signature)

    def link_matrix2label(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'region'.
        """
        if self.mean_individual_profile is not None:
            s = str(self.mean_individual_profile.get("gyrus"))
            name = self.signature["region"].findValue(s)
        else:
            name = ""
        return name

    # link of parameters for autocompletion
    self.linkParameters(
        "region", "mean_individual_profile", link_matrix2label)
    self.linkParameters(
        "normed_individual_profile", "mean_individual_profile")
    self.linkParameters(
        "keep_regions", "regions_nomenclature",
        link_keep_regions)


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constel_remove_internal_connections.py'.

    STEP 1/2: Remove internals connections of patch.
    STEP 2/2: The profile is normalized.
    """
    from constel.lib.utils.filetools import select_ROI_number
    # selects the label number corresponding to label name
    label_number = select_ROI_number(self.regions_nomenclature.fullPath(),
                                     self.region)

    cmd = ["constel_remove_internal_connections.py",
           label_number,
           self.mean_individual_profile,
           self.regions_parcellation,
           self.normed_individual_profile]

    labels = []
    for region in self.keep_regions:
        label_number = select_ROI_number(
            self.regions_nomenclature.fullPath(), region)
        labels.append(label_number)
    cmd += ["-r"]
    for label in labels:
        cmd += [label]
    context.pythonSystem(*cmd)
