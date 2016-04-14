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
* defines a BrainVisa pipeline
    - the parameters of a pipeline (Signature),
    - the parameters initialization...
* iterative version (it is necessary if we are to iterate on all gyri at the
  same time as subjects)

Main dependencies:

Author: Sandrine Lefranc, 2016
"""

#----------------------------Imports-------------------------------------------


# Axon python API modules
from brainvisa.processes import Signature, String, Choice, ReadDiskItem, \
    Float, OpenChoice, neuroHierarchy, ListOf, ParallelExecutionNode, \
    mapValuesToChildrenParameters, ExecutionNode

# soma module
from soma.functiontools import partial


# constel module
try:
    from constel.lib.utils.files import read_file
except:
    pass


#----------------------------Header--------------------------------------------


name = "Constellation Individual Pipeline - Iterative Version"
userLevel = 0

signature = Signature(
    #inputs
    "study_name", String(),
    "outputs_database", Choice(),
    "format_fiber_tracts", Choice("bundles", "trk"),
    "method", Choice(
        ("averaged approach", "avg"), ("concatenated approach", "concat")),
    "ROIs_nomenclature", ReadDiskItem("Nomenclature ROIs File", "Text File"),
    "ROI", OpenChoice(),
    "dirsubject", ListOf(ReadDiskItem("subject", "directory")),
    "ROIs_segmentation", ListOf(ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"})),
    "white_mesh", ListOf(ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes",
                            "inflated": "No"})),
    "smoothing", Float(),
)


#----------------------------Functions-----------------------------------------


def afterChildAddedCallback(self, parent, key, child):
    """
    """
    # remove link of the sub process
    child.removeLink("ROI", "ROIs_nomenclature")

    # Set default values
    child.study_name = parent.study_name
    child.outputs_database = parent.outputs_database
    child.format_fiber_tracts = parent.format_fiber_tracts
    child.method = parent.method
    child.ROIs_nomenclature = parent.ROIs_nomenclature
    child.ROI = parent.ROI
    child.smoothing = parent.smoothing

    # Add link between eNode.ListOf_Input_3dImage and pNode.Input_3dImage
    parent.addDoubleLink(key + ".study_name", "study_name")
    parent.addDoubleLink(key + ".outputs_database", "outputs_database")
    parent.addDoubleLink(key + ".format_fiber_tracts", "format_fiber_tracts")
    parent.addDoubleLink(key + ".method", "method")
    parent.addDoubleLink(key + ".ROIs_nomenclature", "ROIs_nomenclature")
    parent.addDoubleLink(key + ".ROI", "ROI")
    parent.addDoubleLink(key + ".smoothing", "smoothing")


def beforeChildRemovedCallback(self, parent, key, child):
    parent.removeDoubleLink(key + ".study_name", "study_name")
    parent.removeDoubleLink(key + ".outputs_database", "outputs_database")
    parent.removeDoubleLink(
        key + ".format_fiber_tracts", "format_fiber_tracts")
    parent.removeDoubleLink(key + ".method", "method")
    parent.removeDoubleLink(key + ".ROIs_nomenclature", "ROIs_nomenclature")
    parent.removeDoubleLink(key + ".ROI", "ROI")
    parent.removeDoubleLink(key + ".smoothing", "smoothing")


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

   # define the main node of the pipeline
    eNode = ParallelExecutionNode(
        "Pipeline_iterative_version", parameterized=self,
        possibleChildrenProcesses=["constel_individual_pipeline"],
        notify=True)
    self.setExecutionNode(eNode)

    # Add callback to warn about child add and remove
    eNode.afterChildAdded.add(
        ExecutionNode.MethodCallbackProxy(self.afterChildAddedCallback))
    eNode.beforeChildRemoved.add(
        ExecutionNode.MethodCallbackProxy(self.beforeChildRemovedCallback))

    # Add links to refresh child nodes when main lists are modified
    eNode.addLink(
        None, "dirsubject",
        partial(mapValuesToChildrenParameters, eNode,
                eNode, "dirsubject",
                "dirsubject",
                defaultProcess="constel_individual_pipeline",
                name="constel_individual_pipeline"))

    eNode.addLink(
        None, "white_mesh",
        partial(mapValuesToChildrenParameters, eNode,
                eNode, "white_mesh",
                "white_mesh",
                defaultProcess="constel_individual_pipeline",
                name="constel_individual_pipeline"))

    eNode.addLink(
        None, "ROIs_segmentation",
        partial(mapValuesToChildrenParameters, eNode,
                eNode, "ROIs_segmentation",
                "ROIs_segmentation",
                defaultProcess="constel_individual_pipeline",
                name="constel_individual_pipeline"))
