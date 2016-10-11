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
    - the signature of the inputs/ouputs,
    - the initialization (by default) of the inputs,
    - the interlinkages between inputs/outputs.
* this process executes the command 'constelRemoveInternalConnections.py'.

Main dependencies: Axon python API, Soma-base, constel

Author: Sandrine Lefranc, 2015
"""

#----------------------------Imports-------------------------------------------


# Axon python API module
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError
from brainvisa.processes import OpenChoice
from brainvisa.processes import Choice
from brainvisa.processes import String
from brainvisa.processes import ListOf

# constel module
try:
    from constel.lib.utils.filetools import read_file
    from constel.lib.utils.filetools import select_ROI_number
except:
    pass


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    try:
        import constel
    except:
        raise ValidationError(
            "Please make sure that constel module is installed.")


#----------------------------Header--------------------------------------------


name = "Mean Individual Profile Normalization"
userLevel = 2

signature = Signature(
    # --inputs--
    "mean_individual_profile", ReadDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"normed": "No",
                            "thresholded": "No",
                            "averaged": "No",
                            "intersubject": "No"}),
    "cortical_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "cortical_region", String(),

    # --outputs--
    "normed_individual_profile", WriteDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"normed": "Yes",
                            "thresholded": "Yes",
                            "averaged": "No",
                            "intersubject": "No"}),
    "keep_regions", OpenChoice(),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters.
    """
    # default value
    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_keep_regions(self, dummy):
        """
        """
        if self.cortical_regions_nomenclature is not None:
            s = []
            s += read_file(
                self.cortical_regions_nomenclature.fullPath(), mode=2)
            self.signature["keep_regions"] = ListOf(Choice(*s))
            self.changeSignature(self.signature)

    def link_matrix2label(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'cortical_region'.
        """
        if self.mean_individual_profile is not None:
            s = str(self.mean_individual_profile.get("gyrus"))
            name = self.signature["cortical_region"].findValue(s)
        return name

    # link of parameters for autocompletion
    self.linkParameters(
        "cortical_region", "mean_individual_profile", link_matrix2label)
    self.linkParameters(
        "normed_individual_profile", "mean_individual_profile")
    self.linkParameters(
        "keep_regions", "cortical_regions_nomenclature",
        link_keep_regions)


#----------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constelRemoveInternalConnections.py'.

    STEP 1/2: Remove internals connections of patch.
    STEP 2/2: The profile is normalized.
    """
    # selects the label number corresponding to label name
    label_number = select_ROI_number(
        self.cortical_regions_nomenclature.fullPath(), self.cortical_region)

    cmd = ["constelRemoveInternalConnections.py",
           label_number,
           self.mean_individual_profile,
           self.cortical_parcellation,
           self.normed_individual_profile,
          ]

    labels = []
    for region in self.keep_regions:
        l = select_ROI_number(
            self.cortical_regions_nomenclature.fullPath(), region)
        labels.append(l)
    cmd += ["-r"]
    for label in labels:
        cmd += [label]
    context.write(cmd)
    context.pythonSystem(*cmd)
