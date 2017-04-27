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
* executes the command 'constel_calculate_dice_index.py'

Main dependencies: axon python API, soma, constel

Author: Sandrine Lefranc, 2016
"""

#----------------------------Imports-------------------------------------------


# python system module
import os
import sys

# axon python API module
from brainvisa.processes import Signature, ListOf, ReadDiskItem, String, \
    WriteDiskItem, ValidationError, Integer

# soma module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constel_calculate_dice_index.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


#----------------------------Header--------------------------------------------


name = "Dice Index"
userLevel = 2

signature = Signature(
    # --inputs--
    "individual_clustering",
        ReadDiskItem("Connectivity ROI Texture", "Aims texture formats",
                      requiredAttributes={"roi_autodetect": "no",
                                          "roi_filtered": "no",
                                          "intersubject": "yes",
                                          "step_time": "yes",
                                          "measure": "no"}),
    "nb_individual_clusters", Integer(),
    "atlas_clustering",
        ReadDiskItem("Connectivity ROI Texture", "Aims texture formats",
                     requiredAttributes={"roi_autodetect": "no",
                                         "roi_filtered": "no",
                                         "intersubject": "yes",
                                         "step_time": "yes",
                                         "measure": "no"}),
    "nb_atlas_clusters", Integer(),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),

    # --output--
    "stem_plot_pdffile", String(),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides link of parameters"""
    self.nb_individual_clusters = 5
    self.nb_atlas_clusters = 5


#----------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constel_clusters_from_atlas'.
    """
    # Check the input parameter
    if (self.nb_individual_clusters < 2 or self.nb_atlas_clusters < 2):
        raise ValueError("The cluster number must be largest tha '2'.")
    
    # In the Constellation toolbox, the minimun of clusters is '2'.
    # For nb_clusters = 2, python indexation is 0.
    individual_time_step = self.nb_individual_clusters - 2
    atlas_time_step = self.nb_atlas_clusters - 2
    
    # Return the cortical region name
    cortical_region = self.atlas_clustering.get("gyrus")

    # Compute the Dice index and write the stem plot
    context.pythonSystem("constel_calculate_dice_index.py",
                         self.individual_clustering,
                         self.atlas_clustering,
                         self.white_mesh,
                         individual_time_step,
                         atlas_time_step,
                         cortical_region,
                         self.stem_plot_pdffile)

