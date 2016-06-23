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
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError

# soma module
from soma.path import find_in_path


def validation():
    if not find_in_path("AimsSparseMatrixToDense.py"):
        raise ValidationError("aims module is not here.")


#----------------------------Header--------------------------------------------


name = "Convert Sparse Matrix to Dense"
userLevel = 2

signature = Signature(
    #--inputs--
    "sparse_connectivity_matrix", ReadDiskItem(
        "Connectivity Matrix", "Aims writable volume formats",
        requiredAttributes={"ends_labelled": "mixed",
                            "reduced": "No",
                            "dense": "No",
                            "intersubject": "No"}),

    #--outputs--
    "dense_connectivity_matrix", WriteDiskItem(
        "Connectivity Matrix", "Aims writable volume formats",
        requiredAttributes={"ends_labelled": "mixed",
                            "reduced": "No",
                            "dense": "Yes",
                            "intersubject": "No"}))


#----------------------------Functions-----------------------------------------


def initialization(self):
    """
    """
    self.linkParameters(
        "dense_connectivity_matrix", "sparse_connectivity_matrix")


#----------------------------Main Program--------------------------------------


def execution(self, context):
    """ Execute the command "AimsSparseMatrixToDense".
    """
    context.system("AimsSparseMatrixToDense.py",
                   "-i", self.sparse_connectivity_matrix,
                   "-o", self.dense_connectivity_matrix)

