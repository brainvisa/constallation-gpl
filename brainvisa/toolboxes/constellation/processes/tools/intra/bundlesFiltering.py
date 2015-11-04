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
    "outputs_database", Choice(),
    "format_fiber_tracts", Choice("bundles", "trk"),
    "method", Choice(("averaged approach", "avg"),
                     ("concatenated approach", "concat")),
    "ROIs_nomenclature", ReadDiskItem("Nomenclature ROIs File", "Text File"),
    "ROI", OpenChoice(),
    "dirsubject", ReadDiskItem("subject", "directory"),
    "ROIs_segmentation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "dw_to_t1", ReadDiskItem("Transformation matrix", "Transformation matrix"),
    "minlength_labeled_fibers", Float(),
    "maxlength_labeled_fibers", Float(),
    "minlength_semilabeled_fibers", Float(),
    "maxlength_semilabeled_fibers", Float(),

    # --outputs--
    "labeled_fibers", WriteDiskItem(
        "Filtered Fascicles Bundles", "Aims writable bundles formats",
        requiredAttributes={"both_ends_labelled": "Yes", "oversampled": "No"}),
    "semilabeled_fibers", WriteDiskItem(
        "Filtered Fascicles Bundles", "Aims writable bundles formats",
        requiredAttributes={"both_ends_labelled": "No", "oversampled": "No"}),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters
    """
    # default values
    self.minlength_labeled_fibers = 30.
    self.maxlength_labeled_fibers = 500.
    self.minlength_semilabeled_fibers = 20.
    self.maxlength_semilabeled_fibers = 500.
    self.ROIs_nomenclature = self.signature["ROIs_nomenclature"].findValue({
        "atlasname": "desikan_freesurfer"})

    # list of possible databases, while respecting the ontology
    databases = [h.name for h in neuroHierarchy.hierarchies()
                 if h.fso.name == "brainvisa-3.2.0"]
    self.signature["outputs_database"].setChoices(*databases)
    if len(databases) != 0:
        self.outputs_database = databases[0]
    else:
        self.signature["outputs_database"] = OpenChoice()

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
        """Defines all attributs of 'abeled_fibers' in order to
        allow autocompletion.
        """
        if (self.outputs_database and self.study_name and self.dirsubject
                and self.ROI) is not None:
            attrs = dict()
            attrs["_database"] = self.outputs_database
            attrs["study"] = self.method
            attrs["texture"] = self.study_name
            attrs["subject"] = os.path.basename(self.dirsubject.fullPath())
            attrs["gyrus"] = str(self.ROI)
            attrs["smallerlength1"] = str(int(self.minlength_labeled_fibers))
            attrs["greaterlength1"] = str(int(self.maxlength_labeled_fibers))
            filename = self.signature["labeled_fibers"].findValue(attrs)
            return filename

    def link_between_filtered_bundles(self, dummy):
        """Defines all attributs of 'semilabeled_fibers' in order to
        allow autocompletion.
        """
        if (self.outputs_database and self.study_name and self.dirsubject
                and self.ROI) is not None:
            attrs = dict()
            attrs["_database"] = self.outputs_database
            attrs["study"] = self.method
            attrs["texture"] = self.study_name
            attrs["subject"] = os.path.basename(self.dirsubject.fullPath())
            attrs["gyrus"] = str(self.ROI)
            attrs["smallerlength2"] = str(
                int(self.minlength_semilabeled_fibers))
            attrs["greaterlength2"] = str(
                int(self.maxlength_semilabeled_fibers))
            filename = self.signature["semilabeled_fibers"].findValue(attrs)
            return filename

    # link of parameters for autocompletion
    self.linkParameters("ROI", "ROIs_nomenclature", link_roi)
    self.linkParameters("dw_to_t1", "dirsubject")
    self.linkParameters("labeled_fibers", (
        "outputs_database", "dirsubject", "method", "study_name", "ROI",
        "minlength_labeled_fibers",
        "maxlength_labeled_fibers"), link_filtered_bundles)
    self.linkParameters(
        "semilabeled_fibers", (
            "outputs_database", "dirsubject", "method", "study_name", "ROI",
            "minlength_semilabeled_fibers",
            "maxlength_semilabeled_fibers"), link_between_filtered_bundles)


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
        self.dirsubject.fullPath(), self.format_fiber_tracts)

    # selects the ROI label corresponding to ROI name
    ROIlabel = select_ROI_number(self.ROIs_nomenclature.fullPath(), self.ROI)

    # name of the command (C++)
    cmd = ["constelBundlesFiltering"]

    # options of the command
    for fiber_tract in list_fiber_tracts:
        cmd += ["-i", fiber_tract]
    cmd += [
        "-o", self.labeled_fibers,
        "-n", self.semilabeled_fibers,
        "--mesh", self.white_mesh,
        "--tex", self.ROIs_segmentation,
        "--trs", self.dw_to_t1,
        "--mode", "Name1_Name2orNotInMesh",
        "--names", "^" + str(ROIlabel) + "_[0-9]+$",
        "--names", "^[0-9]+_" + str(ROIlabel) + "$",
        "-g", ROIlabel,
        "-r",
        "-l", self.minlength_labeled_fibers,
        "-L", self.maxlength_labeled_fibers,
        "--nimlmin", self.minlength_semilabeled_fibers,
        "--nimlmax", self.maxlength_semilabeled_fibers,
    ]

    # executes the command
    context.system(*cmd)
