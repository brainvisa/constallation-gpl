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
* defines a Brainvisa pipeline
    - the parameters of a pipeline (Signature),
    - the parameters initialization
    - the linked parameters between processes

Main dependencies: axon python API, constel

Author: Sandrine Lefranc, 2015
"""

#----------------------------Imports-------------------------------------------


# Axon python API modules
from brainvisa.processes import Signature, String, Choice, ReadDiskItem, \
    Float, OpenChoice, neuroHierarchy, SerialExecutionNode, \
    ProcessExecutionNode

# constel module
try:
    from constel.lib.utils.files import read_file
except:
    pass


#----------------------------Header--------------------------------------------


name = "Constellation within-subject pipeline"
userLevel = 2

signature = Signature(
    #inputs
    "study_name", String(),
    "database", Choice(),
    "format_fiber_tracts", Choice("bundles", "trk"),
    "method", Choice(
        ("averaged approach", "avg"), ("concatenated approach", "concat")),
    "ROIs_nomenclature", ReadDiskItem("Nomenclature ROIs File", "Text File"),
    "ROI", OpenChoice(),
    "subject", ReadDiskItem("subject", "directory"),
    "ROIs_segmentation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "smoothing", Float(),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters
    """

    # list of possible databases, while respecting the ontology
    # ontology: brainvisa-3.2.0
    databases = [h.name for h in neuroHierarchy.hierarchies()
                 if h.fso.name == "brainvisa-3.2.0"]
    self.signature["database"].setChoices(*databases)
    if len(databases) != 0:
        self.database = databases[0]
    else:
        self.signature["database"] = OpenChoice()

    # default value
    self.smoothing = 3.0
    self.ROIs_nomenclature = self.signature["ROIs_nomenclature"].findValue({})

    def link_roi(self, dummy):
        """Reads the ROIs nomenclature and proposes them in the signature 'ROI'
        of process.
        """
        if self.ROIs_nomenclature is not None:
            s = ["Select a ROI in this list"]
            s += read_file(self.ROIs_nomenclature.fullPath(), mode=2)
            self.signature["ROI"].setChoices(*s)
            if isinstance(self.signature["ROI"], OpenChoice):
                self.signature["ROI"] = Choice(*s)
                self.changeSignature(self.signature)

    # link of parameters for autocompletion
    self.linkParameters("ROI", "ROIs_nomenclature", link_roi)

    # define the main node of a pipeline
    eNode = SerialExecutionNode(self.name, parameterized=self)

    ###########################################################################
    #        link of parameters for the process: "Bundles Filtering"          #
    ###########################################################################

    eNode.addChild(
        "filter", ProcessExecutionNode("bundlesFiltering", optional=1))

    eNode.addDoubleLink("filter.database", "database")
    eNode.addDoubleLink("filter.format_fiber_tracts", "format_fiber_tracts")
    eNode.addDoubleLink("filter.method", "method")
    eNode.addDoubleLink("filter.ROI", "ROI")
    eNode.addDoubleLink("filter.study_name", "study_name")
    eNode.addDoubleLink("filter.subject", "subject")
    eNode.addDoubleLink("filter.ROIs_segmentation", "ROIs_segmentation")
    eNode.addDoubleLink("filter.white_mesh", "white_mesh")

    ###########################################################################
    #        link of parameters with the process: "Fiber Oversampler"         #
    ###########################################################################

    eNode.addChild(
        "oversampler", ProcessExecutionNode("fiberOversampler", optional=1))

    eNode.addDoubleLink("oversampler.filtered_length_distant_fibers",
                        "filter.subsets_of_distant_fibers")

    ###########################################################################
    #        link of parameters with the process: "Connectivity Matrix"       #
    ###########################################################################

    eNode.addChild(
        "ConnectivityMatrix", ProcessExecutionNode("createConnectivityMatrix",
                                                   optional=1))

    eNode.addDoubleLink("ConnectivityMatrix.oversampled_distant_fibers",
                        "oversampler.oversampled_distant_fibers")
    eNode.addDoubleLink(
        "ConnectivityMatrix.filtered_length_fibers_near_cortex",
        "filter.subsets_of_fibers_near_cortex")
    eNode.addDoubleLink(
        "ConnectivityMatrix.ROIs_segmentation", "ROIs_segmentation")
    eNode.addDoubleLink("ConnectivityMatrix.white_mesh", "white_mesh")
    eNode.addDoubleLink("ConnectivityMatrix.dw_to_t1", "filter.dw_to_t1")

    ###########################################################################
    #    link of parameters with the process: "Sum Sparse Matrix Smoothing"   #
    ###########################################################################

    eNode.addChild(
        "smoothing", ProcessExecutionNode("sumSparseMatrix", optional=1))

    eNode.addDoubleLink("smoothing.matrix_of_fibers_near_cortex",
                        "ConnectivityMatrix.matrix_of_fibers_near_cortex")
    eNode.addDoubleLink("smoothing.matrix_of_distant_fibers",
                        "ConnectivityMatrix.matrix_of_distant_fibers")
    eNode.addDoubleLink("smoothing.white_mesh", "white_mesh")
    eNode.addDoubleLink("smoothing.ROIs_segmentation", "ROIs_segmentation")
    eNode.addDoubleLink("smoothing.smoothing", "smoothing")

    ###########################################################################
    #    link of parameters with the process: "Mean Connectivity Profile"     #
    ###########################################################################

    eNode.addChild(
        "MeanProfile", ProcessExecutionNode("createMeanConnectivityProfile",
                                            optional=1))

    eNode.addDoubleLink("MeanProfile.complete_connectivity_matrix",
                        "smoothing.complete_connectivity_matrix")
    eNode.addDoubleLink("MeanProfile.ROIs_segmentation", "ROIs_segmentation")

    ###########################################################################
    #    link of parameters with the process: "Remove Internal Connections"   #
    ###########################################################################

    eNode.addChild("InternalConnections",
                   ProcessExecutionNode("removeInternalConnections",
                                        optional=1))

    eNode.addDoubleLink("InternalConnections.patch_connectivity_profile",
                        "MeanProfile.patch_connectivity_profile")
    eNode.addDoubleLink(
        "InternalConnections.ROIs_segmentation", "ROIs_segmentation")

    ###########################################################################
    #        link of parameters with the process: "Watershed"                 #
    ###########################################################################

    eNode.addChild(
        "Watershed",
        ProcessExecutionNode("watershedReflectingConnectionsToGyrus",
                             optional=1, selected=False))

    eNode.addDoubleLink("Watershed.normed_connectivity_profile",
                        "InternalConnections.normed_connectivity_profile")
    eNode.addDoubleLink("Watershed.white_mesh", "white_mesh")

    ###########################################################################
    # link of parameters with the process: "Filtering Watershed"              #
    ###########################################################################

    eNode.addChild("FilteringWatershed",
                   ProcessExecutionNode("filteringWatershed",
                                        optional=1, selected=False))

    eNode.addDoubleLink("FilteringWatershed.watershed", "Watershed.watershed")
    eNode.addDoubleLink("FilteringWatershed.complete_connectivity_matrix",
                        "MeanProfile.complete_connectivity_matrix")
    eNode.addDoubleLink(
        "FilteringWatershed.ROIs_segmentation", "ROIs_segmentation")
    eNode.addDoubleLink("FilteringWatershed.white_mesh", "white_mesh")

    ###########################################################################
    #    link of parameters with the process: "Reduced Connectivity Matrix"   #
    ###########################################################################

    eNode.addChild("ReducedMatrix",
                   ProcessExecutionNode("createReducedConnectivityMatrix",
                                        optional=1, selected=False))

    eNode.addDoubleLink("ReducedMatrix.complete_connectivity_matrix",
                        "FilteringWatershed.complete_connectivity_matrix")
    eNode.addDoubleLink("ReducedMatrix.ROIs_segmentation", "ROIs_segmentation")
    eNode.addDoubleLink("ReducedMatrix.white_mesh", "white_mesh")

    ###########################################################################
    #        link of parameters with the process: "Clustering"                #
    ###########################################################################

    eNode.addChild("ClusteringIntraSubjects",
                   ProcessExecutionNode("ClusteringIntrasubject",
                                        optional=1, selected=False))

    eNode.addDoubleLink("ClusteringIntraSubjects.reduced_connectivity_matrix",
                        "ReducedMatrix.reduced_connectivity_matrix")
    eNode.addDoubleLink(
        "ClusteringIntraSubjects.ROIs_segmentation", "ROIs_segmentation")
    eNode.addDoubleLink("ClusteringIntraSubjects.white_mesh", "white_mesh")

    self.setExecutionNode(eNode)
