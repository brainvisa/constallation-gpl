###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################


# ---------------------------Imports-------------------------------------------


# Axon python API module
from __future__ import absolute_import
from brainvisa.processes import String
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError

# Soma module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    cmd = "constelConnectivityMatrix"
    if not find_in_path(cmd):
        raise ValidationError(
            "'{0}' is not contained in PATH environnement variable. "
            "Please make sure that constel package is installed.".format(cmd))
    try:
        from constel.lib.utils.filetools import select_ROI_number
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ---------------------------Functions-----------------------------------------


name = "Sparse Individual Matrices and Profiles From Tracts."
userLevel = 2

signature = Signature(
    "regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File", section="Nomenclature"),

    "region", String(section="Study parameters"),

    # inputs
    "oversampled_semilabeled_fibers", ReadDiskItem(
        "Filtered Fascicles Bundles", "Aims readable bundles formats",
        requiredAttributes={"ends_labelled": "one",
                            "oversampled": "yes"},
        section="Filtered tracts"),
    "labeled_fibers", ReadDiskItem(
        "Filtered Fascicles Bundles", "Aims readable bundles formats",
        requiredAttributes={"ends_labelled": "both",
                            "oversampled": "no"},
        section="Filtered tracts"),
    "individual_white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"},
        section="Freesurfer data"),
    "dw_to_t1", ReadDiskItem(
        "Transform T2 Diffusion MR to Raw T1 MRI",
        "Transformation matrix",
        section="Freesurfer data"),
    "regions_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"},
        section="Freesurfer data"),

    # ouputs
    "matrix_semilabeled_fibers", WriteDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "one",
                            "reduced": "no",
                            "intersubject": "no",
                            "individual": "yes"},
        section="Connectomist outputs"),
    "matrix_labeled_fibers", WriteDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "both",
                            "reduced": "no",
                            "intersubject": "no",
                            "individual": "yes"},
        section="Connectomist outputs"),
    "profile_semilabeled_fibers", WriteDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"ends_labelled": "one",
                            "normed": "no",
                            "intersubject": "no"},
        section="Connectomist outputs"),
    "profile_labeled_fibers", WriteDiskItem(
        "Connectivity Profile Texture", "Aims texture formats",
        requiredAttributes={"ends_labelled": "both",
                            "normed": "no",
                            "intersubject": "no"},
        section="Connectomist outputs"),
    "complete_individual_matrix", WriteDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "no",
                            "intersubject": "no"},
        section="Connectomist outputs"),
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link between parameters"""
    # default value
    self.regions_nomenclature = self.signature[
        "regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_fibertracts2label(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'region'.
        """
        if self.oversampled_semilabeled_fibers is not None:
            s = str(self.oversampled_semilabeled_fibers.get("gyrus"))
            name = self.signature["region"].findValue(s)
        return name

    def link_smooth(self, dummy):
        """
        """
        if self.matrix_semilabeled_fibers is not None:
            attrs = dict(self.matrix_semilabeled_fibers.hierarchyAttributes())
            attrs["smoothing"] = str(0.0)
            attrs["smallerlength2"] = self.matrix_semilabeled_fibers.get(
                "smallerlength1")
            attrs["greaterlength2"] = self.matrix_semilabeled_fibers.get(
                "smallerlength1")
            filename = self.signature[
                "complete_individual_matrix"].findValue(attrs)
            return filename

    # link of parameters for autocompletion
    self.linkParameters("matrix_semilabeled_fibers",
                        "oversampled_semilabeled_fibers")
    self.linkParameters("region",
                        "oversampled_semilabeled_fibers",
                        link_fibertracts2label)
    self.linkParameters("matrix_labeled_fibers",
                        "labeled_fibers")
    self.linkParameters("profile_semilabeled_fibers",
                        "matrix_semilabeled_fibers")
    self.linkParameters("profile_labeled_fibers",
                        "matrix_labeled_fibers")
    self.linkParameters("complete_individual_matrix",
                        "matrix_semilabeled_fibers",
                        link_smooth)


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Run the commands 'constelConnectivityMatrix' and 'AimsSumSparseMatrix'.

    Computes two connectivity matrices and sum them.
    (labelname vertices, cortical surface vertices).

    (1) case 1: computes connectivity matrix for semilabeled fibers of cortex
                one end only of fibers is identified.
    (2) case 2:computes connectivity matrix for labeled fibers
               both ends of fibers are well identified.
    """
    from constel.lib.utils.filetools import select_ROI_number

    # selects the label number corresponding to label name
    label_number = select_ROI_number(self.regions_nomenclature.fullPath(),
                                     self.region)

    # case 1
    # this command is mostly concerned with fibers leaving the brain stem
    context.system("constelConnectivityMatrix",
                   "-bundles", self.oversampled_semilabeled_fibers,
                   "-connmatrix", self.matrix_semilabeled_fibers,
                   "-matrixcompute", "meshintersectionpoint",
                   "-dist", 0.0,  # no smoothing
                   "-wthresh", 0.001,
                   "-distmax", 5.0,
                   "-seedregionstex", self.regions_parcellation,
                   "-outconntex", self.profile_semilabeled_fibers,
                   "-mesh", self.individual_white_mesh,
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
                   "-seedregionstex", self.regions_parcellation,
                   "-outconntex", self.profile_labeled_fibers,
                   "-mesh", self.individual_white_mesh,
                   "-type", "seed_mean_connectivity_profile",
                   "-trs", self.dw_to_t1,
                   "-seedlabel", label_number,
                   "-normalize", 0,
                   "-verbose", 1)

    # sum matrix (without smoothing)
    context.system("AimsSumSparseMatrix",
                   "-i", self.matrix_semilabeled_fibers,
                   "-i", self.matrix_labeled_fibers,
                   "-o", self.complete_individual_matrix)
