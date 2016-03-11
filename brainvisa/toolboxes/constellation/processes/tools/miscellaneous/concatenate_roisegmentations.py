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


# python system module
from brainvisa.processes import ValidationError, Signature, ReadDiskItem, \
    WriteDiskItem, String, ListOf

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
    "average_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes",
                            "averaged": "Yes"}),
    "concatenated_ROI_segmentations", String()
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """
    """
    pass


def execution(self, context):
    """
    """
    list_roi_clusterings = []
    for roi_clustering in self.ROI_clustering:
        roi = aims.read(roi_clustering.fullPath())
        list_roi_clusterings.append(roi)
    print list_roi_clusterings
    
    for idx, texfile in enumerate(list_roi_clusterings):
        if idx == 0:
            input_roi = list_roi_clusterings[0]
        else:
            vertices_tex = int(input_roi[0].nItem())
            vertices_added = int(texfile[0].nItem())
            value = max(input_roi[0].arraydata())
            for v in xrange(vertices_tex):
                v_tex_add = texfile[0][v]
                v_tex = input_roi[0][v]
                if v_tex_add > 0 and v_tex == 0:
                    input_roi[0][v] = v_tex_add + value
    aims.write(input_roi, self.concatenated_ROI_segmentations)

