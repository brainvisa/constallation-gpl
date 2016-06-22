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
    - the initialization (by default) of the inputs,
    - the interlinkages between inputs/outputs.
* execute the command 'AimsSumSparseMatrix': sum sparse matrices
* execute the command 'AimsSparseMatrixSmoothing':sparse matrix smoothing using
  heat diffusion, with the geometry of a mesh. Smoothing is applied for each
  line, each line is a texture for the mesh.

Main dependencies: axon python API, soma, constel

Author: Sandrine Lefranc, 2015
"""

#----------------------------Imports-------------------------------------------


# axon python API module
from brainvisa.processes import Signature, ReadDiskItem, Float, String, \
    WriteDiskItem, ValidationError

# soma module
from soma.path import find_in_path

# constel module
try:
    from constel.lib.utils.filetools import select_ROI_number
except:
    pass


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("AimsSumSparseMatrix") \
            or not find_in_path("AimsSparseMatrixSmoothing"):  # checks command
        raise ValidationError(
            "AimsSumSparseMatrix or AimsSparseMatrixSmoothing is not contained"
            "in PATH environnement variable."
            "Please make sure that aims is installed.")


#----------------------------Header--------------------------------------------


name = "Sum Sparse Individual Matrices and Smoothing"
userLevel = 2

signature = Signature(
    # --inputs--
    "matrix_labeled_fibers", ReadDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "both",
                            "reduced": "No",
                            "dense": "No",
                            "intersubject": "No"}),
    "matrix_semilabeled_fibers", ReadDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "single",
                            "reduced": "No",
                            "dense": "No",
                            "intersubject": "No"}),
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "cortical_region", String(),
    "cortical_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "smoothing", Float(),

    # --outputs--
    "complete_individual_matrix", WriteDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "mixed",
                            "reduced": "No",
                            "dense": "No",
                            "intersubject": "No"}),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters"""

    # default values
    self.smoothing = 3.0
    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_matrix2label(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'cortical_region'.
        """
        if self.matrix_labeled_fibers is not None:
            s = str(self.matrix_labeled_fibers.get("gyrus"))
            name = self.signature["cortical_region"].findValue(s)
        return name

    def link_smooth(self, dummy):
        """
        """
        if (self.matrix_semilabeled_fibers and self.smoothing) is not None:
            attrs = dict(self.matrix_semilabeled_fibers.hierarchyAttributes())
            attrs["smoothing"] = str(self.smoothing)
            attrs["smallerlength2"] = self.matrix_semilabeled_fibers.get(
                "smallerlength1")
            attrs["greaterlength2"] = self.matrix_semilabeled_fibers.get(
                "smallerlength1")
            filename = self.signature[
                "complete_individual_matrix"].findValue(attrs)
            return filename

    # link of parameters for autocompletion
    self.linkParameters("cortical_region",
                        "matrix_labeled_fibers",
                        link_matrix2label)
    self.linkParameters("complete_individual_matrix",
                        ("matrix_semilabeled_fibers", "smoothing"),
                        link_smooth)


#----------------------------Main program--------------------------------------


def execution(self, context):
    """Run the commands 'AimsSumSparseMatrix' and 'AimsSparseMatrixSmoothing'.

    Sum of two matrices and smoothing"""
    # selects the label number corresponding to label name
    label_number = select_ROI_number(
        self.cortical_regions_nomenclature.fullPath(), self.cortical_region)

    # sum matrix
    context.system("AimsSumSparseMatrix",
                   "-i", self.matrix_semilabeled_fibers,
                   "-i", self.matrix_labeled_fibers,
                   "-o", self.complete_individual_matrix)

    # matrix smoothing: -s in millimetres
    context.system("AimsSparseMatrixSmoothing",
                   "-i", self.complete_individual_matrix,
                   "-m", self.white_mesh,
                   "-o", self.complete_individual_matrix,
                   "-s", self.smoothing,
                   "-l", self.cortical_parcellation,
                   "-p", label_number)
