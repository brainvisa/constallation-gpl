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
from soma.minf.api import registerClass, readMinf
from brainvisa.group_utils import Subject

# Plot constel module
try:
    import constel
except:
    raise ValidationError("Please make sure that constel module is installed.")

name = "Constellation inter-subject pipeline"
userLevel = 2

signature = Signature(
    "study", Choice(
        ("averaged approach", "avg"), ("concatenated approach", "concat")),
    "patch", Choice(
        ("*** use_new_patch ***"),
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
    "smoothing", Float(),
    "group", ReadDiskItem("Group definition", "XML"),
    "connectivity_profiles", ListOf(
        ReadDiskItem("Gyrus Connectivity Profile", "Aims texture formats")),
    "normed_connectivity_profiles", ListOf(
        ReadDiskItem("Normed Connectivity Profile", "Aims texture formats")),
    "average_mesh", ReadDiskItem("Mesh", "BrainVISA mesh formats"),
    "gyri_texture", ListOf(
        ReadDiskItem("Label Texture", "Aims texture formats")),
)


def linkGroup(self, param1):
    self.smoothing = 3.0
    eNode = self.executionNode()
    for node in eNode.children():
        if node.name() == "Parallel Node":
            node.addChild(
                "N%d" % len(list(node.children())), ProcessExecutionNode(
                    "createReducedConnectivityMatrixOnRangeOfSubjects",
                    optional=1))


def initialization(self):
    """Provides default values and link of parameters
    """
    self.addLink(None, "group", self.linkGroup)

    # default value
    self.smoothing = 3.0

    # optional value
    self.setOptional("new_patch")

    def link_profiles(self, dummy):
        """Function of link to determine the connectivity profiles
        """
        if self.group is not None:
            registerClass("minf_2.0", Subject, "Subject")
            groupOfSubjects = readMinf(self.group.fullPath())
            profiles = []
            for subject in groupOfSubjects:
                atts = dict(self.group.hierarchyAttributes())
                atts["study"] = self.study
                if self.new_patch is not None:
                    atts["gyrus"] = "G" + str(self.new_patch)
                else:
                    atts["gyrus"] = "G" + str(self.patch)
                atts["smoothing"] = str(self.smoothing)
                atts["texture"] = self.segmentation_name_used
                profile = ReadDiskItem(
                    "Gyrus Connectivity Profile", 
                    "Aims texture formats").findValue(
                        atts, subject.attributes())
                if profile is not None:
                    profiles.append(profile)
            return profiles

    # link of parameters
    self.linkParameters(
        "connectivity_profiles",
        ("study", "patch", "new_patch", "smoothing", "segmentation_name_used",
         "group"), link_profiles)
    self.linkParameters(
        "normed_connectivity_profiles", "connectivity_profiles")

    # visibility level for the user
    self.signature["connectivity_profiles"].userLevel = 3
    self.signature["normed_connectivity_profiles"].userLevel = 3

    # define the main node of a pipeline
    eNode = SerialExecutionNode(self.name, parameterized=self)

    ###########################################################################
    #        link of parameters for the "Creation of a mask" process          #
    ###########################################################################
    eNode.addChild("CreateMask",
                   ProcessExecutionNode(
                       "surfaceWithEnoughConnectionsCreation",
                       optional=1))

    eNode.addDoubleLink("CreateMask.group", "group")
    eNode.addDoubleLink(
        "CreateMask.connectivity_profiles", "connectivity_profiles")
    
    ###########################################################################
    #   link of parameters for the "Connectivity Profile of Group" process    #
    ###########################################################################
    eNode.addChild("ConnectivityProfileGroup",
                   ProcessExecutionNode(
                       "createConnectivityProfileOnRangeOfSubjects",
                       optional=1))

    eNode.addDoubleLink("ConnectivityProfileGroup.group", "group")
    eNode.addDoubleLink(
        "ConnectivityProfileGroup.normed_connectivity_profiles",
        "normed_connectivity_profiles")
    
    ###########################################################################
    #link of parameters for the "Normed Connectivity Profile of Group" process#
    ###########################################################################
    eNode.addChild("NormedProfileGroup",
                   ProcessExecutionNode(
                       "removeInternalConnectionsOnRangeOfSubjects",
                       optional=1))

    eNode.addDoubleLink("NormedProfileGroup.mask", "CreateMask.mask")
                        
    ###########################################################################
    #        link of parameters for the "Watershed of Group" process          #
    ###########################################################################
    eNode.addChild("WatershedGroup",
                   ProcessExecutionNode("filteringWatershedOnRangeOfSubjects",
                                        optional=1))

    eNode.addDoubleLink("WatershedGroup.average_mesh", "average_mesh")
    eNode.addDoubleLink("WatershedGroup.normed_connectivity_profile",
                        "NormedProfileGroup.normed_connectivity_profile")
                        
    ###########################################################################
    #    link of parameters for the "Reduced Connectivity Matrix" process     #
    ###########################################################################
    eNode.addChild("ReducedMatrixGroup",
                   ProcessExecutionNode(
                       "createReducedConnectivityMatrixOnRangeOfSubjects",
                       optional=1))

    eNode.addDoubleLink("ReducedMatrixGroup.group", "group")
    eNode.addDoubleLink("ReducedMatrixGroup.average_mesh", "average_mesh")
    eNode.addDoubleLink("ReducedMatrixGroup.gyri_texture", "gyri_texture")
    eNode.addDoubleLink("ReducedMatrixGroup.filtered_watershed",
                        "WatershedGroup.filtered_watershed")
                        
    ###########################################################################
    #        link of parameters for the "Clustering of Group" process         #
    ###########################################################################
    eNode.addChild("ClusteringGroup",
                   ProcessExecutionNode("clusteringInterSubjects",
                                        optional=1))

    eNode.addDoubleLink("ClusteringGroup.group", "group")
    eNode.addDoubleLink("ClusteringGroup.study", "study")
    eNode.addDoubleLink("ClusteringGroup.average_mesh", "average_mesh")
    eNode.addDoubleLink("ClusteringGroup.gyri_texture", "gyri_texture")
    eNode.addDoubleLink("ClusteringGroup.reduced_connectivity_matrix",
                        "ReducedMatrixGroup.reduced_connectivity_matrix")

    self.setExecutionNode(eNode)
