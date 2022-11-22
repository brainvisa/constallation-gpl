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
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import neuroHierarchy
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


name = "Constellation Individual Clusters from atlas pipeline - MRtrix"
userLevel = 0

signature = Signature(
    "regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File", section="Nomenclature"),

    # inputs
    "outputs_database", Choice(section="Study parameters"),
    "study_name", OpenChoice(section="Study parameters"),
    "method", Choice(
        ("averaged approach", "avg"),
        ("concatenated approach", "concat"),
        section="Study parameters"),
    "region", OpenChoice(section="Study parameters"),

    # MRtrix data
    "tractography", ReadDiskItem("Fascicles bundles",
                                 "Aims readable bundles formats",
                                 section="Tractography inputs"),
    "apply_weights", Boolean(section="Tractography inputs"),
    "weights_file", ReadDiskItem("Fiber weights", "Text File",
                                 section="Tractography inputs"),

    # Freesurfer mesh / parcellation
    "dw_to_mesh", ReadDiskItem(
        "Transform T2 Diffusion MR to Raw T1 MRI", "Transformation matrix",
        section="Freesurfer data"),
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

    # atlas inputs
    "atlas_matrix", ReadDiskItem(
        "Connectivity Matrix", "Aims matrix formats",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "yes",
                            "intersubject": "yes",
                            "individual": "no"},
        section="Atlas inputs"),
    "filtered_reduced_group_profile", ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "yes",
                            "roi_filtered": "yes",
                            "intersubject": "yes",
                            "step_time": "no",
                            "measure": "no"},
        section="Atlas inputs"),
    "group_clustering", ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "no",
                            "roi_filtered": "no",
                            "intersubject": "yes",
                            "step_time": "yes",
                            "measure": "no"},
        section="Atlas inputs"),

    # options
    "regions_selection", Choice("All but main region", "All", "Custom",
                                section="Options"),
    "keep_regions", ListOf(OpenChoice(), section="Options", userLevel=2),
    "min_fibers_length", Float(section="Options"),
    "smoothing", Float(section="Options"),
    "kmax", Integer(section="Options"),
    "normalize", Boolean(section="Options"),
    "erase_smoothed_matrix", Boolean(section="Options"),

    # outputs
    "complete_individual_matrix", WriteDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "no",
                            "intersubject": "no",
                            "individual": "yes"},
        section="Outputs"),
    "complete_individual_smoothed_matrix", WriteDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "no",
                            "intersubject": "no",
                            "individual": "yes"},
        section="Outputs"),
    "reduced_matrix", WriteDiskItem(
        "Connectivity Matrix", "Aims matrix formats",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "yes",
                            "intersubject": "yes",
                            "individual": "yes"},
        section="Outputs"),
    "individual_clustering", WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "no",
                            "roi_filtered": "no",
                            "intersubject": "yes",
                            "step_time": "yes",
                            "measure": "no"},
        section="Outputs"),

)


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

    self.erase_smoothed_matrix = True
    self.setOptional("weights_file")
    self.method = "avg"
    self.apply_weights = True

    def link_keep_regions(self, dummy):
        """
        """
        from constel.lib.utils.filetools import read_nomenclature_file
        if self.regions_nomenclature is not None:
            self.keep_regions = None
            s = []
            s += read_nomenclature_file(
                self.regions_nomenclature.fullPath(), mode=2)
            self.signature["keep_regions"] = ListOf(Choice(*s),
                                                    section="Options")
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
                        _type="Connectivity Matrix")])
            else:
                choices = []
        self.signature["study_name"].setChoices(*sorted(choices))
        if len(choices) != 0 and self.isDefault("study_name") \
                and self.study_name not in choices:
            self.setValue("study_name", list(choices)[0], True)

    def reset_label(self, dummy):
        """Read and/or reset the region parameter.

        This callback reads the labels nomenclature and proposes them in the
        signature 'region' of process.
        It also resets the region parameter to default state after
        the nomenclature changes.
        """
        from constel.lib.utils.filetools import read_nomenclature_file
        current = self.region
        self.setValue("region", current, True)
        if self.regions_nomenclature is not None:
            s = [("Select a region in this list", None)]
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

    def method_changed(self, dummy):
        """
        """
        signature = self.signature
        if self.method == "avg":
            signature["regions_parcellation"] = ReadDiskItem(
                "ROI Texture", "Aims texture formats",
                requiredAttributes={"side": "both", "vertex_corr": "Yes",
                                    "averaged": "Yes"},
                section="Freesurfer data")
            self.changeSignature(signature)
            self.setValue("regions_parcellation",
                          signature["regions_parcellation"].findValue(
                              self.tractography), True)
        else:
            signature["regions_parcellation"] = ReadDiskItem(
                "ROI Texture", "Aims texture formats",
                requiredAttributes={"side": "both", "vertex_corr": "Yes",
                                    "averaged": "No"},
                section="Freesurfer data")
            self.changeSignature(signature)
            self.setValue("regions_parcellation", link_label(self), True)
        fill_study_choice(self)

    def link_label(self, dummy=None):
        """
        """
        roi_type = self.signature["regions_parcellation"]
        if self.method == "avg" and self.study_name:
            res = roi_type.findValue(
                {"freesurfer_group_of_subjects": self.study_name})
            if res is None:
                res = roi_type.findValue(
                    {"group_of_subjects": self.study_name})
            return res
        elif self.method == "concat" and self.tractography is not None:
            res = roi_type.findValue(
                self.tractography)
            if res is None:
                res = roi_type.findValue(
                    self.tractography,
                    requiredAttributes={"_type": "BothResampledGyri"})
            return res

    def link_atlas_matrix(self, dummy):
        match = {
            "method": "avg",
            "gyrus": self.region,
        }
        return self.signature["atlas_matrix"].findValue(match)

    def link_reduced_matrix(self, dummy):
        if self.complete_individual_smoothed_matrix is not None \
                and self.atlas_matrix is not None:
            match = dict(
                self.complete_individual_smoothed_matrix.hierarchyAttributes())
            match.update({
                "group_of_subjects":
                    self.atlas_matrix.get("group_of_subjects"),
                "sid": self.complete_individual_smoothed_matrix.get("subject"),
                "reduced": "yes",
                "intersubject": "yes",
                "_format": "gz compressed NIFTI-1 image",
            })
            for att in ["name_serie", "tracking_session", "subject",
                        "analysis", "acquisition"]:
                if att in match:
                    del match[att]
            return self.signature["reduced_matrix"].findValue(match)

    def link_clusters(self, dummy):
        if self.reduced_matrix:
            match = dict(self.reduced_matrix.hierarchyAttributes())
            for att in ["name_serie", "tracking_session",  # "subject",
                        "analysis", "acquisition", "ends_labelled", "reduced",
                        "individual"]:
                if att in match:
                    del match[att]
            # artificially add format in match. If we do not do this, existing
            # (GIFTI) files and potential output ones (.tex) do not appear to
            # have the same attributes, and findValue() cannot decide.
            # strangely, findValues() returns 1 element....
            match["_format"] = 'GIFTI file'
            return self.signature["individual_clustering"].findValue(match)

    # link of parameters for autocompletion
    self.linkParameters(None,
                        ("outputs_database", "method"),
                        fill_study_choice)
    self.linkParameters(None,
                        "regions_nomenclature",
                        reset_label)
    self.linkParameters(None,
                        "regions_nomenclature",
                        link_keep_regions)
    self.addLink("keep_regions",
                 ("regions_nomenclature", "regions_selection", "region"),
                 self.link_keep_regions_value)
    self.linkParameters("atlas_matrix", "region", link_atlas_matrix)
    self.linkParameters("filtered_reduced_group_profile", "atlas_matrix")
    self.linkParameters("reduced_matrix",
                        ("complete_individual_smoothed_matrix",
                         "atlas_matrix"),
                        link_reduced_matrix)
    self.linkParameters("group_clustering", "atlas_matrix")
    self.linkParameters("individual_clustering", "reduced_matrix",
                        link_clusters)

    method_changed(self, self.method)

    # define the main node of a pipeline
    eNode = SerialExecutionNode(self.name, parameterized=self)

    ###########################################################################
    #    link of parameters with the pipeline:                                #
    #        "Individual Pipeline - MRtrix"                           #
    ###########################################################################

    eNode.addChild(
        "mrtrix_indiv",
        ProcessExecutionNode("constel_individual_pipeline_mrtrix",
                             optional=True))
    mrtrix_indiv = eNode.child("mrtrix_indiv")._process
    mrtrix_indiv.method = 'avg'
    mrtrix_indiv.executionNode().child("subpipeline").child(
        'MeanProfile').setSelected(False)
    mrtrix_indiv.executionNode().child("subpipeline").child(
        'InternalConnections').setSelected(False)
    eNode.addDoubleLink("outputs_database", "mrtrix_indiv.outputs_database")
    eNode.addDoubleLink("method", "mrtrix_indiv.method")
    eNode.addDoubleLink("study_name", "mrtrix_indiv.study_name")
    eNode.addDoubleLink("regions_nomenclature",
                        "mrtrix_indiv.regions_nomenclature")
    eNode.addDoubleLink("region", "mrtrix_indiv.region")
    eNode.addDoubleLink("regions_parcellation",
                        "mrtrix_indiv.regions_parcellation")
    eNode.addDoubleLink("individual_white_mesh",
                        "mrtrix_indiv.individual_white_mesh")
    eNode.addDoubleLink("tractography", "mrtrix_indiv.tractography")
    eNode.addDoubleLink("apply_weights", "mrtrix_indiv.apply_weights")
    eNode.addDoubleLink("weights_file", "mrtrix_indiv.weights_file")
    eNode.addDoubleLink("dw_to_mesh", "mrtrix_indiv.dw_to_mesh")
    eNode.addDoubleLink("regions_selection", "mrtrix_indiv.regions_selection")
    eNode.addDoubleLink("min_fibers_length", "mrtrix_indiv.min_fibers_length")
    eNode.addDoubleLink("smoothing", "mrtrix_indiv.smoothing")
    eNode.addDoubleLink("normalize", "mrtrix_indiv.normalize")
    eNode.addDoubleLink("erase_smoothed_matrix",
                        "mrtrix_indiv.erase_smoothed_matrix")
    eNode.addDoubleLink("kmax", "mrtrix_indiv.kmax")
    eNode.addDoubleLink(
        "complete_individual_matrix",
        "mrtrix_indiv.ConnectivityMatrix.complete_individual_matrix")
    eNode.addDoubleLink(
        "complete_individual_smoothed_matrix",
        "mrtrix_indiv.subpipeline.smoothing.complete_matrix_smoothed")
    self.signature["outputs_database"].setChoices(
        *mrtrix_indiv.signature["outputs_database"].values)
    self.signature["region"].setChoices(
        *mrtrix_indiv.signature["region"].values)
    self.min_fibers_length = mrtrix_indiv.min_fibers_length
    self.smoothing = mrtrix_indiv.smoothing
    self.kmax = mrtrix_indiv.kmax
    link_keep_regions(self, self)

    ###########################################################################
    #    link of parameters with the process:                                 #
    #        "Reduced Individual Matrices From Group Regions"                 #
    ###########################################################################

    eNode.addChild(
        "reduced_matrix",
        ProcessExecutionNode("constel_individual_reduced_matrix",
                             optional=True))
    eNode.child('reduced_matrix')._process.removeLink(
        "filtered_reduced_individual_profile", "complete_matrix_smoothed")
    eNode.child('reduced_matrix')._process.removeLink(
        "reduced_individual_matrix", "filtered_reduced_individual_profile")
    eNode.child('reduced_matrix')._process.signature[
        "filtered_reduced_individual_profile"] \
        = self.signature["filtered_reduced_group_profile"]
    eNode.child('reduced_matrix')._process.signature[
        "reduced_individual_matrix"] = self.signature["reduced_matrix"]

    eNode.addDoubleLink("complete_individual_smoothed_matrix",
                        "reduced_matrix.complete_matrix_smoothed")
    eNode.addDoubleLink("filtered_reduced_group_profile",
                        "reduced_matrix.filtered_reduced_individual_profile")
    eNode.addDoubleLink("regions_parcellation",
                        "reduced_matrix.regions_parcellation")
    eNode.addDoubleLink("reduced_matrix",
                        "reduced_matrix.reduced_individual_matrix")
    eNode.addDoubleLink("individual_white_mesh",
                        "reduced_matrix.individual_white_mesh")
    eNode.addDoubleLink("normalize",
                        "reduced_matrix.normalize")
    eNode.addDoubleLink("erase_smoothed_matrix",
                        "reduced_matrix.erase_smoothed_matrix")
    eNode.addDoubleLink("region",
                        "reduced_matrix.region")
    eNode.addDoubleLink("regions_nomenclature",
                        "reduced_matrix.regions_nomenclature")

    ###########################################################################
    #    link of parameters with the process:                                 #
    #        "Individual clusters from atlas"                                 #
    ###########################################################################

    eNode.addChild(
        "individual_clusters",
        ProcessExecutionNode("constel_indiv_clusters_from_atlas",
                             optional=True))
    eNode.addDoubleLink("reduced_matrix",
                        "individual_clusters.reduced_individual_matrix")
    eNode.addDoubleLink("atlas_matrix",
                        "individual_clusters.atlas_matrix")
    eNode.addDoubleLink("group_clustering",
                        "individual_clusters.group_clustering")
    eNode.addDoubleLink("individual_clustering",
                        "individual_clusters.individual_clustering")
    eNode.addDoubleLink("regions_parcellation",
                        "individual_clusters.individual_regions_parcellation")
    eNode.addDoubleLink("regions_nomenclature",
                        "individual_clusters.regions_nomenclature")
    eNode.addDoubleLink("region",
                        "individual_clusters.region")

    self.setExecutionNode(eNode)

    if len(self.signature["outputs_database"].values) != 0:
        self.outputs_database = self.signature["outputs_database"].values[0][0]
    self.regions_nomenclature \
        = eNode.child("mrtrix_indiv")._process.regions_nomenclature
