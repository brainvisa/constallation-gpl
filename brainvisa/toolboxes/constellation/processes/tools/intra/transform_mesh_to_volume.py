# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 09:35:29 2014

@author: sl236442
"""

# Axon python API module
from brainvisa.processes import *
from soma.path import find_in_path

import numpy

# Plot connectomist module
def validation():
    """This function is executed at BrainVisa startup when the process is loaded.

    It checks some conditions for the process to be available.
    """
    if not find_in_path("comistFiberOversampler"):
        raise ValidationError(
            "Please make sure that connectomist module is installed.")

name = "Extract clusters"
userLevel = 2


# Argument declaration
signature = Signature(
    "white_mesh", ListOf(ReadDiskItem("Mesh", "Aims mesh formats")))


def initialization(self):
    pass


def bounding_box(list_mesh):
    min_x, min_y = numpy.min(list_mesh[0], axis=0)
    max_x, max_y = numpy.max(list_mesh[0], axis=0)
    return numpy.array([(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)])


def execution(self, context):
    # determine bouding box
    vertices = numpy.array([])
    for mesh in self.white_mesh:
        m = aims.read(mesh)
        vertices.append
        
        
    
    # voxel size
    spacing = (1, 1, 1)