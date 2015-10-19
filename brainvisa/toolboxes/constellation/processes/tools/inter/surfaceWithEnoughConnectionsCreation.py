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
* this process executes the command 'constelConnectivityProfileOverlapMask'

Main dependencies: Axon python API, Soma-base, constel

Author: sandrine.lefranc@cea.fr
"""

#----------------------------Imports-------------------------------------------


# python system module
import os
import sys

# axon python API module
from brainvisa.processes import Signature, ListOf, ReadDiskItem, String, \
    WriteDiskItem, ValidationError

# soma-base module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constelConnectivityProfileOverlapMask.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


#----------------------------Header--------------------------------------------


name = "Creation of a mask"
userLevel = 2

signature = Signature(
    # inputs
    "connectivity_profiles", ListOf(
        ReadDiskItem("Connectivity Profile Texture", "Aims texture formats",
                     requiredAttributes={"normed": "No",
                                         "thresholded": "No",
                                         "averaged": "No",
                                         "intersubject": "No"})),
    "group", ReadDiskItem("Group definition", "XML"),
    "new_name", String(),

    # outputs
    "mask", WriteDiskItem("Mask Texture", "Aims texture formats"), )


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides link of parameters"""

    # optional value
    self.setOptional("new_name")

    # link of parameters
    def link_mask(self, dummy):
        """Function of link between mask and group parameters."""
        if (self.group and self.connectivity_profiles) is not None:
            atts = dict(self.connectivity_profiles[0].hierarchyAttributes())
            atts["group_of_subjects"] = os.path.basename(
                os.path.dirname(self.group.fullPath()))
            if self.new_name is not None:
                atts["texture"] = self.new_name
            print atts
            return self.signature["mask"].findValue(atts)

    # link of parameters for autocompletion
    self.linkParameters("mask", ("connectivity_profiles", "group", "new_name"),
                        link_mask)


#----------------------------Main program--------------------------------------


def execution(self, context):
    # execute the command
    context.system(sys.executable,
                   find_in_path("constelConnectivityProfileOverlapMask.py"),
                   self.connectivity_profiles,
                   self.mask)
