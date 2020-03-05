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

# ---------------------------Imports-------------------------------------------


# system module
from __future__ import absolute_import
import os

# axon python API module
from brainvisa.processes import Float
from brainvisa.processes import ListOf
from brainvisa.processes import Boolean
from brainvisa.processes import Integer
from brainvisa.processes import Choice
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


# ---------------------------Header--------------------------------------------


name = "Average Silhouette Width"
userLevel = 2

signature = Signature(
    # --inputs
    "reduced_matrices", ListOf(
        ReadDiskItem("Connectivity Matrix", "Aims matrix formats",
                     requiredAttributes={"ends_labelled": "all",
                                         "reduced": "yes",
                                         "intersubject": "yes",
                                         "individual": "yes"})),
    "kmax", Integer(),

    # --outputs--
    "outpdffile", WriteDiskItem("Text File", 'PDF File'),
    "ybound", ListOf(Float()),
    "kmin_type", Choice("none", "min", "avg_pts"),
    "kmin", Integer(),
    "max_avg_points", Float(),
    "save_asw_values", Boolean()
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """
    """
    self.kmax = 12
    self.setOptional("ybound")
    self.kmin_type = "none"
    self.kmin = 0
    self.max_avg_points = 0
    self.save_asw_values = False

    def link_outdir(self, dummy):
        """
        """
        if self.reduced_matrices:
            for matrix in self.reduced_matrices:
                name = os.path.dirname(os.path.dirname(
                                       os.path.dirname(matrix.fullPath())))
            filename = os.path.join(name, "asw.pdf")
            return filename

    self.linkParameters("outpdffile", "reduced_matrices", link_outdir)


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constel_calculate_asw.py'.
    """
    cmd = ["constel_calculate_asw.py"] \
        + self.reduced_matrices \
        + [self.kmax,
           self.outpdffile]

    if self.ybound:
        cmd += ["-s"] + self.ybound

    cmd += ["--kmintype", self.kmin_type]
    if self.kmin_type == "min":
        cmd += ["--kmin", str(self.kmin)]
    elif self.kmin_type == "avg_pts":
        cmd += ["--max_avg_pts", str(self.max_avg_points)]

    if self.save_asw_values:
        cmd += ["-c"]

    context.pythonSystem(*cmd)
