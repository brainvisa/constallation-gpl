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
* define a Brainvisa process.
* execute the command 'AimsSparseMatrixSmoothing'.

Main dependencies: axon python API, soma, constel
"""

# ---------------------------Imports-------------------------------------------

# axon python API module
from brainvisa.processes import Integer
from brainvisa.processes import Signature
from brainvisa.processes import getAllFormats
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError

# soma.path module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    cmd_name = "constel_reorganize_fsl_connectome.py"
    if not find_in_path(cmd_name):  # checks command
        raise ValidationError(
            "'{0}' is not contained in PATH environnement variable. "
            "Please make sure that aims is installed.".format(cmd_name))

# ---------------------------Header--------------------------------------------


name = "FSL Connectome."
userLevel = 2

signature = Signature(
    # --inputs--
    "vertex_labels", ReadDiskItem("ROI Texture", "Aims texture formats"),
    "fdt_matrix", ReadDiskItem("Any Type", getAllFormats()),
    "coords", ReadDiskItem("Any Type", getAllFormats()),
    "label", Integer(),

    # --outputs--
    "outdir", WriteDiskItem("directory", "directory"),
)

# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters"""
    pass


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constel_reorganize_fsl_connectome.py'.

    Compute connectome from the FSL outputs (probtrackx2)."""

    # matrix smoothing: -s in millimetres
    context.pythonSystem("constel_reorganize_fsl_connectome.py",
                         self.vertex_labels,
                         self.fdt_matrix,
                         self.coords,
                         self.label,
                         self.outdir)
