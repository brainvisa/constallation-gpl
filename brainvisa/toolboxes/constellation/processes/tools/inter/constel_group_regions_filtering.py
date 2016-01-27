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
* this process executes the command 'AimsMeshWatershed.py' and
  'constelFilteringWatershed.py'

Main dependencies: Axon python API, Soma-base, constel

Author: Sandrine Lefranc
"""

#----------------------------Imports-------------------------------------------


# python module
import sys

# axon python API module
from brainvisa.processes import Signature, ReadDiskItem, WriteDiskItem, \
    ValidationError

# soma-base module
from soma import aims
from soma.path import find_in_path

# constel module
try:
    from constel.lib.texturetools import remove_labels
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


name = "Group Regions Filtering"
userLevel = 2

signature = Signature(
    # --inputs--
    "normed_group_profile", ReadDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"normed": "Yes",
                            "thresholded": "Yes",
                            "averaged": "Yes",
                            "intersubject": "Yes"}),
    "average_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes",
                            "averaged": "Yes"}),

    # --outputs--
    "reduced_group_profile", WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "Yes",
                            "roi_filtered": "No",
                            "averaged": "Yes",
                            "intersubject": "Yes",
                            "step_time": "No"}),
    "filtered_reduced_group_profile", WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "Yes",
                            "roi_filtered": "Yes",
                            "averaged": "Yes",
                            "intersubject": "Yes",
                            "step_time": "No"}),
)


#----------------------------Function------------------------------------------


def initialization(self):
    """Provides default values and link of parameters"""
    self.linkParameters("reduced_group_profile", "normed_group_profile")
    self.linkParameters("filtered_reduced_group_profile", "normed_group_profile")


#----------------------------Main program--------------------------------------


def execution(self, context):
    """ A watershed was computed on the joint patch cortical connectivity
    profile texture in order to split the cortical surface into catchment
    basins. Small basins are agglomerated to larger ones based on their
    depth and area. This set of T regions will be called target regions.
    A watershed is performed to obtain different patches of interest.
    """
    context.system("AimsMeshWatershed.py",
                   self.normed_group_profile,
                   self.average_mesh,
                   self.reduced_group_profile,
                   "--threshold", 0.05,
                   "--mode", "or")

    # execute the command
    context.system(sys.executable,
                   find_in_path("constelFilteringWatershed.py"),
                   self.reduced_group_profile,
                   self.filtered_reduced_group_profile)
