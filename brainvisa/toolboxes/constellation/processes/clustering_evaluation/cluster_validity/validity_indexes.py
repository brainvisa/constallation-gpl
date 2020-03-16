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
    - the interlinkages between inputs/outputs.
* executes the command "constel_calculate_asw.py": calculate the average
  silhouette width in order to obtain the optimal number of clusters.

Main dependencies: axon python API, soma-base, constel

Author: Sandrine Lefranc, 2015
"""

# ----------------------------Imports------------------------------------------


# system module
from __future__ import absolute_import
import sys

# axon python API module
from brainvisa.processes import Integer
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.data.neuroDiskItems import getAllFormats
from brainvisa.processes import ValidationError

# soma module
from soma.path import find_in_path


def validate(self):
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constel_getting_validity_indexes.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ----------------------------Header-------------------------------------------


name = "Validity Indexes"
userLevel = 2

signature = Signature(
    "matrix", ReadDiskItem(
        "Connectivity Matrix", "GIS image",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "no",
                            "intersubject": "yes",
                            "individual": "yes"}),
    "kmax", Integer(),
    "nbIter", Integer(),
    "indexFile", WriteDiskItem("Any Type", getAllFormats()))


# ----------------------------Functions----------------------------------------


def initialization(self):
    """
    """
    self.kmax = 12
    self.nbIter = 100
    self.indexFile = "/tmp/validityindexes.pdf"


def execution(self, context):
    """
    """
    cortical_region = self.matrix.get("gyrus")

    context.system(sys.executable,
                   find_in_path("constel_getting_validity_indexes.py"),
                   self.matrix,
                   cortical_region,
                   self.nbIter,
                   self.kmax,
                   self.indexFile)
