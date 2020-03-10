###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

"""
Compute the connectome of a given parcellation.
"""


# ----------------------------Imports------------------------------------------


# axon python API module
from __future__ import absolute_import
from brainvisa.processes import String
from brainvisa.processes import Signature
from brainvisa.processes import ValidationError

# soma module
from soma.path import find_in_path


def validate(self):
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constel_merge_nuclei_cortex.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ---------------------------Header-------------------------------------------


name = 'Merge white and nuclei meshes'
userLevel = 2

signature = Signature(
    # --inputs--
    "white_dir", String(),
    "nuclei_dir", String(),
    "texture_dir", String(),

    # --ouput--
    "out_tex_filename", String(),
    "out_mesh_filename", String(),
)


# ----------------------------Functions----------------------------------------


def initialization(self):
    """Provides default values and link of parameters
    """
    pass


# ----------------------------Main Program-------------------------------------


def execution(self, context):
    """
    """
    # define the command parameters
    cmd = ["constel_merge_nuclei_cortex.py",
           self.white_dir,
           self.nuclei_dir,
           self.texture_dir,
           self.out_tex_filename,
           self.out_mesh_filename]

    # execute the command
    context.pythonSystem(*cmd)
