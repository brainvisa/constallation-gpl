# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 09:35:29 2014

@author: sl236442
"""

# Axon python API module
from __future__ import absolute_import
from brainvisa.processes import *
from soma.path import find_in_path

try:
    from constel.lib.utils.meshtools import transform_mesh_to_volume
except ImportError:
    pass
import numpy

# Plot connectomist module
def validation():
    """This function is executed at BrainVisa startup when the process is loaded.

    It checks some conditions for the process to be available.
    """
    try:
        from constel.lib.utils.meshtools import transform_mesh_to_volume
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")

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
