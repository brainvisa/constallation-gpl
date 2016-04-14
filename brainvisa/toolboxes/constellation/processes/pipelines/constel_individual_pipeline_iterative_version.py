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
    "method", Choice(
        ("averaged approach", "avg"), ("concatenated approach", "concat")),
    "study_name", OpenChoice(),
    "outputs_database", Choice(),
    "format_fiber_tracts", Choice("bundles", "trk"),
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
    child.removeLink("white_mesh", "dirsubject")
    child.removeLink("ROIs_segmentation",
                     ["study_name", "dirsubject", "method"])

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

    def fill_study_choice(self, dummy=None):
        if self.outputs_database is not None:
            database = neuroHierarchy.databases.database(self.outputs_database)
            sel = {"study": self.method}
            self.signature['study_name'].setChoices(
                *sorted([x[0] for x in database.findAttributes(
                    ['texture'], selection=sel,
                    _type='Filtered Fascicles Bundles')]))
        else:
            self.signature['study_name'].setChoices()

    def reset_roi(self, dummy):
        """ This callback reads the ROIs nomenclature and proposes them in the
        signature 'ROI' of process.
        It also resets the ROI paramter to default state after
        the nomenclature changes.
        """
        current = self.ROI
        self.setValue('ROI', current, True)
        if self.ROIs_nomenclature is not None:
            s = [("Select a ROI in this list", None)]
            # temporarily set a value which will remain valid
            self.ROI = s[0][1]
            s += read_file(self.ROIs_nomenclature.fullPath(), mode=2)
            self.signature["ROI"].setChoices(*s)
            if isinstance(self.signature["ROI"], OpenChoice):
                self.signature["ROI"] = Choice(*s)
                self.changeSignature(self.signature)
            if current not in s:
                self.setValue('ROI', s[0][1], True)
            else:
                self.setValue('ROI', current, True)

    def method_changed(self, dummy):
        signature = self.signature
        if self.method == "avg":
            item_type = ReadDiskItem(
                "ROI Texture", "Aims texture formats",
                requiredAttributes={"side": "both", "vertex_corr": "Yes",
                                    "averaged": "Yes"})
        else:
            item_type = ReadDiskItem(
                "ROI Texture", "Aims texture formats",
                requiredAttributes={"side": "both", "vertex_corr": "Yes",
                                    "averaged": "No"})
        signature["ROIs_segmentation"] = ListOf(item_type)
        self.changeSignature(signature)
        self.setValue("ROIs_segmentation", link_roi(self), True)
        fill_study_choice(self)

    #def linkMesh(self, dummy):
        #item_type = self.signature["white_mesh"]
        #if self.method == "avg":
            #return [item_type.findValue(roi_seg)
                    #for roi_seg in self.ROIs_segmentation]
        #else:
            #return [item_type.findValue({"subject": dirsubject.get("subject")})
                    #for dirsubject in self.dirsubject]

    def link_roi(self, dummy=None):
        if self.method == "avg" and self.study_name:
            # just in case study_name corresponds to subjects group...
            res = self.signature["ROIs_segmentation"].findValue(
                {"freesurfer_group_of_subjects": self.study_name})
            if res is None:
                res = self.signature["ROIs_segmentation"].findValue(
                    {"group_of_subjects": self.study_name})
            if res is not None:
                return [res] * len(self.executionNode().childrenNames())
        elif self.method == "concat" and self.dirsubject is not None:
            item_type = self.signature["ROIs_segmentation"].contentType
            res = [item_type.findValue(dirsubject)
                   for dirsubject in self.dirsubject]
            if res == [None] * len(self.dirsubject):
                res = [item_type.findValue(dirsubject,
                          requiredAttributes={"_type": "BothResampledGyri"})
                       for dirsubject in self.dirsubject]
            return res

    # link of parameters for autocompletion
    self.linkParameters(None, "ROIs_nomenclature", reset_roi)
    self.linkParameters(None, "method", method_changed)
    self.linkParameters("white_mesh", "dirsubject")
    self.linkParameters(None, "outputs_database", fill_study_choice)
    self.linkParameters("ROIs_segmentation",
                        ["study_name", "dirsubject", "method"], link_roi)

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

    fill_study_choice(self)
    if len(self.signature['study_name'].values) != 0:
        self.study_name = self.signature['study_name'].values[0][0]
