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
from brainvisa.processes import ValidationError
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem

# Soma module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("AimsMeshWatershed.py"):
        raise ValidationError(
            "Please make sure that aims module is installed.")


# ---------------------------Header--------------------------------------------


name = "Individual High Connectivity Regions"
userLevel = 2

signature = Signature(
    # inputs
    "normed_individual_profile", ReadDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"ends_labelled": "all",
                            "normed": "yes",
                            "intersubject": "no"}),
    "individual_white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes",
                            "averaged": "No"}),

    # outputs
    "reduced_individual_profile", WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "yes",
                            "roi_filtered": "no",
                            "intersubject": "no",
                            "step_time": "no",
                            "measure": "no"}),
)


# ---------------------------Function------------------------------------------


def initialization(self):
    """Provides default values and link of parameters.
    """
    self.linkParameters("reduced_individual_profile",
                        "normed_individual_profile")


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'AimsMeshWatershed'.

    Watershed is computed providing a set of target regions.
    """
    context.pythonSystem("AimsMeshWatershed.py",
                         self.normed_individual_profile,
                         self.individual_white_mesh,
                         self.reduced_individual_profile,
                         "--threshold", 0.05,
                         "--mode", "or")
