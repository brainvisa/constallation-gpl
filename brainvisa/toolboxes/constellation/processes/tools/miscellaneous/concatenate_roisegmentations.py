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


# system module
import numpy

from brainvisa.processes import ValidationError, Signature, ReadDiskItem, \
    WriteDiskItem, String, ListOf, Integer, WriteDiskItem

# soma module
from soma import aims

name = 'Concatenate the ROI segmentations on the same mesh'
userLevel = 2


signature = Signature(
    "ROI_clustering", ListOf(ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "No",
                            "roi_filtered": "No",
                            "averaged": "No",
                            "intersubject": "Yes",
                            "step_time": "Yes"})),
    "time_step", ListOf(Integer()),
    "mesh", ReadDiskItem("White Mesh", "Aims mesh formats"),
    "concatenated_ROIseg", WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats")
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """
    """
    pass


def execution(self, context):
    """
    """
    for idx, filename in enumerate(self.ROI_clustering):
        roiseg = aims.read(filename.fullPath())
        rseg = numpy.array(roiseg[self.time_step[idx]].arraydata())
        if idx == 0:
            tmp_rseg = rseg
            max_time_step = max(rseg)
        else:
            l = numpy.unique(rseg)
            if l[0] == 0:
                labels = l.nonzero()[0][::-1]
            else:
                labels = l[::-1]
            for label in labels:
                rseg[rseg == label] = label + max_time_step
            temp = tmp_rseg[:]
            tmp_rseg = [x + y for x, y in zip(temp, rseg)]
            max_time_step = max(rseg)
    final_rseg = aims.TimeTexture_S16()
    final_rseg[0].assign(tmp_rseg)
    aims.write(final_rseg, self.concatenated_ROIseg.fullPath())

