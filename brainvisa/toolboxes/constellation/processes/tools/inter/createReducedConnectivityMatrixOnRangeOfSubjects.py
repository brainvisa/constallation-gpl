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
*
*

Main dependencies:

Author: Sandrine Lefranc, 2015
"""


#----------------------------Imports-------------------------------------------

# python module
import os

# Axon python API module
from brainvisa.processes import Signature, ValidationError, ReadDiskItem, \
    WriteDiskItem, String, ListOf, ParallelExecutionNode, ExecutionNode, \
    mapValuesToChildrenParameters
from brainvisa.group_utils import Subject

# Soma-base modules
from soma.path import find_in_path
from soma.minf.api import registerClass, readMinf
from soma.functiontools import partial


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constelConnectionDensityTexture"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


#----------------------------Header--------------------------------------------


name = "Reduced Connectivity Matrix"
userLevel = 2

signature = Signature(
    # --inputs--
    "filtered_watershed", ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "Yes",
                            "roi_filtered": "Yes",
                            "averaged": "Yes",
                            "intersubject": "Yes",
                            "step_time": "No"}),
    "group", ReadDiskItem("Group definition", "XML"),
    "segmentation_name_used", String(),
    "complete_connectivity_matrix", ListOf(ReadDiskItem(
        "Connectivity Matrix", "Aims writable volume formats",
        requiredAttributes={"ends_labelled": "mixed",
                            "reduced": "No",
                            "dense": "No",
                            "intersubject": "No"})),
    "average_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes",
                            "averaged": "Yes"}),
    "ROIs_segmentation", ListOf(ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"})),

    # --outputs--
    "reduced_connectivity_matrix", ListOf(WriteDiskItem(
        "Connectivity Matrix", "Aims writable volume formats",
        requiredAttributes={"ends_labelled": "mixed",
                            "reduced": "Yes",
                            "dense": "No",
                            "intersubject": "Yes"})))


#----------------------------Functions-----------------------------------------


def afterChildAddedCallback(self, parent, key, child):
    # Set default values
    child.removeLink("filtered_watershed", "complete_connectivity_matrix")
    child.removeLink("reduced_connectivity_matrix", "filtered_watershed")

    child.signature["filtered_watershed"] = parent.signature[
        "filtered_watershed"]
    child.signature["white_mesh"] = parent.signature["average_mesh"]
    child.signature["reduced_connectivity_matrix"] = WriteDiskItem(
        "Connectivity Matrix", "Aims writable volume formats")

    child.filtered_watershed = parent.filtered_watershed
    child.white_mesh = parent.average_mesh

    # Add link between eNode.ListOf_Input_3dImage and pNode.Input_3dImage
    parent.addLink(key + ".filtered_watershed", "filtered_watershed")
    parent.addLink(key + ".white_mesh", "average_mesh")


def beforeChildRemovedCallback(self, parent, key, child):
    parent.removeLink(key + ".filtered_watershed", "filtered_watershed")
    parent.removeLink(key + ".white_mesh", "average_mesh")


def initialization(self):
    """Provides default values and link of parameters.
    """

    def link_watershed(self, dummy):
        """Function of link between the filtered watershed and the
        complete matrices.
        """
        if (self.filtered_watershed and self.group
                and self.segmentation_name_used) is not None:
            registerClass("minf_2.0", Subject, "Subject")
            groupOfSubjects = readMinf(self.group.fullPath())
            matrices = []
            for subject in groupOfSubjects:
                atts = dict()
                atts["_database"] = self.filtered_watershed.get("_database")
                atts["center"] = self.filtered_watershed.get("center")
                atts["texture"] = self.segmentation_name_used
                atts["study"] = self.filtered_watershed.get("study")
                atts["gyrus"] = self.filtered_watershed.get("gyrus")
                atts["smoothing"] = self.filtered_watershed.get("smoothing")
                atts["ends_labelled"] = "mixed",
                atts["reduced"] = "No",
                atts["dense"] = "No",
                atts["intersubject"] = "No"
                matrix = self.signature[
                    "complete_connectivity_matrix"].contentType.findValue(
                    atts, subject.attributes())
                if matrix is not None:
                    matrices.append(matrix)
            return matrices

    def link_matrices(self, dummy):
        """Function of link between the complete matrices and
        the reduced matrices.
        """
        if self.group and self.complete_connectivity_matrix and \
                self.filtered_watershed:
            matrices = []
            registerClass("minf_2.0", Subject, "Subject")
            groupOfSubjects = readMinf(self.group.fullPath())
            for subject in groupOfSubjects:
                atts = dict()
                atts["_database"] = self.complete_connectivity_matrix[0].get(
                    "_database")
                atts["center"] = self.complete_connectivity_matrix[0].get(
                    "center")
                atts["texture"] = self.segmentation_name_used
                atts["study"] = self.complete_connectivity_matrix[0].get(
                    "study")
                atts["gyrus"] = self.complete_connectivity_matrix[0].get(
                    "gyrus")
                atts["smoothing"] = self.complete_connectivity_matrix[0].get(
                    "smoothing")
                atts["group_of_subjects"] = os.path.basename(
                    os.path.dirname(self.group.fullPath()))
                atts["texture"] = self.filtered_watershed.get("texture")
                atts["ends_labelled"] = "mixed",
                atts["reduced"] = "Yes",
                atts["dense"] = "No",
                atts["intersubject"] = "Yes"
                matrix = self.signature[
                    "reduced_connectivity_matrix"].contentType.findValue(
                    atts, subject.attributes())
                if matrix is not None:
                    matrices.append(matrix)
            return matrices

    # link of parameters for autocompletion
    self.linkParameters(
        "complete_connectivity_matrix",
        ("filtered_watershed", "group", "segmentation_name_used"),
        link_watershed)
    self.linkParameters(
        "reduced_connectivity_matrix",
        ("complete_connectivity_matrix", "group", "filtered_watershed"),
        link_matrices)

    # define the main node of the pipeline
    eNode = ParallelExecutionNode(
        "Reduced_connectivity_matrix", parameterized=self,
        possibleChildrenProcesses=["createReducedConnectivityMatrix"],
        notify=True)
    self.setExecutionNode(eNode)

    # Add callback to warn about child add and remove
    eNode.afterChildAdded.add(
        ExecutionNode.MethodCallbackProxy(self.afterChildAddedCallback))
    eNode.beforeChildRemoved.add(
        ExecutionNode.MethodCallbackProxy(self.beforeChildRemovedCallback))

    # Add links to refresh child nodes when main lists are modified
    eNode.addLink(
        None, "complete_connectivity_matrix",
        partial(mapValuesToChildrenParameters, eNode,
                eNode, "complete_connectivity_matrix",
                "complete_connectivity_matrix",
                defaultProcess="createReducedConnectivityMatrix",
                name="createReducedConnectivityMatrix"))

    eNode.addLink(
        None, "reduced_connectivity_matrix",
        partial(mapValuesToChildrenParameters, eNode,
                eNode, "reduced_connectivity_matrix",
                "reduced_connectivity_matrix",
                defaultProcess="createReducedConnectivityMatrix",
                name="createReducedConnectivityMatrix"))

    eNode.addLink(
        None, "ROIs_segmentation",
        partial(mapValuesToChildrenParameters, eNode,
                eNode, "ROIs_segmentation",
                "ROIs_segmentation",
                defaultProcess="createReducedConnectivityMatrix",
                name="createReducedConnectivityMatrix"))
