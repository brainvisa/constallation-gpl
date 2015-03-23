###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

# Axon python API module
from brainvisa.processes import *
from brainvisa.group_utils import Subject

# Soma-base modules
from soma.path import find_in_path
from soma.minf.api import registerClass, readMinf
from soma.functiontools import partial


# Plot constel module
def validation():
    if not find_in_path("constelConnectionDensityTexture"):
        raise ValidationError(
            "Please make sure that constel module is installed.")

name = "Reduced Connectivity Matrix"
userLevel = 2

# Argument declaration
signature = Signature(
    "filtered_watershed", ReadDiskItem(
        "Avg Filtered Watershed", "Aims texture formats"),
    "group", ReadDiskItem("Group definition", "XML"),
    "segmentation_name_used", String(),
    "complete_connectivity_matrix", ListOf(
        ReadDiskItem("Gyrus Connectivity Matrix", "Matrix sparse")),
    "average_mesh", ReadDiskItem("Mesh", "Aims mesh formats"),
    "gyri_texture", ListOf(
        ReadDiskItem("Label Texture", "Aims texture formats")),
    "reduced_connectivity_matrix", ListOf(
        WriteDiskItem("Group Reduced Connectivity Matrix", "GIS image")))


def afterChildAddedCallback(self, parent, key, child):
    # Set default values
    child.removeLink("filtered_watershed", "complete_connectivity_matrix")
    child.removeLink("reduced_connectivity_matrix", "filtered_watershed")

    child.signature["filtered_watershed"] = parent.signature[
        "filtered_watershed"]
    child.signature["white_mesh"] = parent.signature["average_mesh"]
    child.signature["reduced_connectivity_matrix"] = WriteDiskItem(
        "Group Reduced Connectivity Matrix", "GIS image")


    child.filtered_watershed = parent.filtered_watershed
    child.white_mesh = parent.average_mesh

    # Add link between eNode.ListOf_Input_3dImage and pNode.Input_3dImage
    parent.addLink(key + ".filtered_watershed", "filtered_watershed")
    parent.addLink(key + ".white_mesh", "average_mesh")


def beforeChildRemovedCallback(self, parent, key, child):
    parent.removeLink(key + ".filtered_watershed", "filtered_watershed")
    parent.removeLink(key + ".white_mesh", "average_mesh")


def initialization(self):
    """Provides default values and link of parameters
    """
    
    def link_watershed(self, dummy):
        """Function of link between the filtered watershed and the
        complete matrices.
        """
        if (self.filtered_watershed and self.group) is not None:
            registerClass("minf_2.0", Subject, "Subject")
            groupOfSubjects = readMinf(self.group.fullPath())
            matrices = []
            for subject in groupOfSubjects:
                atts = dict(self.filtered_watershed.hierarchyAttributes())
                atts["texture"] = self.segmentation_name_used
                matrix = ReadDiskItem(
                    "Gyrus Connectivity Matrix", "Matrix sparse").findValue(
                        atts, subject.attributes())
                if matrix is not None:
                    matrices.append(matrix)
            return matrices
                

    def link_matrices(self, dummy):
        """Function of link between the complete matrices and
        the reduced matrices.
        """
        if (self.group and self.complete_connectivity_matrix) is not None:
            matrices = []
            for matrix in self.complete_connectivity_matrix:
                atts = dict(matrix.hierarchyAttributes())
                atts["group_of_subjects"] = os.path.basename(
                    os.path.dirname(self.group.fullPath()))
                atts["texture"] = os.path.basename(os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(self.filtered_watershed.fullPath()))))
                matrix = WriteDiskItem("Group Reduced Connectivity Matrix",
                                   "GIS image").findValue(atts)
                if matrix is not None:
                    matrices.append(matrix)
            return matrices

    # link of parameters
    self.linkParameters(
        "complete_connectivity_matrix",
        ("filtered_watershed", "group", "segmentation_name_used"),
        link_watershed)
    self.linkParameters(
        "reduced_connectivity_matrix",
        ("complete_connectivity_matrix", "group"), link_matrices)

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
        partial(brainvisa.processes.mapValuesToChildrenParameters, eNode,
                eNode, "complete_connectivity_matrix",
                "complete_connectivity_matrix",
                defaultProcess="createReducedConnectivityMatrix",
                name="createReducedConnectivityMatrix"))

    eNode.addLink(
        None, "reduced_connectivity_matrix",
        partial(brainvisa.processes.mapValuesToChildrenParameters, eNode,
                eNode, "reduced_connectivity_matrix",
                "reduced_connectivity_matrix",
                defaultProcess="createReducedConnectivityMatrix",
                name="createReducedConnectivityMatrix"))

    #~eNode.addLink(
        #~None, "gyri_texture",
        #~partial(brainvisa.processes.mapValuesToChildrenParameters, eNode,
                #~eNode, "gyri_texture",
                #~"gyri_texture",
                #~defaultProcess="createReducedConnectivityMatrix",
                #~name="createReducedConnectivityMatrix"))
