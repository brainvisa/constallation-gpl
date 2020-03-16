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
* Write the fiber lengths in a text file and write also an histogram.

Main dependencies:
"""


# ----------------------------Imports------------------------------------------


# axon python API module
from __future__ import absolute_import
from brainvisa.processes import String
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import ValidationError

# soma
from soma.path import find_in_path


def validation(self):
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constel_write_fibers_histogram.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")

# ----------------------------Header-------------------------------------------


name = 'Write the fiber lengths in a text file'
userLevel = 2

signature = Signature(
    # --inputs--
    "fiber_tracts", ReadDiskItem(
        "Fascicles Bundles", "Aims writable bundles formats"),

    # --ouput--
    "lengths_filename", String(),
)


# ----------------------------Functions----------------------------------------


def initialization(self):
    """
    """
    pass


# ----------------------------Main Program-------------------------------------


def execution(self, context):
    """Execute the python command "constel_fibers_histogram".
    """
    # Give the name of the command
    cmd = ["constel_write_fibers_histogram.py"]

    # Give the options of the command
    cmd += [self.fiber_tracts,
            self.lengths_filename]

    # Execute the command
    context.system(*cmd)
