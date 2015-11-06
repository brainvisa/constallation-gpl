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
* executes the command 'AimsMeshWatershed'

Main dependencies: axon python API, soma-base

Author: Sandrine Lefranc, 2015
"""

#----------------------------Imports-------------------------------------------


#python system
import sys

# Axon python API module
from brainvisa.processes import ValidationError, Signature, ReadDiskItem, \
    WriteDiskItem

# soma-base module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("AimsMeshWatershed.py"):
        raise ValidationError(
            "Please make sure that aims module is installed.")


#----------------------------Header--------------------------------------------


name = "Reduced Profile"
userLevel = 2

signature = Signature(
    # inputs
    "normed_individual_profile", ReadDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"normed": "Yes"}),
    "white_mesh", ReadDiskItem("White Mesh", "Aims mesh formats",
                               requiredAttributes={"side": "both",
                                                   "vertex_corr": "Yes",
                                                   "averaged": "No"}),

    # outputs
    "reduced_individual_profile", WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "Yes",
                            "roi_filtered": "No",
                            "averaged": "No",
                            "intersubject": "No",
                            "step_time": "No"}),
)


#----------------------------Function------------------------------------------


def initialization(self):
    """Provides default values and link of parameters.
    """
    self.linkParameters("reduced_individual_profile", "normed_individual_profile")


#----------------------------Main program--------------------------------------


def execution(self, context):
    """ Watershed is computed providing a set of target regions
    """
    commandMeshWatershedProcessing = [
        sys.executable, find_in_path("AimsMeshWatershed.py"),
        self.normed_individual_profile,
        self.white_mesh,
        self.reduced_individual_profile]
    context.system(*commandMeshWatershedProcessing)
