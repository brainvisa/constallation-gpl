###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

"""
"""

#----------------------------Imports-------------------------------------------


# system module
from __future__ import absolute_import
import os

# axon python API module
from brainvisa.processes import Float
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
    pass
    #if not find_in_path("constel_table_measurements.py"):
    #    raise ValidationError(
    #        "Please make sure that constel module is installed.")


#----------------------------Header--------------------------------------------


name = "Write a different measures in csv file."
userLevel = 2

signature = Signature(
    #--inputs
    "clusters", ReadDiskItem(
        "Connectivity ROI texture", "aims texture formats", 
        requiredAttributes={'step_time': 'yes'}),

    "white_mesh", ReadDiskItem('White Mesh', 'aims mesh formats'),
    "number_of_clusters", Integer(),
    "matrix", ReadDiskItem(
        "Connectivity Matrix", "Gis image",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "yes",
                            "intersubject": "yes",
                            "individual": "no"}),

    #--outputs--
    "csvfile", WriteDiskItem("Any Type", getAllFormats()),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """
    """
    pass


#----------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constel_table_measurements.py'.
    """
    
    cmd = ["constel_table_measurements.py",
           self.clusters,
           self.white_mesh,
           self.number_of_clusters,
           self.matrix,
           self.csvfile]

    context.pythonSystem(*cmd)
