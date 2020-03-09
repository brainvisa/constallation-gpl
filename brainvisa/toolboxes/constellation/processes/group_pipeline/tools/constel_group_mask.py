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
* executes the command 'constel_connectivity_profile_overlap_mask':
the mask of the all individual profiles is computed.

Main dependencies: axon python API, soma, constel

Author: Sandrine Lefranc, 2015
"""

# ----------------------------Imports------------------------------------------


# python system module
from __future__ import absolute_import
import os

# axon python API module
from brainvisa.processes import Signature, ListOf, ReadDiskItem, String, \
    WriteDiskItem, ValidationError

# soma module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constel_connectivity_profile_overlap_mask.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ----------------------------Header-------------------------------------------


name = "Group Connectivity Mask"
userLevel = 2

signature = Signature(
    # --inputs--
    "mean_individual_profiles", ListOf(
        ReadDiskItem("Connectivity Profile Texture", "Aims texture formats",
                     requiredAttributes={"ends_labelled": "all",
                                         "normed": "no",
                                         "intersubject": "no"})),
    "subjects_group", ReadDiskItem("Group definition", "XML"),
    "new_study_name", String(),

    # --outputs--
    "group_mask", WriteDiskItem(
        "Mask Texture", "Aims texture formats"), )


# ----------------------------Functions----------------------------------------


def initialization(self):
    """Provides link of parameters"""

    # optional value
    self.setOptional("new_study_name")

    # link of parameters
    def link_mask(self, dummy):
        """Function of link between mask and group parameters."""
        if self.subjects_group and self.mean_individual_profiles:
            atts = dict(self.mean_individual_profiles[0].hierarchyAttributes())
            atts["group_of_subjects"] = os.path.basename(
                os.path.dirname(self.subjects_group.fullPath()))
            if self.new_study_name:
                atts["studyname"] = self.new_study_name
            else:
                atts["studyname"] = \
                    self.mean_individual_profiles[0].get("studyname")
            return self.signature["group_mask"].findValue(atts)

    # link of parameters for autocompletion
    self.linkParameters(
        "group_mask",
        ("mean_individual_profiles", "subjects_group", "new_study_name"),
        link_mask)


# ----------------------------Main program-------------------------------------


def execution(self, context):
    """Run the command 'constel_connectivity_profile_overlap_mask'.
    """
    context.pythonSystem("constel_connectivity_profile_overlap_mask.py",
                         self.mean_individual_profiles,
                         self.group_mask)
