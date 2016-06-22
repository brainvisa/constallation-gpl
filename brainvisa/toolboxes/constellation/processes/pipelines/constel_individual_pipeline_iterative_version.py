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
    - the signature of the inputs/ouputs,
    - the interlinkages between inputs/outputs.
* iterative version (it is necessary if we are to iterate on all gyri at the
  same time as subjects)

Main dependencies: axon python API, soma, constel

Author: Sandrine Lefranc, 2016
"""

#----------------------------Imports-------------------------------------------


# Axon python API modules
from brainvisa.processes import Signature, Choice, ReadDiskItem, Float, \
    OpenChoice, neuroHierarchy, ListOf, ParallelExecutionNode, \
    mapValuesToChildrenParameters, ExecutionNode

# soma module
from soma.functiontools import partial


# constel module
try:
    from constel.lib.utils.filetools import read_file
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
    "fiber_tracts_format", Choice("bundles", "trk"),
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "cortical_region", OpenChoice(),
    "subject_directory", ListOf(ReadDiskItem("subject", "directory")),
    "cortical_parcellation", ListOf(ReadDiskItem(
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
    child.removeLink("white_mesh", "subject_directory")
    child.removeLink("cortical_parcellation",
                     ["study_name", "subject_directory", "method"])

    # Set default values
    child.study_name = parent.study_name
    child.outputs_database = parent.outputs_database
    child.fiber_tracts_format = parent.fiber_tracts_format
    child.method = parent.method
    child.cortical_regions_nomenclature = parent.cortical_regions_nomenclature
    child.cortical_region = parent.cortical_region
    child.smoothing = parent.smoothing

    # Add link between eNode.ListOf_Input_3dImage and pNode.Input_3dImage
    parent.addDoubleLink(key + ".study_name", "study_name")
    parent.addDoubleLink(key + ".outputs_database", "outputs_database")
    parent.addDoubleLink(key + ".fiber_tracts_format", "fiber_tracts_format")
    parent.addDoubleLink(key + ".method", "method")
    parent.addDoubleLink(key + ".cortical_regions_nomenclature",
                         "cortical_regions_nomenclature")
    parent.addDoubleLink(key + ".cortical_region", "cortical_region")
    parent.addDoubleLink(key + ".smoothing", "smoothing")


def beforeChildRemovedCallback(self, parent, key, child):
    parent.removeDoubleLink(key + ".study_name", "study_name")
    parent.removeDoubleLink(key + ".outputs_database", "outputs_database")
    parent.removeDoubleLink(key + ".fiber_tracts_format",
                            "fiber_tracts_format")
    parent.removeDoubleLink(key + ".method", "method")
    parent.removeDoubleLink(key + ".cortical_regions_nomenclature",
                            "cortical_regions_nomenclature")
    parent.removeDoubleLink(key + ".cortical_region", "cortical_region")
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
    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def fill_study_choice(self, dummy=None):
        """
        """
        choices = set()
        if self.outputs_database is not None:
            database = neuroHierarchy.databases.database(self.outputs_database)
            sel = {"study": self.method}
            choices.update(
                [x[0] for x in database.findAttributes(
                    ['texture'], selection=sel,
                    _type='Filtered Fascicles Bundles')])
        self.signature['study_name'].setChoices(*sorted(choices))
        if len(choices) != 0 and self.isDefault('study_name') \
                and self.study_name not in choices:
            self.setValue('study_name', list(choices)[0], True)

    def reset_cortical_region(self, dummy):
        """ This callback reads the cortical regions nomenclature and proposes
        them in the signature 'cortical_region' of process.
        It also resets the cortical_region paramter to default state after
        the nomenclature changes.
        """
        current = self.cortical_region
        self.setValue('cortical_region', current, True)
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
                self.setValue('cortical_region', s[0][1], True)
            else:
                self.setValue('cortical_region', current, True)

    def method_changed(self, dummy):
        """
        """
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
        signature["cortical_parcellation"] = ListOf(item_type)
        self.changeSignature(signature)
        self.setValue(
            "cortical_parcellation", link_cortical_region(self), True)
        fill_study_choice(self)

    def link_cortical_region(self, dummy=None):
        """
        """
        if self.method == "avg" and self.study_name:
            # just in case study_name corresponds to subjects group...
            res = self.signature["cortical_parcellation"].findValue(
                {"freesurfer_group_of_subjects": self.study_name})
            if res is None:
                res = self.signature["cortical_parcellation"].findValue(
                    {"group_of_subjects": self.study_name})
            if res is not None:
                return [res] * len(self.executionNode().childrenNames())
        elif self.method == "concat" and self.subject_directory is not None:
            item_type = self.signature["cortical_parcellation"].contentType
            res = [item_type.findValue(subject_directory)
                   for subject_directory in self.subject_directory]
            if res == [None] * len(self.subject_directory):
                res = [item_type.findValue(subject_directory,
                       requiredAttributes={"_type": "BothResampledGyri"})
                       for subject_directory in self.subject_directory]
            return res

    # link of parameters for autocompletion
    self.linkParameters(None, "cortical_regions_nomenclature",
                        reset_cortical_region)
    self.linkParameters(None, "method", method_changed)
    self.linkParameters("white_mesh", "subject_directory")
    self.linkParameters(None, "outputs_database", fill_study_choice)
    self.linkParameters("cortical_parcellation",
                        ["study_name", "subject_directory", "method"],
                        link_cortical_region)

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
        None, "subject_directory",
        partial(mapValuesToChildrenParameters, eNode,
                eNode, "subject_directory",
                "subject_directory",
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
        None, "cortical_parcellation",
        partial(mapValuesToChildrenParameters, eNode,
                eNode, "cortical_parcellation",
                "cortical_parcellation",
                defaultProcess="constel_individual_pipeline",
                name="constel_individual_pipeline"))

    fill_study_choice(self)
    if len(self.signature['study_name'].values) != 0:
        self.study_name = self.signature['study_name'].values[0][0]
