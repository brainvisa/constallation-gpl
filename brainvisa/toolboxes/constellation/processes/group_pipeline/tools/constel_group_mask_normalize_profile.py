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
* this process executes the command 'constel_norm_profile': normalize the mean
  profile.

Main dependencies: axon python API, soma, constel

Author: Sandrine Lefranc, 2015
"""

# ----------------------------Imports------------------------------------------


# python system module
from __future__ import absolute_import

# Axon python API module
from brainvisa.processes import Signature, ReadDiskItem, WriteDiskItem, \
    ValidationError

# soma module
from soma.path import find_in_path


# Plot constel module
def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constel_norm_profile.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ----------------------------Functions----------------------------------------


name = "Mask and Normalize Group Profile"
userLevel = 2

# Argument declaration
signature = Signature(
    "group_mask", ReadDiskItem("Mask Texture", "Aims texture formats",
                               section="Inputs"),
    "group_profile", ReadDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"ends_labelled": "all",
                            "normed": "no",
                            "intersubject": "yes"},
        section="Inputs"),

    "normed_group_profile", WriteDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"ends_labelled": "all",
                            "normed": "yes",
                            "intersubject": "yes"},
        section="Group profile outputs"))


def initialization(self):
    """Provides default values and link of parameters"""

    def link_normprofile(self, dummy):
        """
        """
        if self.group_profile is not None:
            atts = dict()
            atts["_database"] = self.group_profile.get("_database")
            atts["center"] = self.group_profile.get("center")
            atts["group_of_subjects"] = self.group_profile.get(
                "group_of_subjects")
            atts["studyname"] = self.group_profile.get("studyname")
            atts["method"] = self.group_profile.get("method")
            atts["smoothing"] = self.group_profile.get("smoothing")
            atts["gyrus"] = self.group_profile.get("gyrus")
            atts['acquisition'] = ""
            atts['analysis'] = ""
            atts['tracking_session'] = ""
            atts['smallerlength'] = self.group_profile.get("smallerlength")
            atts['greaterlength'] = self.group_profile.get("greaterlength")
            atts["intersubject"] = "yes"
            atts["normed"] = "yes"
            return self.signature["normed_group_profile"].findValue(atts)

    self.linkParameters("group_profile", "group_mask")
    self.linkParameters("normed_group_profile", "group_profile",
                        link_normprofile)


# ----------------------------Main program-------------------------------------


def execution(self, context):
    """Execute the command 'constel_norm_profile'.

    Create a group profile normed.
    """
    context.pythonSystem("constel_norm_profile.py",
                         self.group_mask,
                         self.group_profile,
                         self.normed_group_profile)
