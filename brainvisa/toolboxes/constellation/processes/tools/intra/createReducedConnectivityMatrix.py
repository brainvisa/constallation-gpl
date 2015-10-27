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


# axon python API modules
from brainvisa.processes import Signature, ReadDiskItem, ValidationError, \
    WriteDiskItem, OpenChoice, Choice
from soma.path import find_in_path

# constel modules
try:
    from constel.lib.utils.files import read_file, select_ROI_number
except:
    pass

def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constelConnectionDensityTexture"):
        raise ValidationError(
            "constelConnectionDensityTexture is not contained in PATH"
            "environnement variable or please make sure that constellation "
            "is installed.")


#----------------------------Header--------------------------------------------


name = "Reduced Connectivity Matrix"
userLevel = 2

signature = Signature(
    # inputs
    "complete_connectivity_matrix", ReadDiskItem(
        "Connectivity Matrix", "Aims writable volume formats",
        requiredAttributes={"ends_labelled":"mixed",
                            "reduced":"No",
                            "dense":"No",
                            "intersubject":"No"}),
    "filtered_watershed", ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect":"Yes",
                            "roi_filtered":"Yes",
                            "averaged":"No",
                            "intersubject":"No",
                            "step_time":"No"}),
    "ROIs_nomenclature", ReadDiskItem("Nomenclature ROIs File", "Text File"),
    "ROI", OpenChoice(),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "ROIs_segmentation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),

    #outputs
    "reduced_connectivity_matrix", WriteDiskItem(
        "Connectivity Matrix", "Aims writable volume formats",
        requiredAttributes={"ends_labelled":"mixed",
                            "reduced":"Yes",
                            "dense":"No",
                            "intersubject":"No"}),
)


#----------------------------Function--------------------------------------


def initialization(self):
    """Provides default value and link of parameters"""
    # default value
    self.ROIs_nomenclature = self.signature["ROIs_nomenclature"].findValue({})

    def link_roi(self, dummy):
        """Reads the ROIs nomenclature and proposes them in the signature 'ROI'
        of process.
        """
        if self.ROIs_nomenclature is not None:
            s = ["Select a ROI in this list"]
            s += read_file(self.ROIs_nomenclature.fullPath(), mode=2)
            self.signature["ROI"].setChoices(*s)
            if isinstance(self.signature['ROI'], OpenChoice):
                self.signature["ROI"] = Choice(*s)
                self.changeSignature(self.signature)

    def link_matrix2ROI(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'ROI'.
        """
        if self.complete_connectivity_matrix is not None:
            s = str(self.complete_connectivity_matrix.get("gyrus"))
            name = self.signature["ROI"].findValue(s)
        return name

    # link of parameters for autocompletion
    self.linkParameters("filtered_watershed", "complete_connectivity_matrix")
    self.linkParameters("ROI", "ROIs_nomenclature", link_roi)
    self.linkParameters("ROI", "complete_connectivity_matrix", link_matrix2ROI)
    self.linkParameters("reduced_connectivity_matrix", "filtered_watershed")


#----------------------------Main program--------------------------------------


def execution(self, context):
    """ Compute reduced connectivity matrix M(target regions, patch vertices)
    """
    # selects the ROI label corresponding to ROI name
    ROIlabel = select_ROI_number(self.ROIs_nomenclature.fullPath(), self.ROI)

    # M(target regions, patch vertices)
    context.system("constelConnectionDensityTexture",
                   "-mesh", self.white_mesh,
                   "-connmatrixfile", self.complete_connectivity_matrix,
                   "-targetregionstex", self.filtered_watershed,
                   "-seedregionstex", str(self.ROIs_segmentation),
                   "-seedlabel", ROIlabel,
                   "-type", "seedVertex_to_targets",
                   "-connmatrix", self.reduced_connectivity_matrix,
                   "-normalize", 1,
                   "-verbose", 1)
