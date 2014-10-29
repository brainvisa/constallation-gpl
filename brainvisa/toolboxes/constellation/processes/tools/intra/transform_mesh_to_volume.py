# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 09:35:29 2014

@author: sl236442
"""

# Axon python API module
from brainvisa.processes import *
from soma.path import find_in_path

from constel.lib.mesh_tools import transform_mesh_to_volume
import numpy

# Plot connectomist module
def validation():
    """This function is executed at BrainVisa startup when the process is loaded.

    It checks some conditions for the process to be available.
    """
    if not find_in_path("comistFiberOversampler"):
        raise ValidationError(
            "Please make sure that connectomist module is installed.")

name = "Mesh to Volume"
userLevel = 2


# Argument declaration
signature = Signature(
    "white_meshes", ListOf(ReadDiskItem("Mesh", "Aims mesh formats")))


def initialization(self):
    pass


def execution(self, context):
    list_submesh = []
    for submesh in self.white_meshes:
        submesh = aims.read(submesh)
        vertices = submesh.vertex()
        list_submesh.append(numpy.asarray(vertices))
    transform_mesh_to_volume(list_submesh)