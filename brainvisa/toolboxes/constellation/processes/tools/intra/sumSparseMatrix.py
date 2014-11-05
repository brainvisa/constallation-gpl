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

# Axon python API modules
from brainvisa.processes import *
from soma.path import find_in_path


# Plot aims modules
def validation():
    """This function is executed at setup when the process is loaded. 

    It checks some conditions for the process to be available.
    """
    if not find_in_path("AimsSumSparseMatrix") \
            or not find_in_path("AimsSparseMatrixSmoothing"):
        raise ValidationError(
            "Please make sure that constel module is installed.")

name = "Smoothing Matrix"
userLevel = 2

# Argument declaration
signature = Signature(
    "matrix_of_fibers_near_cortex", ReadDiskItem(
        "Connectivity Matrix Fibers Near Cortex", "Matrix sparse"),
    "matrix_of_distant_fibers", ReadDiskItem(
        "Connectivity Matrix Outside Fibers Of Cortex", "Matrix sparse"),
    "white_mesh", ReadDiskItem("Mesh", "Aims mesh formats"),
    "gyri_texture", ReadDiskItem("Label Texture", "Aims texture formats"),
    "smoothing", Float(),
    "patch", Integer(),
    "complete_connectivity_matrix", WriteDiskItem(
        "Gyrus Connectivity Matrix", "Matrix sparse"),
)


# Default values
def initialization(self):
    """Provides default values and link of parameters"""
    self.smoothing = 3.0

    def linkSmooth(self, dummy):
        if self.matrix_of_distant_fibers is not None:
            attrs = dict(self.matrix_of_distant_fibers.hierarchyAttributes())
            attrs["smoothing"] = str(self.smoothing)
            filename = self.signature[
                "complete_connectivity_matrix"].findValue(attrs)
            return filename

    self.linkParameters(
        "matrix_of_distant_fibers", "matrix_of_fibers_near_cortex")
    self.linkParameters("complete_connectivity_matrix",
                        ("matrix_of_distant_fibers", "smoothing"), linkSmooth)
    self.linkParameters("white_mesh", "matrix_of_distant_fibers")
    self.setOptional("patch")
    self.signature["white_mesh"].userLevel = 2


def execution(self, context):
    """Sum of two matrices and smoothing"""
    # provides the patch name
    if self.patch is not None:
        patch = self.patch
    else:
        patch = os.path.basename(os.path.dirname(
            os.path.dirname(self.matrix_of_fibers_near_cortex.fullPath())))
        patch = patch.strip("G")

    # sum matrix
    context.system("AimsSumSparseMatrix",
                   "-i", self.matrix_of_distant_fibers,
                   "-i", self.matrix_of_fibers_near_cortex,
                   "-o", self.complete_connectivity_matrix)

    # smoothing matrix: -s in millimetres
    context.system("AimsSparseMatrixSmoothing",
                   "-i", self.complete_connectivity_matrix,
                   "-m", self.white_mesh,
                   "-o", self.complete_connectivity_matrix,
                   "-s", self.smoothing,
                   "-l", self.gyri_texture,
                   "-p", patch)