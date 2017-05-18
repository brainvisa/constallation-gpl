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
    - the signature of the inputs/ouputs,
    - the initialization (by default) of the inputs,
    - the interlinkages between inputs/outputs.

Main dependencies: axon python API, constel

Author: Sandrine Lefranc, 2015
"""

# ---------------------------Imports-------------------------------------------


# axon python API modules
from brainvisa.processes import Float
from brainvisa.processes import Choice
from brainvisa.processes import ListOf
from brainvisa.processes import Boolean
from brainvisa.processes import Signature
from brainvisa.processes import OpenChoice
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import neuroHierarchy
from brainvisa.processes import SerialExecutionNode
from brainvisa.processes import ProcessExecutionNode

# constel module
try:
    from constel.lib.utils.filetools import read_file
except:
    pass


# ---------------------------Header--------------------------------------------


name = "Constellation Individual Pipeline"
userLevel = 0

signature = Signature(
    # --inputs--
    "method", Choice(
        ("averaged approach", "avg"),
        ("concatenated approach", "concat")),
    "outputs_database", Choice(),
    "study_name", OpenChoice(),
    "fiber_tracts_format", Choice("bundles", "trk"),
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "cortical_region", OpenChoice(),
    "subject_directory", ReadDiskItem("subject", "directory"),
    "cortical_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes",
                            "inflated": "No",
                            "averaged": "No"}),
    "keep_regions", ListOf(OpenChoice()),
    "smoothing", Float(),
    "minlength_labeled_fibers", Float(),
    "maxlength_labeled_fibers", Float(),
    "minlength_semilabeled_fibers", Float(),
    "maxlength_semilabeled_fibers", Float(),
    "normalize", Boolean(),
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters.
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
    self.minlength_labeled_fibers = 30.
    self.maxlength_labeled_fibers = 500.
    self.minlength_semilabeled_fibers = 20.
    self.maxlength_semilabeled_fibers = 500.
    self.normalize = True
    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_keep_regions(self, dummy):
        """
        """
        if self.cortical_regions_nomenclature is not None:
            s = []
            s += read_file(
                self.cortical_regions_nomenclature.fullPath(), mode=2)
            self.signature["keep_regions"] = ListOf(Choice(*s))
            self.changeSignature(self.signature)

    def fill_study_choice(self, dummy=None):
        """
        """
        choices = set()
        if self.outputs_database is not None:
            if neuroHierarchy.databases.hasDatabase(self.outputs_database):
                database = neuroHierarchy.databases.database(
                    self.outputs_database)
                sel = {"method": self.method}
                choices.update(
                    [x[0] for x in database.findAttributes(
                        ["studyname"], selection=sel,
                        _type="Filtered Fascicles Bundles")])
            else:
                choices = []
        self.signature["study_name"].setChoices(*sorted(choices))
        if len(choices) != 0 and self.isDefault("study_name") \
                and self.study_name not in choices:
            self.setValue("study_name", list(choices)[0], True)

    def reset_label(self, dummy):
        """Read and/or reset the cortical_region parameter.

        This callback reads the labels nomenclature and proposes them in the
        signature 'cortical_region' of process.
        It also resets the cortical_region parameter to default state after
        the nomenclature changes.
        """
        current = self.cortical_region
        self.setValue("cortical_region", current, True)
        if self.cortical_regions_nomenclature is not None:
            s = [("Select a cortical_region in this list", None)]
            # temporarily set a value which will remain valid
            self.cortical_region = s[0][1]
            s += read_file(
                self.cortical_regions_nomenclature.fullPath(), mode=2)
            self.signature["cortical_region"].setChoices(*s)
            if isinstance(self.signature["cortical_region"], OpenChoice):
                self.signature["cortical_region"] = Choice(*s)
                self.changeSignature(self.signature)
            if current not in s:
                self.setValue("cortical_region", s[0][1], True)
            else:
                self.setValue("cortical_region", current, True)

    def method_changed(self, dummy):
        """
        """
        signature = self.signature
        if self.method == "avg":
            signature["cortical_parcellation"] = ReadDiskItem(
                "ROI Texture", "Aims texture formats",
                requiredAttributes={"side": "both", "vertex_corr": "Yes",
                                    "averaged": "Yes"})
            self.changeSignature(signature)
            self.setValue("cortical_parcellation",
                          signature["cortical_parcellation"].findValue(
                              self.subject_directory), True)
        else:
            signature["cortical_parcellation"] = ReadDiskItem(
                "ROI Texture", "Aims texture formats",
                requiredAttributes={"side": "both", "vertex_corr": "Yes",
                                    "averaged": "No"})
            self.changeSignature(signature)
            self.setValue("cortical_parcellation", link_label(self), True)
        fill_study_choice(self)

    def linkMesh(self, dummy):
        """
        """
        if self.method == "avg":
            if self.cortical_parcellation is not None:
                return self.signature["white_mesh"].findValue(
                    self.cortical_parcellation)
            return None
        else:
            if self.subject_directory is not None:
                atts = {"subject": self.subject_directory.get("subject")}
                return self.signature["white_mesh"].findValue(atts)

    def link_label(self, dummy=None):
        """
        """
        roi_type = self.signature["cortical_parcellation"]
        if self.method == "avg" and self.study_name:
            # just in case study_name corresponds to subjects group...
            res = roi_type.findValue(
                {"freesurfer_group_of_subjects": self.study_name})
            if res is None:
                res = roi_type.findValue(
                    {"group_of_subjects": self.study_name})
            return res
        elif self.method == "concat" and self.subject_directory is not None:
            res = roi_type.findValue(
                self.subject_directory)
            if res is None:
                res = roi_type.findValue(
                    self.subject_directory,
                    requiredAttributes={"_type": "BothResampledGyri"})
            return res

    # link of parameters for autocompletion
    self.linkParameters(None, "cortical_regions_nomenclature", reset_label)
    self.linkParameters(None, "method", method_changed)
    self.linkParameters("white_mesh", "subject_directory")
    method_changed(self, self.method)
    self.linkParameters(None, "outputs_database", fill_study_choice)
    self.linkParameters("cortical_parcellation",
                        ["study_name", "subject_directory", "method"],
                        link_label)
    self.linkParameters(
        "keep_regions", "cortical_regions_nomenclature",
        link_keep_regions)

    # define the main node of a pipeline
    eNode = SerialExecutionNode(self.name, parameterized=self)

    ###########################################################################
    #        link of parameters for the process: "Bundles Filtering"          #
    ###########################################################################

    eNode.addChild(
        "filter", ProcessExecutionNode("constel_brain_tracts_filtering",
                                       optional=1))

    eNode.addDoubleLink("filter.outputs_database", "outputs_database")
    eNode.addDoubleLink("filter.fiber_tracts_format", "fiber_tracts_format")
    eNode.addDoubleLink("filter.method", "method")
    eNode.addDoubleLink("filter.cortical_region", "cortical_region")
    eNode.addDoubleLink("filter.cortical_regions_nomenclature",
                        "cortical_regions_nomenclature")
    eNode.addDoubleLink("filter.study_name", "study_name")
    eNode.addDoubleLink("filter.subject_directory", "subject_directory")
    eNode.addDoubleLink("filter.cortical_parcellation",
                        "cortical_parcellation")
    eNode.addDoubleLink("filter.white_mesh", "white_mesh")
    eNode.addDoubleLink("filter.minlength_labeled_fibers",
                        "minlength_labeled_fibers")
    eNode.addDoubleLink("filter.maxlength_labeled_fibers",
                        "maxlength_labeled_fibers")
    eNode.addDoubleLink("filter.minlength_semilabeled_fibers",
                        "minlength_semilabeled_fibers")
    eNode.addDoubleLink("filter.maxlength_semilabeled_fibers",
                        "maxlength_semilabeled_fibers")

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
    eNode.addDoubleLink("ConnectivityMatrix.labeled_fibers",
                        "filter.labeled_fibers")
    eNode.addDoubleLink("ConnectivityMatrix.cortical_regions_nomenclature",
                        "cortical_regions_nomenclature")
    eNode.addDoubleLink("ConnectivityMatrix.cortical_region",
                        "cortical_region")
    eNode.addDoubleLink("ConnectivityMatrix.cortical_parcellation",
                        "cortical_parcellation")
    eNode.addDoubleLink("ConnectivityMatrix.white_mesh", "white_mesh")
    eNode.addDoubleLink("ConnectivityMatrix.dw_to_t1", "filter.dw_to_t1")

    ###########################################################################
    #    link of parameters with the process: "Sum Sparse Matrix Smoothing"   #
    ###########################################################################

    eNode.addChild(
        "smoothing", ProcessExecutionNode("constel_smooth_matrix", optional=1))

    eNode.addDoubleLink("smoothing.complete_individual_matrix",
                        "ConnectivityMatrix.complete_individual_matrix")
    eNode.addDoubleLink("smoothing.cortical_regions_nomenclature",
                        "ConnectivityMatrix.cortical_regions_nomenclature")
    eNode.addDoubleLink("smoothing.cortical_region",
                        "ConnectivityMatrix.cortical_region")
    eNode.addDoubleLink("smoothing.white_mesh", "white_mesh")
    eNode.addDoubleLink("smoothing.cortical_parcellation",
                        "cortical_parcellation")
    eNode.addDoubleLink("smoothing.smoothing", "smoothing")

    ###########################################################################
    #    link of parameters with the process: "Mean Connectivity Profile"     #
    ###########################################################################

    eNode.addChild(
        "MeanProfile", ProcessExecutionNode("constel_mean_individual_profile",
                                            optional=1))

    eNode.addDoubleLink("MeanProfile.complete_individual_matrix",
                        "smoothing.complete_individual_matrix")
    eNode.addDoubleLink("MeanProfile.cortical_regions_nomenclature",
                        "smoothing.cortical_regions_nomenclature")
    eNode.addDoubleLink("MeanProfile.cortical_region",
                        "smoothing.cortical_region")
    eNode.addDoubleLink("MeanProfile.cortical_parcellation",
                        "cortical_parcellation")

    ###########################################################################
    #    link of parameters with the process: "Remove Internal Connections"   #
    ###########################################################################

    eNode.addChild("InternalConnections",
                   ProcessExecutionNode("constel_normalize_individual_profile",
                                        optional=1))

    eNode.addDoubleLink("InternalConnections.mean_individual_profile",
                        "MeanProfile.mean_individual_profile")
    eNode.addDoubleLink("InternalConnections.cortical_regions_nomenclature",
                        "MeanProfile.cortical_regions_nomenclature")
    eNode.addDoubleLink("InternalConnections.cortical_region",
                        "MeanProfile.cortical_region")
    eNode.addDoubleLink("InternalConnections.cortical_parcellation",
                        "cortical_parcellation")
    eNode.addDoubleLink("InternalConnections.keep_regions",
                        "keep_regions")

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
    eNode.addDoubleLink("FilteringWatershed.cortical_regions_nomenclature",
                        "MeanProfile.cortical_regions_nomenclature")
    eNode.addDoubleLink("FilteringWatershed.cortical_region",
                        "MeanProfile.cortical_region")
    eNode.addDoubleLink("FilteringWatershed.cortical_parcellation",
                        "cortical_parcellation")
    eNode.addDoubleLink("FilteringWatershed.white_mesh", "white_mesh")

    ###########################################################################
    #    link of parameters with the process: "Reduced Connectivity Matrix"   #
    ###########################################################################

    eNode.addChild("ReducedMatrix",
                   ProcessExecutionNode("constel_individual_reduced_matrix",
                                        optional=1, selected=False))

    eNode.addDoubleLink("ReducedMatrix.complete_individual_matrix",
                        "FilteringWatershed.complete_individual_matrix")
    eNode.addDoubleLink("ReducedMatrix.cortical_regions_nomenclature",
                        "FilteringWatershed.cortical_regions_nomenclature")
    eNode.addDoubleLink("ReducedMatrix.cortical_region",
                        "FilteringWatershed.cortical_region")
    eNode.addDoubleLink("ReducedMatrix.cortical_parcellation",
                        "cortical_parcellation")
    eNode.addDoubleLink("ReducedMatrix.white_mesh", "white_mesh")
    eNode.addDoubleLink("ReducedMatrix.normalize", "normalize")

    ###########################################################################
    #        link of parameters with the process: "Clustering"                #
    ###########################################################################

    eNode.addChild("ClusteringIntraSubjects",
                   ProcessExecutionNode("constel_individual_clustering",
                                        optional=1, selected=False))

    eNode.ClusteringIntraSubjects.removeLink("cortical_parcellation",
                                             "white_mesh")
    eNode.addDoubleLink("ClusteringIntraSubjects.reduced_individual_matrix",
                        "ReducedMatrix.reduced_individual_matrix")
    eNode.addDoubleLink("ClusteringIntraSubjects.cortical_regions_nomenclature",
                        "ReducedMatrix.cortical_regions_nomenclature")
    eNode.addDoubleLink("ClusteringIntraSubjects.cortical_region",
                        "ReducedMatrix.cortical_region")
    eNode.addDoubleLink("ClusteringIntraSubjects.cortical_parcellation",
                        "cortical_parcellation")
    eNode.addDoubleLink("ClusteringIntraSubjects.white_mesh", "white_mesh")

    self.setExecutionNode(eNode)

    fill_study_choice(self)
    if len(self.signature["study_name"].values) != 0:
        self.study_name = self.signature["study_name"].values[0][0]
