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

#----------------------------Imports-------------------------------------------


# system module
import os
import sys

# axon python API module
from brainvisa.processes import ListOf
from brainvisa.processes import Boolean
from brainvisa.processes import Integer
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import getAllFormats
from brainvisa.processes import ValidationError

# soma module
from soma.path import find_in_path


def validate(self):
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constel_calculate_asw.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


#----------------------------Header--------------------------------------------


name = "Average Silhouette Width"
userLevel = 2

signature = Signature(
    #--inputs
    "reduced_matrices", ListOf(
        ReadDiskItem("Connectivity Matrix", "GIS image",
                     requiredAttributes={"ends_labelled": "mixed",
                                         "reduced": "No",
                                         "dense": "No",
                                         "intersubject": "Yes"})),
    "kmax", Integer(),

    #--outputs--
    "outpdffile", WriteDiskItem("Any Type", getAllFormats()),
    "autoscale_y", Boolean(),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """
    """
    self.kmax = 12
    self.autoscale_y = True

    def link_outdir(self, dummy):
        """
        """
        if self.reduced_matrices:
            for matrix in self.reduced_matrices:
                name = os.path.dirname(os.path.dirname(
                                       os.path.dirname(matrix.fullPath())))
                print name
            filename = os.path.join(name, "asw.pdf")
            return filename

    self.linkParameters("outpdffile", "reduced_matrices", link_outdir)


#----------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constel_calculate_asw.py'.
    """
    if not self.autoscale_y:
        arg = "-q"
    else:
        arg = "-c"

    context.system(sys.executable,
                   find_in_path("constel_calculate_asw.py"),
                   self.reduced_matrices,
                   self.kmax,
                   self.outpdffile,
                   arg)
