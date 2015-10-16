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
* executes the command 'constelBundlesFiltering' to filter the fiber tracts
  according to length.

Main dependencies: axon python API, soma-base, constel

Author: Sandrine Lefranc, 2015
"""

#----------------------------Imports-------------------------------------------


# python modules
import os
import glob

# axon python API module
from brainvisa.processes import Signature, String, Choice, Float, \
    ReadDiskItem, WriteDiskItem, ValidationError, neuroHierarchy, OpenChoice

# soma-base module
from soma.path import find_in_path

# constel modules
try:
    from constel.lib.utils.files import read_file, select_ROI_number
    from constel.lib.bundles.bundles_tools import load_fiber_tracts
except:
    pass


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constelBundlesFiltering"):  # checks command (C++)
        raise ValidationError(
            "constelBundlesFiltering is not contained in PATH environnement "
            "variable. Please make sure that constellation is installed.")


#----------------------------Header--------------------------------------------


name = "Bundles Filtering"
userLevel = 2

signature = Signature(
    # --inputs--
    "study_name", String(),
    "database", Choice(),
    "format_fiber_tracts", Choice("bundles", "trk"),
    "method", Choice(("averaged approach", "avg"),
                     ("concatenated approach", "concat")),
    "ROIs_nomenclature", ReadDiskItem("Text file", "Text File"),
    "ROI", OpenChoice(),
    "subject", ReadDiskItem("subject", "directory"),
    "ROIs_segmentation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "dw_to_t1", ReadDiskItem("Transformation matrix", "Transformation matrix"),
    "min_length_of_fibers_near_cortex", Float(),
    "max_length_of_fibers_near_cortex", Float(),
    "min_distant_fibers_length", Float(),
    "max_distant_fibers_length", Float(),

    # --outputs--
    "subsets_of_fibers_near_cortex", WriteDiskItem(
        "Filtered Fascicles Bundles", "Aims writable bundles formats",
        requiredAttributes={"both_ends_labelled": "Yes", "oversampled": "No"}),
    "subsets_of_distant_fibers", WriteDiskItem(
        "Filtered Fascicles Bundles", "Aims writable bundles formats",
        requiredAttributes={"both_ends_labelled": "No", "oversampled": "No"}),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters
    """
    # default values
    self.min_length_of_fibers_near_cortex = 30.
    self.max_length_of_fibers_near_cortex = 500.
    self.min_distant_fibers_length = 20.
    self.max_distant_fibers_length = 500.

    # list of possible databases, while respecting the ontology
    databases = [h.name for h in neuroHierarchy.hierarchies()
                 if h.fso.name == "brainvisa-3.2.0"]
    self.signature["database"].setChoices(*databases)
    if len(databases) != 0:
        self.database = databases[0]
    else:
        self.signature["database"] = OpenChoice()

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

    def link_filtered_bundles(self, dummy):
        """Defines all attributs of 'subsets_of_fibers_near_cortex' in order to
        allow autocompletion.
        """
        if (self.database and self.study_name and self.subject
                and self.ROI) is not None:
            attrs = dict()
            attrs["_database"] = self.database
            attrs["study"] = self.method
            attrs["texture"] = self.study_name
            attrs["subject"] = os.path.basename(self.subject.fullPath())
            attrs["gyrus"] = str(self.ROI)
            attrs["smallerlength1"] = str(
                int(self.min_length_of_fibers_near_cortex))
            attrs["greaterlength1"] = str(
                int(self.max_length_of_fibers_near_cortex))
            filename = self.signature[
                "subsets_of_fibers_near_cortex"].findValue(attrs)
            return filename

    def link_between_filtered_bundles(self, dummy):
        """Defines all attributs of 'subsets_of_distant_fibers' in order to
        allow autocompletion.
        """
        if (self.database and self.study_name and self.subject
                and self.ROI) is not None:
            attrs = dict()
            attrs["_database"] = self.database
            attrs["study"] = self.method
            attrs["texture"] = self.study_name
            attrs["subject"] = os.path.basename(self.subject.fullPath())
            attrs["gyrus"] = str(self.ROI)
            attrs["smallerlength2"] = str(int(self.min_distant_fibers_length))
            attrs["greaterlength2"] = str(int(self.max_distant_fibers_length))
            filename = self.signature[
                "subsets_of_distant_fibers"].findValue(attrs)
            return filename

    # link of parameters for autocompletion
    self.linkParameters("ROI", "ROIs_nomenclature", link_roi)
    self.linkParameters("dw_to_t1", "subject")
    self.linkParameters("subsets_of_fibers_near_cortex", (
        "database", "subject", "method", "study_name", "ROI",
        "min_length_of_fibers_near_cortex",
        "max_length_of_fibers_near_cortex"), link_filtered_bundles)
    self.linkParameters(
        "subsets_of_distant_fibers", (
            "database", "subject", "method", "study_name", "ROI",
            "min_distant_fibers_length",
            "max_distant_fibers_length"), link_between_filtered_bundles)


#----------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constelBundlesFiltering' to filter the fiber tracts
    according to length.

    Two type of fiber tracts files are to be considered in this process:
        - the fibers near cortex are defined as having both ends attached to
          the mesh (and are consequently labelled)
        - the distant fibers are defined as having only one end attached to the
          mesh (the other being not identified)
    """
    # selects all fiber tracts of the given subject
    list_fiber_tracts = load_fiber_tracts(
        self.subject.fullPath(), self.format_fiber_tracts)

    # selects the ROI label corresponding to ROI name
    ROIlabel = select_ROI_number(self.ROIs_nomenclature.fullPath(), self.ROI)

    # name of the command (C++)
    cmd = ["constelBundlesFiltering"]

    # options of the command
    for fiber_tract in list_fiber_tracts:
        cmd += ["-i", fiber_tract]
    cmd += [
        "-o", self.subsets_of_fibers_near_cortex,
        "-n", self.subsets_of_distant_fibers,
        "--mesh", self.white_mesh,
        "--tex", self.ROIs_segmentation,
        "--trs", self.dw_to_t1,
        "--mode", "Name1_Name2orNotInMesh",
        "--names", "^" + str(ROIlabel) + "_[0-9]+$",
        "--names", "^[0-9]+_" + str(ROIlabel) + "$",
        "-g", ROIlabel,
        "-r",
        "-l", self.min_length_of_fibers_near_cortex,
        "-L", self.max_length_of_fibers_near_cortex,
        "--nimlmin", self.min_distant_fibers_length,
        "--nimlmax", self.max_distant_fibers_length,
    ]

    # executes the command
    context.system(*cmd)
