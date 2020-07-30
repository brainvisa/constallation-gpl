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


name = "Constellation Individual Pipeline -  Connectomist"
userLevel = 1

signature = Signature(
    "regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File", section="Nomenclature"),

    "outputs_database", Choice(section="Study parameters"),
    "study_name", OpenChoice(section="Study parameters"),
    "method", Choice(
        ("averaged approach", "avg"),
        ("concatenated approach", "concat"),
        section="Study parameters"),
    "region", OpenChoice(section="Study parameters"),

    # --inputs--
    "subject_indir", ReadDiskItem("subject", "directory",
                                  section="Tractography inputs"),

    "individual_white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes",
                            "inflated": "No",
                            "averaged": "No"},
        section="Freesurfer data"),
    "dw_to_t1", ReadDiskItem(
        "Transform T2 Diffusion MR to Raw T1 MRI", "Transformation matrix",
        section="Freesurfer data"),
    "regions_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"},
        section="Freesurfer data"),

    "regions_selection", Choice("All but main region", "All", "Custom",
                                section="Options"),
    "keep_regions", ListOf(OpenChoice(), section="Options"),
    "fiber_tracts_format", Choice("bundles", "trk", section="Options"),
    "min_fibers_length", Float(section="Options"),
    "max_fibers_length", Float(section="Options"),
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
    # list of possible databases, while respecting the ontology
    # ontology: brainvisa-3.2.0
    databases = [h.name for h in neuroHierarchy.hierarchies()
                 if h.fso.name == "brainvisa-3.2.0"]
    self.signature["outputs_database"].setChoices(*databases)
    if len(databases) != 0:
        self.outputs_database = databases[0]
    else:
        self.signature["outputs_database"] = OpenChoice(
                                                section="Study parameters")

    # default value
    self.smoothing = 3.0
    self.kmax = 12
    self.min_fibers_length = 20.
    self.max_fibers_length = 500.
    self.normalize = True
    self.erase_matrices = True
    self.regions_nomenclature = self.signature[
        "regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_keep_regions(self, dummy):
        """
        """
        if self.regions_nomenclature is not None:
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
                        _type="Filtered Fascicles Bundles")])
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
                              self.subject_indir), True)
        else:
            signature["regions_parcellation"] = ReadDiskItem(
                "ROI Texture", "Aims texture formats",
                requiredAttributes={"side": "both", "vertex_corr": "Yes",
                                    "averaged": "No"},
                section="Freesurfer data")
            self.changeSignature(signature)
            self.setValue("regions_parcellation", link_label(self), True)
        fill_study_choice(self)

    def linkMesh(self, dummy):
        """
        """
        if self.method == "avg":
            if self.regions_parcellation is not None:
                return self.signature["individual_white_mesh"].findValue(
                    self.regions_parcellation)
            return None
        else:
            if self.subject_indir is not None:
                atts = {"subject": self.subject_indir.get("subject")}
                return self.signature["individual_white_mesh"].findValue(atts)

    def link_label(self, dummy=None):
        """
        """
        roi_type = self.signature["regions_parcellation"]
        if self.method == "avg" and self.study_name:
            # just in case study_name corresponds to subjects group...
            res = roi_type.findValue(
                {"freesurfer_group_of_subjects": self.study_name})
            if res is None:
                res = roi_type.findValue(
                    {"group_of_subjects": self.study_name})
            return res
        elif self.method == "concat" and self.subject_indir is not None:
            res = roi_type.findValue(
                self.subject_indir)
            if res is None:
                res = roi_type.findValue(
                    self.subject_indir,
                    requiredAttributes={"_type": "BothResampledGyri"})
            return res

    # link of parameters for autocompletion
    self.linkParameters(None,
                        "regions_nomenclature",
                        reset_label)
    self.linkParameters(None,
                        "method",
                        method_changed)
    self.linkParameters("individual_white_mesh",
                        "subject_indir")
    self.linkParameters(None,
                        "outputs_database",
                        fill_study_choice)
    self.linkParameters("regions_parcellation",
                        ["study_name", "subject_indir", "method"],
                        link_label)
    self.linkParameters(None,
                        "regions_nomenclature",
                        link_keep_regions)
    self.addLink("keep_regions",
                 ("regions_nomenclature", "regions_selection", "region"),
                 self.link_keep_regions_value)

    method_changed(self, self.method)

    # define the main node of a pipeline
    eNode = SerialExecutionNode(self.name, parameterized=self)

    ###########################################################################
    #        link of parameters for the process: "Bundles Filtering"          #
    ###########################################################################

    eNode.addChild(
        "filter", ProcessExecutionNode("constel_brain_tracts_filtering",
                                       optional=1))

    eNode.addDoubleLink("filter.outputs_database",
                        "outputs_database")
    eNode.addDoubleLink("filter.fiber_tracts_format",
                        "fiber_tracts_format")
    eNode.addDoubleLink("filter.method",
                        "method")
    eNode.addDoubleLink("filter.region",
                        "region")
    eNode.addDoubleLink("filter.regions_nomenclature",
                        "regions_nomenclature")
    eNode.addDoubleLink("filter.study_name",
                        "study_name")
    eNode.addDoubleLink("filter.subject_indir",
                        "subject_indir")
    eNode.addDoubleLink("filter.regions_parcellation",
                        "regions_parcellation")
    eNode.addDoubleLink("filter.individual_white_mesh",
                        "individual_white_mesh")
    eNode.addDoubleLink("filter.dw_to_t1",
                        "dw_to_t1")
    eNode.addDoubleLink("filter.min_fibers_length",
                        "min_fibers_length")
    eNode.addDoubleLink("filter.max_fibers_length",
                        "max_fibers_length")

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
    eNode.addDoubleLink("ConnectivityMatrix.regions_nomenclature",
                        "regions_nomenclature")
    eNode.addDoubleLink("ConnectivityMatrix.region",
                        "region")
    eNode.addDoubleLink("ConnectivityMatrix.regions_parcellation",
                        "regions_parcellation")
    eNode.addDoubleLink("ConnectivityMatrix.individual_white_mesh",
                        "individual_white_mesh")
    eNode.addDoubleLink("ConnectivityMatrix.dw_to_t1",
                        "filter.dw_to_t1")

    ###########################################################################
    #    "Constellation Individual Sub-pipeline"                              #
    ###########################################################################

    eNode.addChild("subpipeline",
                   ProcessExecutionNode("constel_individual_subpipeline",
                                        optional=1))

    eNode.addDoubleLink("subpipeline.complete_individual_matrix",
                        "ConnectivityMatrix.complete_individual_matrix")
    eNode.addDoubleLink("subpipeline.regions_nomenclature",
                        "regions_nomenclature")
    eNode.addDoubleLink("subpipeline.region",
                        "region")
    eNode.addDoubleLink("subpipeline.regions_parcellation",
                        "regions_parcellation")
    eNode.addDoubleLink("subpipeline.individual_white_mesh",
                        "individual_white_mesh")
    eNode.addDoubleLink("subpipeline.regions_parcellation",
                        "regions_parcellation")
    eNode.addDoubleLink("subpipeline.smoothing",
                        "smoothing")
    eNode.addDoubleLink("subpipeline.normalize",
                        "normalize")
    eNode.addDoubleLink("subpipeline.kmax",
                        "kmax")
    eNode.addDoubleLink("subpipeline.keep_regions",
                        "keep_regions")
    eNode.addDoubleLink("subpipeline.erase_matrices",
                        "erase_matrices")

    self.setExecutionNode(eNode)

    fill_study_choice(self)
    if len(self.signature["study_name"].values) != 0:
        self.study_name = self.signature["study_name"].values[0][0]
