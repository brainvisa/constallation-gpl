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


# ---------------------------Imports-------------------------------------------


# system module
from __future__ import absolute_import

# axon python API module
from brainvisa.processes import ListOf
from brainvisa.processes import Integer
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError

# soma module
from soma import aims


def validation(self):
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    try:
        from constel.lib.utils.texturetools import concatenate_texture
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")

# ---------------------------Header--------------------------------------------


name = 'Concatenate the ROI segmentations on the same mesh'
userLevel = 2


signature = Signature(
    "ROI_clustering", ListOf(ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "no",
                            "roi_filtered": "no",
                            "intersubject": "yes",
                            "step_time": "yes",
                            "measure": "no"})),
    "time_step", ListOf(Integer()),
    "mesh", ReadDiskItem("White Mesh", "Aims mesh formats"),
    "concatenated_ROIseg", WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats")
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """
    """
    pass


# ---------------------------Main Program--------------------------------------


def execution(self, context):
    """
    """
    from constel.lib.utils.texturetools import concatenate_texture
    final_rseg = concatenate_texture(self.ROI_clustering, self.time_step)
    aims.write(final_rseg, self.concatenated_ROIseg.fullPath())
