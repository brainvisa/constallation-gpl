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

# Package import
try:
    from constel.lib.utils.filetools import read_file
except:
    pass


# ---------------------------Header--------------------------------------------


name = "Constellation Individual Pipeline - FSL connectome"
userLevel = 0

signature = Signature(
    # --inputs--
    "outputs_database", Choice(),
    "study_name", OpenChoice(),
    "method", Choice(
        ("averaged approach", "avg"),
        ("concatenated approach", "concat")),
    "regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "region", OpenChoice(),
    "regions_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),
    "individual_white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes",
                            "inflated": "No",
                            "averaged": "No"}),
    "probtrackx_indir", ReadDiskItem("directory",
                                     "directory"),
    "outdir", ReadDiskItem("directory", "directory"),
    "keep_regions", ListOf(OpenChoice()),
    "min_fibers_length", Float(),
    "smoothing", Float(),
    "normalize", Boolean(),
    "kmax", Integer(),
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
    self.min_fibers_length = 20.0
    self.kmax = 12
    self.normalize = True
    self.regions_nomenclature = self.signature[
        "regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_keep_regions(self, dummy):
        """
        """
        if self.regions_nomenclature is not None:
            s = []
            s += read_file(
                self.regions_nomenclature.fullPath(), mode=2)
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
            s += read_file(
                self.regions_nomenclature.fullPath(), mode=2)
            self.signature["region"].setChoices(*s)
            if isinstance(self.signature["region"], OpenChoice):
                self.signature["region"] = Choice(*s)
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
                        "outputs_database",
                        fill_study_choice)
    self.linkParameters("keep_regions",
                        "regions_nomenclature",
                        link_keep_regions)

    # define the main node of a pipeline
    eNode = SerialExecutionNode(self.name, parameterized=self)

    ###########################################################################
    #    link of parameters with the process: "FSL connectome"                #
    ###########################################################################

    eNode.addChild(
        "confsl", ProcessExecutionNode("constel_fsl_connectome", optional=1))

    eNode.addDoubleLink("confsl.probtrackx_indir",
                        "probtrackx_indir")
    eNode.addDoubleLink("confsl.regions_parcellation",
                        "regions_parcellation")
    eNode.addDoubleLink("confsl.regions_nomenclature",
                        "regions_nomenclature")
    eNode.addDoubleLink("confsl.region",
                        "region")
    eNode.addDoubleLink("confsl.outdir",
                        "outdir")

    ###########################################################################
    #    link of parameters with the process: "Import FSL connectome"         #
    ###########################################################################

    eNode.addChild(
        "import", ProcessExecutionNode("import_fsl_connectome", optional=1))

    eNode.addDoubleLink("import.outputs_database",
                        "outputs_database")
    eNode.addDoubleLink("import.study_name",
                        "study_name")
    eNode.addDoubleLink("import.method",
                        "method")
    eNode.addDoubleLink("import.regions_nomenclature",
                        "confsl.regions_nomenclature")
    eNode.addDoubleLink("import.region",
                        "confsl.region")
    eNode.addDoubleLink("import.min_fibers_length",
                        "min_fibers_length")
    eNode.addDoubleLink("import.fsl_connectome",
                        "confsl.output_connectome")

    ###########################################################################
    #    "Constellation Individual Sub-pipeline"                              #
    ###########################################################################

    eNode.addChild("subpipeline",
                   ProcessExecutionNode("constel_individual_subpipeline",
                                        optional=1))

    eNode.addDoubleLink("subpipeline.complete_individual_matrix",
                        "import.complete_individual_matrix")
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

    self.setExecutionNode(eNode)

    fill_study_choice(self)
    if len(self.signature["study_name"].values) != 0:
        self.study_name = self.signature["study_name"].values[0][0]
