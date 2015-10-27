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
    - the parameters of a process (Signature),
    - the parameters initialization
    - the linked parameters
* 

Main dependencies: axon python API, soma-base, constel

Author: Sandrine Lefranc, 2015
"""

#----------------------------Imports-------------------------------------------


# Axon python API module
from brainvisa.processes import ValidationError, Signature, ReadDiskItem, \
    Integer, WriteDiskItem, String
from soma.path import find_in_path

# constel module
try:
    from constel.lib.utils.files import select_ROI_number
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


name = "Clustering"
userLevel = 2

signature = Signature(
    # inputs
    "reduced_connectivity_matrix", ReadDiskItem(
        "Connectivity Matrix", "Aims writable volume formats",
        requiredAttributes={"ends_labelled":"mixed",
                            "reduced":"Yes",
                            "dense":"No",
                            "intersubject":"No"}),
    "ROIs_nomenclature", ReadDiskItem("Nomenclature ROIs File", "Text File"),
    "ROI", String(),
    "ROIs_segmentation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side":"both", "vertex_corr":"Yes"}),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side":"both", "vertex_corr":"Yes"}),
    "kmax", Integer(),
    
    # outputs
    "clustering_time", WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect":"No",
                            "roi_filtered":"No",
                            "averaged":"No",
                            "intersubject":"No",
                            "step_time":"Yes"}),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters
    """
    # default value
    self.ROIs_nomenclature = self.signature["ROIs_nomenclature"].findValue({})
    self.kmax = 12
    
    def link_matrix2ROI(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'ROI'.
        """
        if self.reduced_connectivity_matrix is not None:
            s = str(self.reduced_connectivity_matrix.get("gyrus"))
            name = self.signature["ROI"].findValue(s)
        return name
    
    # link of parameters for autocompletion
    self.linkParameters("ROI", "reduced_connectivity_matrix", link_matrix2ROI)
    self.linkParameters("clustering_time", "reduced_connectivity_matrix")
    self.linkParameters("ROIs_segmentation", "white_mesh")


#----------------------------Main program--------------------------------------


def execution(self, context):
    """Reduced connectivity matrix is clustered using the kmedoids algorithm.
    """
    # selects the ROI label corresponding to ROI name
    ROIlabel = select_ROI_number(self.ROIs_nomenclature.fullPath(), self.ROI)

    context.system("python",
                   find_in_path("constelIntraSubjectClustering.py"),
                   "matrix", self.reduced_connectivity_matrix,
                   "patch", ROIlabel,
                   "gyri_segmentation", self.ROIs_segmentation,
                   "mesh", self.white_mesh,
                   "kmax", self.kmax,
                   "clustering_time", self.clustering_time)
