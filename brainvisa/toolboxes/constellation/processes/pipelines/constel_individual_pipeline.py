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


name = "Constellation Individual Pipeline"
userLevel = 0

signature = Signature(
    #inputs
    "study_name", String(),
    "outputs_database", Choice(),
    "format_fiber_tracts", Choice("bundles", "trk"),
    "method", Choice(
        ("averaged approach", "avg"), ("concatenated approach", "concat")),
    "ROIs_nomenclature", ReadDiskItem("Nomenclature ROIs File", "Text File"),
    "ROI", OpenChoice(),
    "dirsubject", ReadDiskItem("subject", "directory"),
    "ROIs_segmentation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes",
                            "inflated": "No"}),
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
    self.signature["outputs_database"].setChoices(*databases)
    if len(databases) != 0:
        self.outputs_database = databases[0]
    else:
        self.signature["outputs_database"] = OpenChoice()

    # default value
    self.smoothing = 3.0
    self.ROIs_nomenclature = self.signature["ROIs_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

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

    def linkMesh(self, dummy):
        if self.method == "avg":
            if self.ROIs_segmentation is not None:
                return self.signature["white_mesh"].findValue(
                    self.ROIs_segmentation)
            return None
        else:
            if self.dirsubject is not None:
                atts = {"subject": self.dirsubject.get("subject")}
                return self.signature["white_mesh"].findValue(atts)

    # link of parameters for autocompletion
    self.linkParameters("ROI", "ROIs_nomenclature", link_roi)
    self.linkParameters("white_mesh", ["dirsubject", "method",
                                       "ROIs_segmentation"], linkMesh)

    # define the main node of a pipeline
    eNode = SerialExecutionNode(self.name, parameterized=self)

    ###########################################################################
    #        link of parameters for the process: "Bundles Filtering"          #
    ###########################################################################

    eNode.addChild(
        "filter", ProcessExecutionNode("constel_brain_tracts_filtering",
                                       optional=1))

    eNode.addDoubleLink("filter.outputs_database", "outputs_database")
    eNode.addDoubleLink("filter.format_fiber_tracts", "format_fiber_tracts")
    eNode.addDoubleLink("filter.method", "method")
    eNode.addDoubleLink("filter.ROI", "ROI")
    eNode.addDoubleLink("filter.ROIs_nomenclature", "ROIs_nomenclature")
    eNode.addDoubleLink("filter.study_name", "study_name")
    eNode.addDoubleLink("filter.dirsubject", "dirsubject")
    eNode.addDoubleLink("filter.ROIs_segmentation", "ROIs_segmentation")
    eNode.addDoubleLink("filter.white_mesh", "white_mesh")

    ###########################################################################
    #        link of parameters with the process: "Fiber Oversampler"         #
    ###########################################################################

    eNode.addChild(
        "oversampler", ProcessExecutionNode("constel_fiber_oversampler",
                                            optional=1))

    eNode.addDoubleLink("oversampler.semilabeled_fibers",
                        "filter.semilabeled_fibers")

    ###########################################################################
    #        link of parameters with the process: "Connectivity Matrix"       #
    ###########################################################################

    eNode.addChild(
        "ConnectivityMatrix",
        ProcessExecutionNode("constel_sparse_individual_matrices", optional=1))

    eNode.addDoubleLink("ConnectivityMatrix.oversampled_semilabeled_fibers",
                        "oversampler.oversampled_semilabeled_fibers")
    eNode.addDoubleLink(
        "ConnectivityMatrix.labeled_fibers", "filter.labeled_fibers")
    eNode.addDoubleLink(
        "ConnectivityMatrix.ROIs_nomenclature", "ROIs_nomenclature")
    eNode.addDoubleLink("ConnectivityMatrix.ROI", "ROI")
    eNode.addDoubleLink(
        "ConnectivityMatrix.ROIs_segmentation", "ROIs_segmentation")
    eNode.addDoubleLink("ConnectivityMatrix.white_mesh", "white_mesh")
    eNode.addDoubleLink("ConnectivityMatrix.dw_to_t1", "filter.dw_to_t1")

    ###########################################################################
    #    link of parameters with the process: "Sum Sparse Matrix Smoothing"   #
    ###########################################################################

    eNode.addChild(
        "smoothing", ProcessExecutionNode("constel_smooth_matrix", optional=1))

    eNode.addDoubleLink("smoothing.matrix_labeled_fibers",
                        "ConnectivityMatrix.matrix_labeled_fibers")
    eNode.addDoubleLink("smoothing.matrix_semilabeled_fibers",
                        "ConnectivityMatrix.matrix_semilabeled_fibers")
    eNode.addDoubleLink(
        "smoothing.ROIs_nomenclature", "ConnectivityMatrix.ROIs_nomenclature")
    eNode.addDoubleLink("smoothing.ROI", "ConnectivityMatrix.ROI")
    eNode.addDoubleLink("smoothing.white_mesh", "white_mesh")
    eNode.addDoubleLink("smoothing.ROIs_segmentation", "ROIs_segmentation")
    eNode.addDoubleLink("smoothing.smoothing", "smoothing")

    ###########################################################################
    #    link of parameters with the process: "Mean Connectivity Profile"     #
    ###########################################################################

    eNode.addChild(
        "MeanProfile", ProcessExecutionNode("constel_mean_individual_profile",
                                            optional=1))

    eNode.addDoubleLink("MeanProfile.complete_individual_matrix",
                        "smoothing.complete_individual_matrix")
    eNode.addDoubleLink(
        "MeanProfile.ROIs_nomenclature", "smoothing.ROIs_nomenclature")
    eNode.addDoubleLink("MeanProfile.ROI", "smoothing.ROI")
    eNode.addDoubleLink("MeanProfile.ROIs_segmentation", "ROIs_segmentation")

    ###########################################################################
    #    link of parameters with the process: "Remove Internal Connections"   #
    ###########################################################################

    eNode.addChild("InternalConnections",
                   ProcessExecutionNode("constel_normalize_individual_profile",
                                        optional=1))

    eNode.addDoubleLink("InternalConnections.mean_individual_profile",
                        "MeanProfile.mean_individual_profile")
    eNode.addDoubleLink("InternalConnections.ROIs_nomenclature",
                        "MeanProfile.ROIs_nomenclature")
    eNode.addDoubleLink("InternalConnections.ROI", "MeanProfile.ROI")
    eNode.addDoubleLink(
        "InternalConnections.ROIs_segmentation", "ROIs_segmentation")

    ###########################################################################
    #        link of parameters with the process: "Watershed"                 #
    ###########################################################################

    eNode.addChild(
        "Watershed",
        ProcessExecutionNode("constel_individual_high_connectivity_regions",
                             optional=1, selected=False))

    eNode.addDoubleLink("Watershed.normed_individual_profile",
                        "InternalConnections.normed_individual_profile")
    eNode.addDoubleLink("Watershed.white_mesh", "white_mesh")

    ###########################################################################
    # link of parameters with the process: "Filtering Watershed"              #
    ###########################################################################

    eNode.addChild("FilteringWatershed",
                   ProcessExecutionNode("constel_individual_regions_filtering",
                                        optional=1, selected=False))

    eNode.addDoubleLink("FilteringWatershed.reduced_individual_profile",
                        "Watershed.reduced_individual_profile")
    eNode.addDoubleLink("FilteringWatershed.complete_individual_matrix",
                        "MeanProfile.complete_individual_matrix")
    eNode.addDoubleLink("FilteringWatershed.ROIs_nomenclature",
                        "MeanProfile.ROIs_nomenclature")
    eNode.addDoubleLink("FilteringWatershed.ROI", "MeanProfile.ROI")
    eNode.addDoubleLink(
        "FilteringWatershed.ROIs_segmentation", "ROIs_segmentation")
    eNode.addDoubleLink("FilteringWatershed.white_mesh", "white_mesh")

    ###########################################################################
    #    link of parameters with the process: "Reduced Connectivity Matrix"   #
    ###########################################################################

    eNode.addChild("ReducedMatrix",
                   ProcessExecutionNode("constel_individual_reduced_matrix",
                                        optional=1, selected=False))

    eNode.addDoubleLink("ReducedMatrix.complete_individual_matrix",
                        "FilteringWatershed.complete_individual_matrix")
    eNode.addDoubleLink("ReducedMatrix.ROIs_nomenclature",
                        "FilteringWatershed.ROIs_nomenclature")
    eNode.addDoubleLink("ReducedMatrix.ROI", "FilteringWatershed.ROI")
    eNode.addDoubleLink("ReducedMatrix.ROIs_segmentation", "ROIs_segmentation")
    eNode.addDoubleLink("ReducedMatrix.white_mesh", "white_mesh")

    ###########################################################################
    #        link of parameters with the process: "Clustering"                #
    ###########################################################################

    eNode.addChild("ClusteringIntraSubjects",
                   ProcessExecutionNode("constel_individual_clustering",
                                        optional=1, selected=False))

    eNode.ClusteringIntraSubjects.removeLink("ROIs_segmentation", "white_mesh")
    eNode.addDoubleLink("ClusteringIntraSubjects.reduced_individual_matrix",
                        "ReducedMatrix.reduced_individual_matrix")
    eNode.addDoubleLink("ClusteringIntraSubjects.ROIs_nomenclature",
                        "ReducedMatrix.ROIs_nomenclature")
    eNode.addDoubleLink("ClusteringIntraSubjects.ROI", "ReducedMatrix.ROI")
    eNode.addDoubleLink(
        "ClusteringIntraSubjects.ROIs_segmentation", "ROIs_segmentation")
    eNode.addDoubleLink("ClusteringIntraSubjects.white_mesh", "white_mesh")

    self.setExecutionNode(eNode)
