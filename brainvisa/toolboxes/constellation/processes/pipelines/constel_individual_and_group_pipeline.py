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


from brainvisa.processes import Signature, String, Choice, ReadDiskItem, \
    Float, SerialExecutionNode, ProcessExecutionNode, neuroHierarchy, \
    ValidationError, OpenChoice

# constel module
try:
    from constel.lib.utils.files import read_file
except:
    raise ValidationError("Please make sure that constel module is installed.")


#----------------------------Header--------------------------------------------


name = "Constellation Individual And Group pipeline"
userLevel = 0

signature = Signature(
    # inputs
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
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "smoothing", Float(),
    "subjects_group", ReadDiskItem("Group definition", "XML"),
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

    # link of parameters for autocompletion
    self.linkParameters("ROI", "ROIs_nomenclature", link_roi)
    eNode = SerialExecutionNode(self.name, parameterized=self)

    ###########################################################################
    #      link of parameters for the Constellation Individual Pipeline       #
    ###########################################################################

    eNode.addChild(
        "pipelineIntra", ProcessExecutionNode("constel_individual_pipeline",
                                              optional=1))

    eNode.pipelineIntra.removeLink("ROI", "ROIs_nomenclature")

    eNode.addDoubleLink("pipelineIntra.study_name", "study_name")
    eNode.addDoubleLink("pipelineIntra.outputs_database", "outputs_database")
    eNode.addDoubleLink(
        "pipelineIntra.format_fiber_tracts", "format_fiber_tracts")
    eNode.addDoubleLink("pipelineIntra.method", "method")
    eNode.addDoubleLink("pipelineIntra.ROIs_nomenclature", "ROIs_nomenclature")
    eNode.addDoubleLink("pipelineIntra.ROI", "ROI")
    eNode.addDoubleLink("pipelineIntra.dirsubject", "dirsubject")
    eNode.addDoubleLink("pipelineIntra.ROIs_segmentation", "ROIs_segmentation")
    eNode.addDoubleLink("pipelineIntra.white_mesh", "white_mesh")
    eNode.addDoubleLink("pipelineIntra.smoothing", "smoothing")

    ###########################################################################
    #        link of parameters for the Constellation Group Pipeline          #
    ###########################################################################

    eNode.addChild(
        "pipelineInter", ProcessExecutionNode("constel_group_pipeline",
                                              optional=1))

    eNode.pipelineInter.removeLink("ROI", "ROIs_nomenclature")
    eNode.pipelineInter.removeLink("average_mesh", "ROIs_nomenclature")

    eNode.addDoubleLink("pipelineInter.method", "method")
    eNode.addDoubleLink("pipelineInter.ROIs_nomenclature", "ROIs_nomenclature")
    eNode.addDoubleLink("pipelineInter.ROI", "ROI")
    eNode.addDoubleLink("pipelineInter.study_name", "study_name")
    eNode.addDoubleLink("pipelineInter.new_study_name", "new_study_name")
    eNode.addDoubleLink("pipelineInter.smoothing", "smoothing")
    eNode.addDoubleLink("pipelineInter.subjects_group", "subjects_group")
    #eNode.addDoubleLink("pipelineInter.ROIs_segmentation", "ROIs_segmentation")
    eNode.addDoubleLink("pipelineInter.average_mesh", "average_mesh")

    self.setExecutionNode(eNode)
