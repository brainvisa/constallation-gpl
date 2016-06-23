#!/usr/bin/env python
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
*
*

Main dependencies:

Author: Sandrine Lefranc
"""


#----------------------------Imports-------------------------------------------


# axon python API module
from brainvisa.processes import *

# soma module
from soma.path import find_in_path


def validation():
    """
    """
    if not find_in_path("AimsMergeLabelsFromTexture.py"):
        raise ValidationError("aims module is not here.")
    if not find_in_path("AimsExtractLabelsFromTexture.py"):
        raise ValidationError("aims module is not here.")


#----------------------------Header--------------------------------------------


name = "Merge Labels From texture"
userLevel = 2

signature = Signature(
    #--inputs--
    "gyri_texture", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "old_labels", ListOf(Integer()),
    "new_label", Integer(),  
  
    #--outputs--
    "new_gyri_texture", WriteDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side":"both", "vertex_corr":"Yes"}),
    "keep_only_merged_regions", Boolean(),)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """
    """
    self.keep_only_merged_regions = False


#----------------------------Main Program--------------------------------------


def execution(self, context):
    """
    """
    cmd_args = []
    for n in self.old_labels:
        cmd_args += ["-l", n]
    cmd_args += ["-i", self.gyri_texture, "-n", self.new_label,
                 "-o", self.new_gyri_texture]
    if not self.keep_only_merged_regions:
        context.system("python",
                       find_in_path("AimsMergeLabelsFromTexture.py"),
                       *cmd_args)
    else:
        context.system("python",
                       find_in_path("AimsExtractLabelsFromTexture.py"),
                       *cmd_args)
