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
"""


# ---------------------------Imports-------------------------------------------


# system module
from __future__ import absolute_import

# axon python API module
from brainvisa.processes import ListOf
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError

# soma module
from soma.path import find_in_path


def validation(self):
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constel_concatenate_textures.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")
# ---------------------------Header--------------------------------------------


name = 'Concatenate the ROI segmentations on the same mesh'
userLevel = 1


signature = Signature(
    "ROI_clustering", ListOf(ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "no",
                            "roi_filtered": "no",
                            "intersubject": "yes",
                            "step_time": "yes",
                            "measure": "no",
                            "optimal": "silhouette"})),
    "concatenated_ROIseg", WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "no",
                            "roi_filtered": "no",
                            "intersubject": "yes",
                            "step_time": "no",
                            "measure": "no",
                            "optimal": "silhouette",
                            "concatenated": "yes"}),
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """
    """
    def link_concatenated(self, dummy):
        """
        """
        if self.ROI_clustering:
            match = dict(self.ROI_clustering[0].hierarchyAttributes())
            if "gyrus" in match:
                del match["gyrus"]
            return self.signature["concatenated_ROIseg"].findValue(match)

    self.linkParameters("concatenated_ROIseg",
                        "ROI_clustering",
                        link_concatenated)


# ---------------------------Main Program--------------------------------------


def execution(self, context):
    """
    """
    cmd = ["constel_concatenate_textures.py",
           self.ROI_clustering,
           self.concatenated_ROIseg]

    context.pythonSystem(*cmd)
