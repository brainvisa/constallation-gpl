###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################


# ---------------------------Imports-------------------------------------------


# Axon python API modules
from __future__ import absolute_import
from brainvisa.processes import Float
from brainvisa.processes import Choice
from brainvisa.processes import ListOf
from brainvisa.processes import Boolean
from brainvisa.processes import Integer
from brainvisa.processes import Signature
from brainvisa.processes import OpenChoice
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import SerialExecutionNode
from brainvisa.processes import ProcessExecutionNode
from brainvisa.processes import ValidationError


def validation(self):
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    try:
        from constel.lib.utils.filetools import read_nomenclature_file
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ---------------------------Header--------------------------------------------


name = "Constellation Individual Sub-Pipeline"
userLevel = 2

signature = Signature(
    "regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File", section="Nomenclature"),

    "region", OpenChoice(section="Study parameters"),

    # --inputs--
    "complete_individual_matrix", ReadDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "no",
                            "intersubject": "no"},
        section="Input matrix"),

    "individual_white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes",
                            "inflated": "No",
                            "averaged": "No"},
        section="Freesurfer data"),
    "regions_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"},
        section="Freesurfer data"),

    "regions_selection", Choice("All but main region", "All", "Custom",
                                section="Options"),
    "keep_regions", ListOf(OpenChoice(), section="Options"),
    "smoothing", Float(section="Options"),
    "kmax", Integer(section="Options"),
    "normalize", Boolean(section="Options"),
    "erase_matrices", Boolean(section="Options")

)


# ---------------------------Functions-----------------------------------------

def link_keep_regions_value(self, dummy, other=None, oother=None):
    s = [x[1] for x in self.signature["keep_regions"].contentType.values
         if x[1] is not None]
    if self.regions_selection == "All":
        keep_regions = s
    elif self.regions_selection == "All but main region":
        keep_regions = [x for x in s if x != self.region]
    else:
        keep_regions = None
    return keep_regions


def initialization(self):
    """Provides default values and link of parameters.
    """
    from constel.lib.utils.filetools import read_nomenclature_file
    # default value
    self.smoothing = 3.0
    self.kmax = 12
    self.normalize = True
    self.erase_matrices = True
    self.regions_nomenclature = self.signature[
        "regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_keep_regions(self, dummy):
        """
        """
        if self.regions_nomenclature is not None:
            self.keep_regions = None
            s = []
            s += read_nomenclature_file(
                self.regions_nomenclature.fullPath(), mode=2)
            self.signature["keep_regions"] = ListOf(Choice(*s),
                                                    section="Options")
            self.changeSignature(self.signature)

    def reset_label(self, dummy):
        """Read and/or reset the region parameter.

        This callback reads the labels nomenclature and proposes them in the
        signature 'region' of process.
        It also resets the region parameter to default state after
        the nomenclature changes.
        """
        current = self.region
        self.setValue("region", current, True)
        if self.regions_nomenclature is not None:
            s = [("Select a region in this list", None)]
            # temporarily set a value which will remain valid
            self.region = s[0][1]
            s += read_nomenclature_file(
                self.regions_nomenclature.fullPath(), mode=2)
            self.signature["region"].setChoices(*s)
            if isinstance(self.signature["region"], OpenChoice):
                self.signature["region"] = Choice(*s,
                                                  section="Study parameters")
                self.changeSignature(self.signature)
            if current not in s:
                self.setValue("region", s[0][1], True)
            else:
                self.setValue("region", current, True)

    # link of parameters for autocompletion
    self.linkParameters(None,
                        "regions_nomenclature",
                        reset_label)
    self.linkParameters(None,
                        "regions_nomenclature",
                        link_keep_regions)
    self.addLink("keep_regions",
                 ("regions_nomenclature", "regions_selection", "region"),
                 self.link_keep_regions_value)

    # define the main node of a pipeline
    eNode = SerialExecutionNode(self.name, parameterized=self)

    ###########################################################################
    #    link of parameters with the process: "Smoothing Individual Matrix"   #
    ###########################################################################

    eNode.addChild(
        "smoothing", ProcessExecutionNode("constel_smooth_matrix", optional=1))

    eNode.addDoubleLink("smoothing.complete_individual_matrix",
                        "complete_individual_matrix")
    eNode.addDoubleLink("smoothing.regions_nomenclature",
                        "regions_nomenclature")
    eNode.addDoubleLink("smoothing.region",
                        "region")
    eNode.addDoubleLink("smoothing.individual_white_mesh",
                        "individual_white_mesh")
    eNode.addDoubleLink("smoothing.regions_parcellation",
                        "regions_parcellation")
    eNode.addDoubleLink("smoothing.smoothing",
                        "smoothing")
    eNode.addDoubleLink("smoothing.erase_matrices",
                        "erase_matrices")

    ###########################################################################
    #    link of parameters with the process: "Mean Connectivity Profile"     #
    ###########################################################################

    eNode.addChild(
        "MeanProfile", ProcessExecutionNode("constel_mean_individual_profile",
                                            optional=1))

    eNode.addDoubleLink("MeanProfile.complete_matrix_smoothed",
                        "smoothing.complete_matrix_smoothed")
    eNode.addDoubleLink("MeanProfile.regions_nomenclature",
                        "regions_nomenclature")
    eNode.addDoubleLink("MeanProfile.region",
                        "region")
    eNode.addDoubleLink("MeanProfile.regions_parcellation",
                        "regions_parcellation")
    eNode.addDoubleLink("MeanProfile.erase_matrices",
                        "erase_matrices")
    ###########################################################################
    #    link of parameters with the process: "Remove Internal Connections"   #
    ###########################################################################

    eNode.addChild("InternalConnections",
                   ProcessExecutionNode("constel_normalize_individual_profile",
                                        optional=1))

    eNode.addDoubleLink("InternalConnections.mean_individual_profile",
                        "MeanProfile.mean_individual_profile")
    eNode.addDoubleLink("InternalConnections.regions_nomenclature",
                        "regions_nomenclature")
    eNode.addDoubleLink("InternalConnections.region",
                        "region")
    eNode.addDoubleLink("InternalConnections.regions_parcellation",
                        "regions_parcellation")

    ###########################################################################
    #        link of parameters with the process: "Watershed"                 #
    ###########################################################################

    eNode.addChild(
        "Watershed",
        ProcessExecutionNode("constel_individual_high_connectivity_regions",
                             optional=1, selected=False))

    eNode.addDoubleLink("Watershed.normed_individual_profile",
                        "InternalConnections.normed_individual_profile")
    eNode.addDoubleLink("Watershed.individual_white_mesh",
                        "individual_white_mesh")

    ###########################################################################
    # link of parameters with the process: "Filtering Watershed"              #
    ###########################################################################

    eNode.addChild("FilteringWatershed",
                   ProcessExecutionNode("constel_individual_regions_filtering",
                                        optional=1, selected=False))

    eNode.addDoubleLink("FilteringWatershed.reduced_individual_profile",
                        "Watershed.reduced_individual_profile")
    eNode.addDoubleLink("FilteringWatershed.complete_matrix_smoothed",
                        "MeanProfile.complete_matrix_smoothed")
    eNode.addDoubleLink("FilteringWatershed.regions_nomenclature",
                        "regions_nomenclature")
    eNode.addDoubleLink("FilteringWatershed.region",
                        "region")
    eNode.addDoubleLink("FilteringWatershed.regions_parcellation",
                        "regions_parcellation")
    eNode.addDoubleLink("FilteringWatershed.individual_white_mesh",
                        "individual_white_mesh")

    ###########################################################################
    #    link of parameters with the process: "Reduced Connectivity Matrix"   #
    ###########################################################################

    eNode.addChild("ReducedMatrix",
                   ProcessExecutionNode("constel_individual_reduced_matrix",
                                        optional=1, selected=False))

    eNode.addDoubleLink("ReducedMatrix.complete_matrix_smoothed",
                        "FilteringWatershed.complete_matrix_smoothed")
    eNode.addDoubleLink("ReducedMatrix.regions_nomenclature",
                        "regions_nomenclature")
    eNode.addDoubleLink("ReducedMatrix.region",
                        "region")
    eNode.addDoubleLink("ReducedMatrix.regions_parcellation",
                        "regions_parcellation")
    eNode.addDoubleLink("ReducedMatrix.individual_white_mesh",
                        "individual_white_mesh")
    eNode.addDoubleLink("ReducedMatrix.normalize",
                        "normalize")

    ###########################################################################
    #        link of parameters with the process: "Clustering"                #
    ###########################################################################

    eNode.addChild("ClusteringIntraSubjects",
                   ProcessExecutionNode("constel_individual_clustering",
                                        optional=1, selected=False))

    eNode.addDoubleLink("ClusteringIntraSubjects.reduced_individual_matrix",
                        "ReducedMatrix.reduced_individual_matrix")
    eNode.addDoubleLink("ClusteringIntraSubjects.regions_nomenclature",
                        "regions_nomenclature")
    eNode.addDoubleLink("ClusteringIntraSubjects.region",
                        "region")
    eNode.addDoubleLink("ClusteringIntraSubjects.regions_parcellation",
                        "regions_parcellation")
    eNode.addDoubleLink("ClusteringIntraSubjects.individual_white_mesh",
                        "individual_white_mesh")
    eNode.addDoubleLink("ClusteringIntraSubjects.kmax",
                        "kmax")

    self.setExecutionNode(eNode)
