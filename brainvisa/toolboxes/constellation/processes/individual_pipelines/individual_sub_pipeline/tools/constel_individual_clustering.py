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
from brainvisa.processes import Integer
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
    if not find_in_path("constel_intra_subject_clustering.py"):
        raise ValidationError(
            "constel_intra_subject_clustering is not contained in PATH "
            "environnement variable or please make sure that constellation "
            "is installed.")
    try:
        from constel.lib.utils.filetools import select_ROI_number
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")

# ---------------------------Header--------------------------------------------


name = "Clustering From Reduced Individual Matrix"
userLevel = 2

signature = Signature(
    "regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File", section="Nomenclature"),

    "region", String(section="Study parameters"),

    # inputs
    "reduced_individual_matrix", ReadDiskItem(
        "Connectivity Matrix", "Aims matrix formats",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "yes",
                            "intersubject": "no",
                            "individual": "yes"},
        section="Reduced matrix"),

    "individual_white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"},
        section="Freesurfer data"),
    "regions_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"},
        section="Freesurfer data"),


    "kmax", Integer(section="Options"),

    # outputs
    "individual_ROI_clustering", WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "no",
                            "roi_filtered": "no",
                            "intersubject": "no",
                            "step_time": "yes",
                            "measure": "no"},
        section="Clustering"),
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters
    """
    # default value
    self.regions_nomenclature = self.signature[
        "regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})
    self.kmax = 12

    def link_matrix2label(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'region'.
        """
        if self.reduced_individual_matrix is not None:
            s = str(self.reduced_individual_matrix.get("gyrus"))
            name = self.signature["region"].findValue(s)
            return name

    # link of parameters for autocompletion
    self.linkParameters("region", "reduced_individual_matrix",
                        link_matrix2label)
    self.linkParameters("individual_ROI_clustering",
                        "reduced_individual_matrix")
    self.linkParameters("regions_parcellation", "individual_white_mesh")


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constel_intra_subject_clustering'.

    Reduced connectivity matrix is clustered using the kmedoids algorithm.
    """
    from constel.lib.utils.filetools import select_ROI_number
    # selects the label number corresponding to label name
    label_number = select_ROI_number(self.regions_nomenclature.fullPath(),
                                     self.region)

    context.pythonSystem("constel_intra_subject_clustering.py",
                         "matrix", self.reduced_individual_matrix,
                         "patch", label_number,
                         "gyri_segmentation", self.regions_parcellation,
                         "mesh", self.individual_white_mesh,
                         "kmax", self.kmax,
                         "clustering_time", self.individual_ROI_clustering)
