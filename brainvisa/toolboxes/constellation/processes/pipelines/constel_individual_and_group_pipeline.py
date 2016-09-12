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


# axon python API modules
from brainvisa.processes import Float
from brainvisa.processes import String
from brainvisa.processes import Choice
from brainvisa.processes import Signature
from brainvisa.processes import OpenChoice
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import neuroHierarchy
from brainvisa.processes import ValidationError
from brainvisa.processes import SerialExecutionNode
from brainvisa.processes import ProcessExecutionNode

# constel module
try:
    from constel.lib.utils.filetools import read_file
except:
    raise ValidationError("Please make sure that constel module is installed.")


#----------------------------Header--------------------------------------------


name = "Constellation Individual And Group pipeline"
userLevel = 0

signature = Signature(
    # inputs
    "study_name", String(),
    "outputs_database", Choice(),
    "fiber_tracts_format", Choice("bundles", "trk"),
    "method", Choice(
        ("averaged approach", "avg"), ("concatenated approach", "concat")),
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "cortical_region", OpenChoice(),
    "subject_directory", ReadDiskItem("subject", "directory"),
    "cortical_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "smoothing", Float(),
    "constellation_subjects_group", ReadDiskItem("Group definition", "XML"),
    "new_study_name", String(),
    "average_mesh", ReadDiskItem("White Mesh", "Aims mesh formats",
                                 requiredAttributes={"side": "both",
                                                     "vertex_corr": "Yes",
                                                     "averaged": "Yes"}),
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

    # optional value
    self.setOptional("new_study_name")

    # default value
    self.smoothing = 3.0
    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_label(self, dummy):
        """Reads the ROIs nomenclature and proposes them in the signature
        'cortical_region' of process.
        """
        if self.cortical_regions_nomenclature is not None:
            s = ["Select a cortical_region in this list"]
            s += read_file(
                self.cortical_regions_nomenclature.fullPath(), mode=2)
            self.signature["cortical_region"].setChoices(*s)
            if isinstance(self.signature["cortical_region"], OpenChoice):
                self.signature["cortical_region"] = Choice(*s)
                self.changeSignature(self.signature)

    # link of parameters for autocompletion
    self.linkParameters(
        "cortical_region", "cortical_regions_nomenclature", link_label)

    eNode = SerialExecutionNode(self.name, parameterized=self)

    ###########################################################################
    #      link of parameters for the Constellation Individual Pipeline       #
    ###########################################################################

    eNode.addChild(
        "pipelineIntra", ProcessExecutionNode("constel_individual_pipeline",
                                              optional=1))

    eNode.pipelineIntra.removeLink("cortical_region",
                                   "cortical_regions_nomenclature")

    eNode.addDoubleLink("pipelineIntra.study_name", "study_name")
    eNode.addDoubleLink("pipelineIntra.outputs_database", "outputs_database")
    eNode.addDoubleLink("pipelineIntra.fiber_tracts_format",
                        "fiber_tracts_format")
    eNode.addDoubleLink("pipelineIntra.method", "method")
    eNode.addDoubleLink("pipelineIntra.cortical_regions_nomenclature",
                        "cortical_regions_nomenclature")
    eNode.addDoubleLink("pipelineIntra.cortical_region", "cortical_region")
    eNode.addDoubleLink("pipelineIntra.subject_directory", "subject_directory")
    eNode.addDoubleLink("pipelineIntra.cortical_parcellation",
                        "cortical_parcellation")
    eNode.addDoubleLink("pipelineIntra.white_mesh", "white_mesh")
    eNode.addDoubleLink("pipelineIntra.smoothing", "smoothing")

    ###########################################################################
    #        link of parameters for the Constellation Group Pipeline          #
    ###########################################################################

    eNode.addChild(
        "pipelineInter", ProcessExecutionNode("constel_group_pipeline",
                                              optional=1))

    eNode.pipelineInter.removeLink("cortical_region",
                                   "cortical_regions_nomenclature")
    eNode.pipelineInter.removeLink("average_mesh",
                                   "cortical_regions_nomenclature")

    eNode.addDoubleLink("pipelineInter.method", "method")
    eNode.addDoubleLink("pipelineInter.cortical_regions_nomenclature",
                        "cortical_regions_nomenclature")
    eNode.addDoubleLink("pipelineInter.cortical_region", "cortical_region")
    eNode.addDoubleLink("pipelineInter.study_name", "study_name")
    eNode.addDoubleLink("pipelineInter.new_study_name", "new_study_name")
    eNode.addDoubleLink("pipelineInter.smoothing", "smoothing")
    eNode.addDoubleLink("pipelineInter.constellation_subjects_group",
                        "constellation_subjects_group")
    eNode.addDoubleLink("pipelineInter.average_mesh", "average_mesh")

    self.setExecutionNode(eNode)
