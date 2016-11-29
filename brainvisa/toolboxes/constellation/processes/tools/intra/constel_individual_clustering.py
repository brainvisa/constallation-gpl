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
* this process execute the command 'constelIntraSubjectClustering': a cortical
  parcellation is computed for a label from a group connectivity matrix.

Main dependencies: axon python API, soma, constel

Author: Sandrine Lefranc, 2015
"""

#----------------------------Imports-------------------------------------------


# Axon python API module
from brainvisa.processes import ValidationError, Signature, ReadDiskItem, \
    Integer, WriteDiskItem, String

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
    if not find_in_path("constelIntraSubjectClustering.py"):
        raise ValidationError(
            "constelIntraSubjectClustering is not contained in PATH "
            "environnement variable or please make sure that constellation "
            "is installed.")


#----------------------------Header--------------------------------------------


name = "Clustering From Reduced Individual Matrix"
userLevel = 2

signature = Signature(
    # inputs
    "reduced_individual_matrix", ReadDiskItem(
        "Connectivity Matrix", "Aims matrix formats",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "yes",
                            "intersubject": "no",
                            "individual": "yes"}),
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "cortical_region", String(),
    "cortical_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),
    "kmax", Integer(),

    # outputs
    "individual_ROI_clustering", WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "no",
                            "roi_filtered": "no",
                            "intersubject": "no",
                            "step_time": "yes",
                            "measure": "no"}),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters
    """
    # default value
    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})
    self.kmax = 12

    def link_matrix2label(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'cortical_region'.
        """
        if self.reduced_individual_matrix is not None:
            s = str(self.reduced_individual_matrix.get("gyrus"))
            name = self.signature["cortical_region"].findValue(s)
            return name

    # link of parameters for autocompletion
    self.linkParameters("cortical_region", "reduced_individual_matrix",
                        link_matrix2label)
    self.linkParameters("individual_ROI_clustering",
                        "reduced_individual_matrix")
    self.linkParameters("cortical_parcellation", "white_mesh")


#----------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constelIntraSubjectClustering'.

    Reduced connectivity matrix is clustered using the kmedoids algorithm.
    """
    # selects the label number corresponding to label name
    label_number = select_ROI_number(
        self.cortical_regions_nomenclature.fullPath(), self.cortical_region)

    context.pythonSystem("constelIntraSubjectClustering.py",
                         "matrix", self.reduced_individual_matrix,
                         "patch", label_number,
                         "gyri_segmentation", self.cortical_parcellation,
                         "mesh", self.white_mesh,
                         "kmax", self.kmax,
                         "clustering_time", self.individual_ROI_clustering)
