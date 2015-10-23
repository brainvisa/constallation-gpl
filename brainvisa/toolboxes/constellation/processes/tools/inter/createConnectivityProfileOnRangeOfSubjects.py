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
    - the parameters of a process (Signature),
    - the parameters initialization
    - the linked parameters
* this process executes the command 'constelAvgConnectivityProfile'

Main dependencies: Axon python API, Soma-base, constel

Author: sandrine.lefranc@cea.fr
"""


#----------------------------Imports-------------------------------------------


# python system module
import os
import sys

# Axon python API module
from brainvisa.processes import Signature, ListOf, ReadDiskItem, String, \
    WriteDiskItem, ValidationError

# soma-base module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constelAvgConnectivityProfile.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


#----------------------------Header--------------------------------------------


name = "Connectivity Profile of Group"
userLevel = 2

signature = Signature(
    # --inputs--
    "normed_connectivity_profiles", ListOf(ReadDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"normed": "Yes",
                            "thresholded" :"Yes",
                            "averaged" :"No",
                            "intersubject" :"No"})),
    "group", ReadDiskItem("Group definition", "XML"),
    "new_name", String(),
    
    # --outputs--
    "normed_connectivity_profile_nb", ListOf(WriteDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"normed": "Yes",
                            "thresholded": "Yes",
                            "averaged": "No",
                            "intersubject": "Yes"})),
    "group_connectivity_profile", WriteDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"normed": "No",
                            "thresholded": "No",
                            "averaged": "Yes",
                            "intersubject": "Yes"}),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters"""

    # optional value
    self.setOptional("new_name")

    def link_profiles(self, dummy):
        """Function of link between individual profiles and normed profiles.
        """
        profiles = []
        if (self.normed_connectivity_profiles and self.group) is not None:
            for profile in self.normed_connectivity_profiles:
                atts = dict()
                atts["_database"] = profile.get("_database")
                atts["center"] = profile.get("center")
                atts["subject"] = profile.get("subject")
                atts["smoothing"] = profile.get("smoothing")
                atts["group_of_subjects"] = os.path.basename(
                    os.path.dirname(self.group.fullPath()))
                atts["study"] = profile.get("study")
                atts["gyrus"] = profile.get("gyrus")
                atts['acquisition'] = ''
                atts['analysis'] = ''
                atts['tracking_session'] = ''
                if self.new_name is None:
                    atts["texture"] = profile.get("texture")
                else:
                    atts["texture"] = self.new_name
                profile = self.signature[
                    "normed_connectivity_profile_nb"].contentType.findValue(atts)
                if profile is not None:
                    profiles.append(profile)
            return profiles

    def link_group_profiles(self, dummy):
        """Function of link between individual profiles and group profile.
        """
        if (self.group and self.normed_connectivity_profiles) is not None:
            atts = dict()
            atts["_database"] = self.normed_connectivity_profiles[0].get("_database")
            atts["center"] = self.normed_connectivity_profiles[0].get("center")
            atts["group_of_subjects"] = os.path.basename(
                os.path.dirname(self.group.fullPath()))
            if self.new_name is None:
                atts["texture"] = self.normed_connectivity_profiles[0].get("texture")
            else:
                atts["texture"] = self.new_name
            atts["study"] = self.normed_connectivity_profiles[0].get("study")
            atts["smoothing"] = self.normed_connectivity_profiles[0].get("smoothing")
            atts["gyrus"] = self.normed_connectivity_profiles[0].get("gyrus")
            atts['acquisition'] = ''
            atts['analysis'] = ''
            atts['tracking_session'] = ''
            atts["intersubject"] = "Yes"
            atts["averaged"] = "Yes"
            atts["normed"] = "No"
            atts["thresholded"] = "No"
            return self.signature["group_connectivity_profile"].findValue(atts)

    # link of parameters for autocompletion
    self.linkParameters("normed_connectivity_profile_nb", (
        "normed_connectivity_profiles", "group", "new_name"), link_profiles)
    self.linkParameters(
        "group_connectivity_profile",
        ("normed_connectivity_profiles", "group", "new_name"),
        link_group_profiles)


#----------------------------Main program--------------------------------------


def execution(self, context):
    """ A connectivity profile is determinated on a range of subjects
    (for a group of subjects)
    """
    context.system(sys.executable,
                   find_in_path("constelAvgConnectivityProfile.py"),
                   self.normed_connectivity_profiles,
                   self.normed_connectivity_profile_nb,
                   self.group_connectivity_profile)
