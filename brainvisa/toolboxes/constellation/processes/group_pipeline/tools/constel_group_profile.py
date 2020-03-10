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
* this process executes the command 'constel_avg_connectivity_profile':
the mean group profile is computed.

Main dependencies: axon python API, soma, constel

Author: sandrine.lefranc@cea.fr
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
    if not find_in_path("constel_avg_connectivity_profile.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ----------------------------Header-------------------------------------------


name = "Group Connectivity Profile"
userLevel = 2

signature = Signature(
    # --inputs--
    "normed_individual_profiles", ListOf(ReadDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"ends_labelled": "all",
                            "normed": "yes",
                            "intersubject": "no"})),
    "subjects_group", ReadDiskItem("Group definition", "XML"),
    "new_study_name", String(),

    # --outputs--
    "group_profile", WriteDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"ends_labelled": "all",
                            "normed": "no",
                            "intersubject": "yes"}),
)


# ----------------------------Functions----------------------------------------


def initialization(self):
    """Provides default values and link of parameters"""

    # optional value
    self.setOptional("new_study_name")

    def link_group_profiles(self, dummy):
        """Function of link between individual profiles and group profile.
        """
        if self.subjects_group and self.normed_individual_profiles:
            atts = dict()
            atts["_database"] = self.normed_individual_profiles[0].get(
                "_database")
            atts["center"] = self.normed_individual_profiles[0].get("center")
            atts["group_of_subjects"] = os.path.basename(
                os.path.dirname(self.subjects_group.fullPath()))
            if self.new_study_name is None:
                atts["studyname"] = self.normed_individual_profiles[0].get(
                    "studyname")
            else:
                atts["studyname"] = self.new_study_name
            atts["method"] = self.normed_individual_profiles[0].get("method")
            atts["smoothing"] = self.normed_individual_profiles[0].get(
                "smoothing")
            atts["gyrus"] = self.normed_individual_profiles[0].get("gyrus")
            atts['acquisition'] = ""
            atts['analysis'] = ""
            atts['tracking_session'] = ""
            atts['smallerlength'] = self.normed_individual_profiles[0].get(
                "smallerlength")
            atts['greaterlength'] = self.normed_individual_profiles[0].get(
                "greaterlength")
            atts["intersubject"] = "yes"
            atts["normed"] = "no"
            return self.signature["group_profile"].findValue(atts)

    # link of parameters for autocompletion
    self.linkParameters(
        "group_profile",
        ("normed_individual_profiles", "subjects_group", "new_study_name"),
        link_group_profiles)


# ----------------------------Main program-------------------------------------


def execution(self, context):
    """Run the command 'constel_avg_connectivity_profile'.

    A connectivity profile is determinated on a range of subjects
    (for a group of subjects)
    """
    context.pythonSystem("constel_avg_connectivity_profile.py",
                         self.normed_individual_profiles,
                         self.group_profile)
