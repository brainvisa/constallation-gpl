###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

# Axon python API modules
from brainvisa.processes import *

name = "Constellation within-subject pipeline"
userLevel = 2

# Argument declaration
signature = Signature(
    "database", Choice(),
    "formats_fiber_tracts", Choice("bundles", "trk"),
    "study", Choice(
        ("averaged approach", "avg"), ("concatenated approach", "concat")),
    "patch", Choice(
        ("*** use_new_patch ***", 0),
        ("left corpus callosum", 1), ("left bankssts", 2),
        ("left caudal anterior cingulate", 3),
        ("left caudal middle frontal", 4), ("left cuneus", 6),
        ("left entorhinal", 7), ("left fusiform", 8),
        ("left inferior parietal", 9), ("left inferior temporal", 10),
        ("left isthmus cingulate", 11), ("left lateral occipital", 12),
        ("left lateral orbitofrontal", 13), ("left lingual", 14),
        ("left medial orbitofrontal", 15), ("left middle temporal", 16),
        ("left parahippocampal", 17), ("left paracentral", 18),
        ("left pars opercularis", 19), ("left pars orbitalis", 20),
        ("left pars triangularis", 21), ("left pericalcarine", 22),
        ("left postcentral", 23), ("left posterior cingulate", 24),
        ("left precentral", 25), ("left precuneus", 26),
        ("left rostral anterior cingulate", 27),
        ("left rostral middle frontal", 28), ("left superior frontal", 29),
        ("left superior parietal", 30), ("left superior temporal", 31),
        ("left supramarginal", 32), ("left frontal pole", 33),
        ("left temporal pole", 34), ("left transverse temporal", 35),
        ("left insula", 36), ("right corpus callosum", 37),
        ("right bankssts", 38), ("right caudal anterior cingulate", 39),
        ("right caudal middle frontal", 40), ("right cuneus", 42),
        ("right entorhinal", 43), ("right fusiform", 44),
        ("right inferior parietal", 45), ("right inferior temporal", 46),
        ("right isthmus cingulate", 47), ("right lateral occipital", 48),
        ("right lateral orbitofrontal", 49), ("right lingual", 50),
        ("right medial orbitofrontal", 51), ("right middle temporal", 52),
        ("right parahippocampal", 53), ("right paracentral", 54),
        ("right pars opercularis", 55), ("right pars orbitalis", 56),
        ("right pars triangularis", 57), ("right pericalcarine", 58),
        ("right postcentral", 59), ("right posterior cingulate", 60),
        ("right precentral", 61), ("right precuneus", 62),
        ("right rostral anterior cingulate", 63),
        ("right rostral middle frontal", 64), ("right superior frontal", 65),
        ("right superior parietal", 66), ("right superior temporal", 67),
        ("right supramarginal", 68), ("right frontal pole", 69),
        ("right temporal pole", 70), ("right transverse temporal", 71),
        ("right insula", 72)),
    "new_patch", Integer(),
    "segmentation_name_used", String(),
    "subject", ReadDiskItem("subject", "directory"),
    "gyri_texture", ReadDiskItem("Label Texture", "Aims texture formats"),
    "white_mesh", ReadDiskItem("Mesh", "Aims mesh formats"),
    "smoothing", Float(),
)


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
    
    # optional value
    self.setOptional("new_patch")

    # define the main node of a pipeline
    eNode = SerialExecutionNode(self.name, parameterized=self)

    ###########################################################################
    #        link of parameters for the "Bundles Filtering" process           #
    ###########################################################################
    eNode.addChild(
        "filter", ProcessExecutionNode("bundlesFiltering", optional=1))

    eNode.addDoubleLink("filter.database", "database")
    eNode.addDoubleLink("filter.formats_fiber_tracts", "formats_fiber_tracts")
    eNode.addDoubleLink("filter.study", "study")
    eNode.addDoubleLink("filter.patch", "patch")
    eNode.addDoubleLink("filter.new_patch", "new_patch")
    eNode.addDoubleLink("filter.segmentation_name_used",
                        "segmentation_name_used")
    eNode.addDoubleLink("filter.subject", "subject")
    eNode.addDoubleLink("filter.gyri_texture", "gyri_texture")
    eNode.addDoubleLink("filter.white_mesh", "white_mesh")

    ###########################################################################
    #        link of parameters with the "Fiber Oversampler" process          #
    ###########################################################################
    eNode.addChild(
        "oversampler", ProcessExecutionNode("fiberOversampler", optional=1))

    eNode.addDoubleLink("oversampler.filtered_length_distant_fibers",
                        "filter.subsets_of_distant_fibers")

    ###########################################################################
    #        link of parameters with the "Connectivity Matrix" process        #
    ###########################################################################
    eNode.addChild(
        "ConnectivityMatrix", ProcessExecutionNode("createConnectivityMatrix",
                                                   optional=1))

    eNode.addDoubleLink("ConnectivityMatrix.oversampled_distant_fibers",
                        "oversampler.oversampled_distant_fibers")
    eNode.addDoubleLink(
        "ConnectivityMatrix.filtered_length_fibers_near_cortex",
        "filter.subsets_of_fibers_near_cortex")
    eNode.addDoubleLink("ConnectivityMatrix.gyri_texture", "gyri_texture")
    eNode.addDoubleLink("ConnectivityMatrix.white_mesh", "white_mesh")
    eNode.addDoubleLink("ConnectivityMatrix.dw_to_t1", "filter.dw_to_t1")

    ###########################################################################
    #    link of parameters with the "Sum Sparse Matrix Smoothing" process    #
    ###########################################################################
    eNode.addChild(
        "smoothing", ProcessExecutionNode("sumSparseMatrix", optional=1))

    eNode.addDoubleLink("smoothing.matrix_of_fibers_near_cortex",
                        "ConnectivityMatrix.matrix_of_fibers_near_cortex")
    eNode.addDoubleLink("smoothing.white_mesh", "white_mesh")
    eNode.addDoubleLink("smoothing.gyri_texture", "gyri_texture")
    eNode.addDoubleLink("smoothing.smoothing", "smoothing")

    ###########################################################################
    #    link of parameters with the "Mean Connectivity Profile" process      #
    ###########################################################################
    eNode.addChild(
        "MeanProfile", ProcessExecutionNode("createMeanConnectivityProfile",
                                            optional=1))

    eNode.addDoubleLink("MeanProfile.complete_connectivity_matrix",
                        "smoothing.complete_connectivity_matrix")
    eNode.addDoubleLink("MeanProfile.gyri_texture", "gyri_texture")

    ###########################################################################
    #    link of parameters with the "Remove Internal Connections" process    #
    ###########################################################################
    eNode.addChild("InternalConnections",
                   ProcessExecutionNode("removeInternalConnections",
                                        optional=1))

    eNode.addDoubleLink("InternalConnections.patch_connectivity_profile",
                        "MeanProfile.patch_connectivity_profile")
    eNode.addDoubleLink("InternalConnections.gyri_texture", "gyri_texture")

    ###########################################################################
    #        link of parameters with the "Watershed" process                  #
    ###########################################################################
    eNode.addChild(
        "Watershed",
        ProcessExecutionNode("watershedReflectingConnectionsToGyrus",
                             optional=1, selected=False))

    eNode.addDoubleLink("Watershed.normed_connectivity_profile",
                        "InternalConnections.normed_connectivity_profile")

    ###########################################################################
    # link of parameters with the "Filtering Watershed" process               #
    ###########################################################################
    eNode.addChild("FilteringWatershed",
                   ProcessExecutionNode("filteringWatershed",
                                        optional=1, selected=False))

    eNode.addDoubleLink("FilteringWatershed.watershed", "Watershed.watershed")
    eNode.addDoubleLink("FilteringWatershed.complete_connectivity_matrix",
                        "MeanProfile.complete_connectivity_matrix")
    eNode.addDoubleLink("FilteringWatershed.gyri_texture", "gyri_texture")
    eNode.addDoubleLink("FilteringWatershed.white_mesh", "white_mesh")

    ###########################################################################
    #    link of parameters with the "Reduced Connectivity Matrix" process    #
    ###########################################################################
    eNode.addChild("ReducedMatrix",
                   ProcessExecutionNode("createReducedConnectivityMatrix",
                                        optional=1, selected=False))

    eNode.addDoubleLink("ReducedMatrix.complete_connectivity_matrix",
                        "FilteringWatershed.complete_connectivity_matrix")
    eNode.addDoubleLink("ReducedMatrix.gyri_texture", "gyri_texture")
    eNode.addDoubleLink("ReducedMatrix.white_mesh", "white_mesh")

    ###########################################################################
    #        link of parameters with the "Clustering" process                 #
    ###########################################################################
    eNode.addChild("ClusteringIntraSubjects",
                   ProcessExecutionNode("ClusteringIntrasubject",
                                        optional=1, selected=False))

    eNode.addDoubleLink("ClusteringIntraSubjects.reduced_connectivity_matrix",
                        "ReducedMatrix.reduced_connectivity_matrix")
    eNode.addDoubleLink(
        "ClusteringIntraSubjects.gyri_texture", "gyri_texture")
    eNode.addDoubleLink("ClusteringIntraSubjects.white_mesh", "white_mesh")

    self.setExecutionNode(eNode)
