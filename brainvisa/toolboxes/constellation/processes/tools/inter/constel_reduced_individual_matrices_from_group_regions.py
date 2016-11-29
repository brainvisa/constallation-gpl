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
*defines a Brainvisa process
    - the parameters of a process (Signature),
    - the parameters initialization
    - the linked parameters
*

Main dependencies:

Author: Sandrine Lefranc, 2015
"""


#----------------------------Imports-------------------------------------------


# Axon python API module
from brainvisa.processes import Signature, ValidationError, ReadDiskItem, \
    WriteDiskItem, String, ListOf, ParallelExecutionNode, ExecutionNode, \
    mapValuesToChildrenParameters, Boolean
from brainvisa.group_utils import Subject

# Soma-base modules
from soma.path import find_in_path
from soma.minf.api import registerClass, readMinf
from soma.functiontools import partial


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constelConnectionDensityTexture"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


#----------------------------Header--------------------------------------------


name = "Reduced Individual Matrices From Group Regions"
userLevel = 2

signature = Signature(
    # --inputs--
    "filtered_reduced_group_profile", ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "yes",
                            "roi_filtered": "yes",
                            "intersubject": "yes",
                            "step_time": "no",
                            "individual": "no"}),
    "subjects_group", ReadDiskItem("Group definition", "XML"),
    "study_name", String(),
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "cortical_region", String(),
    "complete_individual_matrices", ListOf(ReadDiskItem(
        "Connectivity Matrix", "Sparse Matrix",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "no",
                            "intersubject": "no"})),
    "average_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes",
                            "averaged": "Yes"}),
    "cortical_parcellation", ListOf(ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"})),

    # --outputs--
    "intersubject_reduced_matrices", ListOf(WriteDiskItem(
        "Connectivity Matrix", "Aims matrix formats",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "yes",
                            "intersubject": "yes"})),
    "normalize", Boolean(),
)


#----------------------------Functions-----------------------------------------


def afterChildAddedCallback(self, parent, key, child):
    """
    """
    # Set default values
    child.removeLink(
        "filtered_reduced_individual_profile", "complete_individual_matrix")
    child.removeLink(
        "reduced_individual_matrix", "filtered_reduced_individual_profile")
    child.removeLink("cortical_region", "complete_individual_matrix")
    child.signature["filtered_reduced_individual_profile"] = parent.signature[
        "filtered_reduced_group_profile"]
    child.signature["white_mesh"] = parent.signature["average_mesh"]
    child.signature["reduced_individual_matrix"] = parent.signature[
        "intersubject_reduced_matrices"].contentType

    child.filtered_reduced_individual_profile = \
        parent.filtered_reduced_group_profile
    child.white_mesh = parent.average_mesh
    child.cortical_regions_nomenclature = parent.cortical_regions_nomenclature
    child.cortical_region = parent.cortical_region
    child.normalize = parent.normalize

    # Add link between eNode.ListOf_Input_3dImage and pNode.Input_3dImage
    parent.addDoubleLink(key + ".filtered_reduced_individual_profile",
                         "filtered_reduced_group_profile")
    parent.addDoubleLink(key + ".white_mesh", "average_mesh")
    parent.addDoubleLink(key + ".cortical_regions_nomenclature",
                         "cortical_regions_nomenclature")
    parent.addDoubleLink(key + ".cortical_region", "cortical_region")
    parent.addDoubleLink(key + ".normalize", "normalize")


def beforeChildRemovedCallback(self, parent, key, child):
    parent.removeDoubleLink(key + ".filtered_reduced_individual_profile",
                            "filtered_reduced_group_profile")
    parent.removeDoubleLink(key + ".white_mesh", "average_mesh")
    parent.removeDoubleLink(key + ".cortical_regions_nomenclature",
                            "cortical_regions_nomenclature")
    parent.removeDoubleLink(key + ".cortical_region", "cortical_region")
    parent.removeDoubleLink(key + ".normalize", "normalize")


def initialization(self):
    """Provides default values and link of parameters.
    """

    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_watershed(self, dummy):
        """Function of link between the filtered watershed and the
        complete matrices.
        """
        if self.filtered_reduced_group_profile and self.subjects_group \
                and self.study_name:
            registerClass("minf_2.0", Subject, "Subject")
            groupOfSubjects = readMinf(self.subjects_group.fullPath())
            matrices = []
            for subject in groupOfSubjects:
                atts = dict()
                atts["_database"] = self.filtered_reduced_group_profile.get(
                    "_database")
                atts["center"] = self.filtered_reduced_group_profile.get(
                    "center")
                atts["studyname"] = self.study_name
                atts["method"] = self.filtered_reduced_group_profile.get(
                    "method")
                atts["gyrus"] = self.filtered_reduced_group_profile.get(
                    "gyrus")
                atts["smoothing"] = self.filtered_reduced_group_profile.get(
                    "smoothing")
                atts["ends_labelled"] = "all",
                atts["reduced"] = "no",
                atts["intersubject"] = "no"
                matrix = self.signature[
                    "complete_individual_matrices"].contentType.findValue(
                    atts, subject.attributes())
                if matrix is not None:
                    matrices.append(matrix)
            return matrices

    def link_matrices(self, dummy):
        """Function of link between the complete matrices and
        the reduced matrices.
        """
        if self.subjects_group and self.complete_individual_matrices and \
                self.filtered_reduced_group_profile:
            matrices = []
            for matrix in self.complete_individual_matrices:
                atts = dict(matrix.hierarchyAttributes())
                atts["group_of_subjects"] = \
                    self.filtered_reduced_group_profile.get(
                        "group_of_subjects")
                atts["studyname"] = self.filtered_reduced_group_profile.get(
                    "studyname")
                atts["tracking_session"] = None
                atts["acquisition"] = None
                atts["analysis"] = None
                matrix = self.signature[
                    "intersubject_reduced_matrices"].contentType.findValue(
                    atts)
                if matrix is not None:
                    matrices.append(matrix)
            return matrices

    def link_label(self, dummy):
        """
        """
        if self.filtered_reduced_group_profile is not None:
            s = str(self.filtered_reduced_group_profile.get("gyrus"))
            return s

    # link of parameters for autocompletion
    self.linkParameters(
        "cortical_region", "filtered_reduced_group_profile", link_label)
    self.linkParameters(
        "complete_individual_matrices",
        ("filtered_reduced_group_profile", "subjects_group", "study_name"),
        link_watershed)
    self.linkParameters(
        "intersubject_reduced_matrices",
        ("complete_individual_matrices", "subjects_group",
         "filtered_reduced_group_profile"), link_matrices)

    # define the main node of the pipeline
    eNode = ParallelExecutionNode(
        "Reduced_connectivity_matrix", parameterized=self,
        possibleChildrenProcesses=["constel_individual_reduced_matrix"],
        notify=True)
    self.setExecutionNode(eNode)

    # Add callback to warn about child add and remove
    eNode.afterChildAdded.add(
        ExecutionNode.MethodCallbackProxy(self.afterChildAddedCallback))
    eNode.beforeChildRemoved.add(
        ExecutionNode.MethodCallbackProxy(self.beforeChildRemovedCallback))

    # Add links to refresh child nodes when main lists are modified
    eNode.addLink(
        None, "complete_individual_matrices",
        partial(mapValuesToChildrenParameters, eNode,
                eNode, "complete_individual_matrix",
                "complete_individual_matrices",
                defaultProcess="constel_individual_reduced_matrix",
                name="constel_individual_reduced_matrix"))

    eNode.addLink(
        None, "intersubject_reduced_matrices",
        partial(mapValuesToChildrenParameters, eNode,
                eNode, "reduced_individual_matrix",
                "intersubject_reduced_matrices",
                defaultProcess="constel_individual_reduced_matrix",
                name="constel_individual_reduced_matrix"))

    eNode.addLink(
        None, "cortical_parcellation",
        partial(mapValuesToChildrenParameters, eNode,
                eNode, "cortical_parcellation",
                "cortical_parcellation",
                defaultProcess="constel_individual_reduced_matrix",
                name="constel_individual_reduced_matrix"))
