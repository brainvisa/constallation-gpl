############################################################################
#  This software and supporting documentation are distributed by
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
############################################################################

# BrainVisa module
from brainvisa.processes import *

name = "Constellation within-subject pipeline"
userLevel = 2

# Argument declaration
signature = Signature(
    "study", Choice(
        ("averaged approach", "avg"), ("concatenated approach", "concat")),
    "texture", String(),
    "patch", Choice(
        ("use_new_patch", None),
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
    "database", Choice(),
    "subject", ReadDiskItem("subject", "directory"),
    "gyri_texture", ReadDiskItem("Label Texture", "Aims texture formats"),
    "white_mesh", ReadDiskItem("Mesh", "Aims mesh formats"),
    "smoothing", Float(),
)


# Default values
def initialization(self):
    databases = [h.name for h in neuroHierarchy.hierarchies()
                 if h.fso.name == "brainvisa-3.2.0"]
    self.signature["database"].setChoices(*databases)
    if len(databases) != 0:
        self.database = databases[0]
    else:
        self.signature["database"] = OpenChoice()

    eNode = SerialExecutionNode(self.name, parameterized=self)

    # link of parameters with the "Bundles Filtering" process
    eNode.addChild(
        "Filter", ProcessExecutionNode("bundlesFiltering", optional=1))

    eNode.addDoubleLink("Filter.study", "study")
    eNode.addDoubleLink("Filter.texture", "texture")
    eNode.addDoubleLink("Filter.new_patch", "new_patch")
    eNode.addDoubleLink("Filter.patch", "patch")
    eNode.addDoubleLink("Filter.database", "database")
    eNode.addDoubleLink("Filter.subject", "subject")
    eNode.addDoubleLink("Filter.gyri_texture", "gyri_texture")
    eNode.addDoubleLink("Filter.white_mesh", "white_mesh")

    # link of parameters with the "Fiber Oversampled" process
    eNode.addChild(
        "Oversampler", ProcessExecutionNode("fiberOversampler", optional=1))

    eNode.addDoubleLink("Oversampler.filtered_length_distant_fibers",
                        "Filter.subsets_of_distant_fibers")

    # link of parameters with the "Connectivity Matrix" process
    eNode.addChild(
        "ConnectivityMatrix", ProcessExecutionNode("createConnectivityMatrix",
                                                   optional=1))

    eNode.addDoubleLink("ConnectivityMatrix.oversampled_distant_fibers",
                        "Oversampler.oversampled_distant_fibers")
    eNode.addDoubleLink(
        "ConnectivityMatrix.filtered_length_fibers_near_cortex",
        "Filter.subsets_of_fibers_near_cortex")
    eNode.addDoubleLink("ConnectivityMatrix.gyri_texture", "gyri_texture")
    eNode.addDoubleLink("ConnectivityMatrix.white_mesh", "white_mesh")
    eNode.addDoubleLink("ConnectivityMatrix.dw_to_t1", "Filter.dw_to_t1")

    # link of parameters with the "Sum Sparse Matrix Smoothing" process
    eNode.addChild(
        "Smoothing", ProcessExecutionNode("sumSparseMatrix", optional=1))

    eNode.addDoubleLink("Smoothing.matrix_of_fibers_near_cortex",
                        "ConnectivityMatrix.matrix_of_fibers_near_cortex")
    eNode.addDoubleLink("Smoothing.white_mesh", "white_mesh")
    eNode.addDoubleLink("Smoothing.gyri_texture", "gyri_texture")
    eNode.addDoubleLink("Smoothing.patch", "patch")
    eNode.addDoubleLink("Smoothing.smoothing", "smoothing")

    # link of parameters with the "Mean Connectivity Profile" process
    eNode.addChild(
        "MeanProfile", ProcessExecutionNode("createMeanConnectivityProfile",
                                            optional=1))

    eNode.addDoubleLink("MeanProfile.complete_connectivity_matrix",
                        "Smoothing.complete_connectivity_matrix")
    eNode.addDoubleLink("MeanProfile.gyri_texture", "gyri_texture")

    # link of parameters with the "Remove Internal Connections" process
    eNode.addChild("InternalConnections",
                   ProcessExecutionNode("removeInternalConnections",
                                        optional=1))

    eNode.addDoubleLink("InternalConnections.patch_connectivity_profile",
                        "MeanProfile.patch_connectivity_profile")
    eNode.addDoubleLink("InternalConnections.gyri_texture", "gyri_texture")
    eNode.addDoubleLink("InternalConnections.white_mesh", "white_mesh")

    # link of parameters with the "Watershed" process
    eNode.addChild(
        "Watershed",
        ProcessExecutionNode("watershedReflectingConnectionsToGyrus",
                             optional=1))

    eNode.addDoubleLink("Watershed.normed_connectivity_profile",
                        "InternalConnections.normed_connectivity_profile")
#    eNode.addDoubleLink("Watershed.white_mesh",
#                        "white_mesh")

    # link of parameters with the "Filtering Watershed" process
    eNode.addChild("FilteringWatershed",
                   ProcessExecutionNode("filteringWatershed",
                                        optional=1))

    eNode.addDoubleLink("FilteringWatershed.watershed", "Watershed.watershed")
    eNode.addDoubleLink("FilteringWatershed.complete_connectivity_matrix",
                        "MeanProfile.complete_connectivity_matrix")
    eNode.addDoubleLink("FilteringWatershed.gyri_texture", "gyri_texture")
    eNode.addDoubleLink("FilteringWatershed.white_mesh", "white_mesh")

    # link of parameters with the "Reduced Connectivity Matrix" process
    eNode.addChild("ReducedMatrix",
                   ProcessExecutionNode("createReducedConnectivityMatrix",
                                        optional=1))

    eNode.addDoubleLink("ReducedMatrix.complete_connectivity_matrix",
                        "FilteringWatershed.complete_connectivity_matrix")
    eNode.addDoubleLink("ReducedMatrix.gyri_texture", "gyri_texture")
    eNode.addDoubleLink("ReducedMatrix.white_mesh", "white_mesh")

    # link of parameters with the "Clustering" process
    eNode.addChild("ClusteringIntraSubjects",
                   ProcessExecutionNode("ClusteringIntrasubject",
                                        optional=1))

    eNode.addDoubleLink("ClusteringIntraSubjects.reduced_connectivity_matrix",
                        "ReducedMatrix.reduced_connectivity_matrix")
    eNode.addDoubleLink(
        "ClusteringIntraSubjects.gyri_texture", "gyri_texture")
    eNode.addDoubleLink("ClusteringIntraSubjects.white_mesh", "white_mesh")

    self.setExecutionNode(eNode)