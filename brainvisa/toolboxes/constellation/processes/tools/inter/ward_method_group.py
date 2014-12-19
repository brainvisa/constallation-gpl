############################################################################
#  This software and supporting documentation are distributed by
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
############################################################################

# Axon python API module
from brainvisa.processes import *

# Soma-base module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is loaded.

    It checks some conditions for the process to be available.
    """
    if not find_in_path("constelConnectionDensityTexture"):
        raise ValidationError(
            "Please make sure that constel module is installed.")

name = "Ward Hierarchical Clustering Method"
userLevel = 2

signature = Signature(
    "kmax", Integer(),
    "patch", Integer(), # TODO: to put a label to a name?
    "group_matrix", String(), # TODO: to define a type
    "distance_matrix_file", String(), # TODO: to define a type
    "average_mesh", ReadDiskItem("Mesh", "Aims mesh formats"),
    "gyri_texture", ListOf(ReadDiskItem("Label Texture", "Aims texture formats")),
    "tex_time", ListOf(
        WriteDiskItem("Group Clustering Time", "Aims texture formats")),
)


def initialization(self):
    self.kmax = 12


def execution(self, context):
    """Run a Ward's hierarchical clustering method.
    """
    args = [sys.executable, find_in_path("constelClusteringWard.py")]
    for x in self.gyri_texture:
        args += ["-g", x]
    for t in self.tex_time:
        args += ["-t", t]
    args += ["-k", self.kmax, "-l", self.patch, "-x", self.group_matrix,
             "-c", self.distance_matrix_file, "-m", self.average_mesh]
    context.system(*args)