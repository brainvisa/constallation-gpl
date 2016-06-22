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
* executes the command 'constelConnectivityMatrix': the connectivity matrix is
  computed  M(labelname vertices, cortical surface vertices)

Main dependencies: axon python API, soma, constel

Author: Sandrine Lefranc, 2015
"""

#----------------------------Imports-------------------------------------------


# axon python API module
from brainvisa.processes import Signature, ReadDiskItem, WriteDiskItem, \
    ValidationError, String

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
    if not find_in_path("constelConnectivityMatrix"):  # checks command (C++)
        raise ValidationError(
            "constelConnectivityMatrix is not contained in PATH environnement "
            "variable or please make sure that constellation is installed.")


#----------------------------Functions-----------------------------------------


name = "Sparse Individual Matrices and Profiles From Tracts"
userLevel = 2

signature = Signature(
    # --inputs--
    "oversampled_semilabeled_fibers", ReadDiskItem(
        "Filtered Fascicles Bundles", "Aims readable bundles formats",
        requiredAttributes={"both_ends_labelled": "No", "oversampled": "Yes"}),
    "labeled_fibers", ReadDiskItem(
        "Filtered Fascicles Bundles", "Aims readable bundles formats",
        requiredAttributes={"both_ends_labelled": "Yes", "oversampled": "No"}),
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "cortical_region", String(),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "cortical_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "dw_to_t1", ReadDiskItem("Transform T2 Diffusion MR to Raw T1 MRI",
                             "Transformation matrix"),

    # --ouputs--
    "matrix_semilabeled_fibers", WriteDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "single",
                            "reduced": "No",
                            "dense": "No",
                            "intersubject": "No"}),
    "matrix_labeled_fibers", WriteDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "both",
                            "reduced": "No",
                            "dense": "No",
                            "intersubject": "No"}),
    "profile_semilabeled_fibers", WriteDiskItem(
        "Filtered Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"normed": "No",
                            "thresholded": "Yes",
                            "averaged": "No",
                            "intersubject": "No",
                            "both_ends_labelled": "No"}),
    "profile_labeled_fibers", WriteDiskItem(
        "Filtered Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"normed": "No",
                            "thresholded": "Yes",
                            "averaged": "No",
                            "intersubject": "No",
                            "both_ends_labelled": "Yes"}),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link between parameters"""
    # default value
    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_fibertracts2label(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'cortical_region'.
        """
        if self.oversampled_semilabeled_fibers is not None:
            s = str(self.oversampled_semilabeled_fibers.get("gyrus"))
            name = self.signature["cortical_region"].findValue(s)
        return name

    # link of parameters for autocompletion
    self.linkParameters(
        "matrix_semilabeled_fibers", "oversampled_semilabeled_fibers")
    self.linkParameters(
        "cortical_region", "oversampled_semilabeled_fibers",
        link_fibertracts2label)
    self.linkParameters(
        "matrix_labeled_fibers", "labeled_fibers")
    self.linkParameters(
        "profile_semilabeled_fibers", "matrix_semilabeled_fibers")
    self.linkParameters(
        "profile_labeled_fibers", "matrix_labeled_fibers")


#----------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constelConnectivityMatrix'.

    Computes two connectivity matrices.
    (labelname vertices, cortical surface vertices).

    (1) case 1: computes connectivity matrix for semilabeled fibers of cortex
                one end only of fibers is identified.
    (2) case 2:computes connectivity matrix for labeled fibers
               both ends of fibers are well identified.
    """
    # selects the label number corresponding to label name
    label_number = select_ROI_number(
        self.cortical_regions_nomenclature.fullPath(), self.cortical_region)

    # case 1
    # this command is mostly concerned with fibers leaving the brain stem
    context.system("constelConnectivityMatrix",
                   "-bundles", self.oversampled_semilabeled_fibers,
                   "-connmatrix", self.matrix_semilabeled_fibers,
                   "-matrixcompute", "meshintersectionpoint",
                   "-dist", 0.0,  # no smoothing
                   "-wthresh", 0.001,
                   "-distmax", 5.0,
                   "-seedregionstex", self.cortical_parcellation,
                   "-outconntex", self.profile_semilabeled_fibers,
                   "-mesh", self.white_mesh,
                   "-type", "seed_mean_connectivity_profile",
                   "-trs", self.dw_to_t1,
                   "-seedlabel", label_number,
                   "-normalize", 0,
                   "-verbose", 1)

    # case 2
    context.system("constelConnectivityMatrix",
                   "-bundles", self.labeled_fibers,
                   "-connmatrix", self.matrix_labeled_fibers,
                   "-dist", 0.0,  # no smoothing
                   "-seedregionstex", self.cortical_parcellation,
                   "-outconntex", self.profile_labeled_fibers,
                   "-mesh", self.white_mesh,
                   "-type", "seed_mean_connectivity_profile",
                   "-trs", self.dw_to_t1,
                   "-seedlabel", label_number,
                   "-normalize", 0,
                   "-verbose", 1)
