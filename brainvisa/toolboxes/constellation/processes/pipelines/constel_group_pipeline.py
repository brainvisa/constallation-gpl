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
from brainvisa.processes import Signature, Choice, ReadDiskItem, OpenChoice, \
    String, Float, ListOf, SerialExecutionNode, ProcessExecutionNode
from soma.minf.api import registerClass, readMinf
from brainvisa.group_utils import Subject

# Plot constel module
try:
    import constel
    from constel.lib.utils.files import read_file
except:
    raise ValidationError("Please make sure that constel module is installed.")


#----------------------------Header--------------------------------------------


name = "Constellation Group Pipeline"
userLevel = 0


signature = Signature(
    "method", Choice(
        ("averaged approach", "avg"), ("concatenated approach", "concat")),
    "ROIs_nomenclature", ReadDiskItem("Nomenclature ROIs File", "Text File"),
    "ROI", OpenChoice(),
    "study_name", String(),
    "new_study_name", String(),
    "smoothing", Float(),
    "subjects_group", ReadDiskItem("Group definition", "XML", exactType=True),
    "mean_individual_profiles", ListOf(
        ReadDiskItem("Connectivity Profile Texture", "Aims texture formats",
                     requiredAttributes={"normed": "No",
                                         "thresholded": "No",
                                         "averaged": "No",
                                         "intersubject": "No"})),
    "normed_individual_profiles", ListOf(
        ReadDiskItem("Connectivity Profile Texture", "Aims texture formats",
                     requiredAttributes={"normed": "Yes",
                                         "thresholded": "Yes",
                                         "averaged": "No",
                                         "intersubject": "No"})),
    "ROIs_segmentation", ListOf(
        ReadDiskItem("ROI Texture", "Aims texture formats",
                     requiredAttributes={"side": "both",
                                         "vertex_corr": "Yes"})),
    "average_mesh", ReadDiskItem("White Mesh", "Aims mesh formats",
                                 requiredAttributes={"side": "both",
                                                     "vertex_corr": "Yes",
                                                     "averaged": "Yes"}),
)


def linkGroup(self, param1):
    self.smoothing = 3.0

    eNode = self.executionNode()
    for node in eNode.children():
        if node.name() == "Parallel Node":
            node.addChild(
                "N%d" % len(list(node.children())), ProcessExecutionNode(
                    "constel_reduced_individual_matrices_from_group_regions",
                    optional=1))


def initialization(self):
    """Provides default values and link of parameters
    """
    self.addLink(None, "subjects_group", self.linkGroup)

    # default value
    self.smoothing = 3.0
    self.ROIs_nomenclature = self.signature["ROIs_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    # optional value
    self.setOptional("new_study_name")

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

    def link_profiles(self, dummy):
        """Function of link to determine the connectivity profiles
        """
        if self.subjects_group and self.method and self.ROI \
                and self.smoothing and self.study_name:
            registerClass("minf_2.0", Subject, "Subject")
            groupOfSubjects = readMinf(self.subjects_group.fullPath())
            profiles = []
            for subject in groupOfSubjects:
                atts = {}
                atts["study"] = self.method
                atts["gyrus"] = str(self.ROI)
                atts["smoothing"] = str(self.smoothing)
                atts["texture"] = self.study_name
                atts["_database"] = self.subjects_group.get("_database")
                atts.update(subject.attributes())
                profile = self.signature[
                    'mean_individual_profiles'].contentType.findValue(
                        atts) #, subject.attributes())
                if profile is not None:
                    profiles.append(profile)
            return profiles

    def linkMesh(self, dummy):
        if self.ROIs_segmentation:
            return self.signature["average_mesh"].findValue(
                self.ROIs_segmentation[0])

    def linkROIsegmentation(self, dummy):
        if self.method == "avg":
            if self.subjects_group is not None:
                atts = {
                    "freesurfer_group_of_subjects":
                        self.subjects_group.get("group_of_subjects"),
                    "group_of_subjects":
                        self.subjects_group.get("group_of_subjects"),
                }
                roi_seg = self.signature[
                    "ROIs_segmentation"].contentType.findValue(
                        atts, requiredAttributes={"averaged": "Yes"})
                if roi_seg:
                    return [roi_seg]
        else:
            if self.subjects_group:
                registerClass("minf_2.0", Subject, "Subject")
                groupOfSubjects = readMinf(self.subjects_group.fullPath())
                roi_seg = []
                rdi = signature["ROIs_segmentation"].contentType
                for subject in groupOfSubjects:
                    req = {"averaged": "No", "subject": subject.subject}
                    req.update(rdi.requiredAttributes)
                    items = list(rdi.findValues({}, req, False))
                    if len(items) == 1:
                        roi_seg.append(items[0])
                    elif len(items) > 1:
                        # ambiguous. Find FS gyri (arbitrarily)
                        prio = [item for item in items
                                if '.aparc.annot.' in item.fullPath()]
                        if prio:
                            roi_seg.append(prio[0])
                        else:
                            roi_seg.append(items[0])
                return roi_seg

    # link of parameters
    self.linkParameters(
        "mean_individual_profiles",
        ("method", "ROI", "smoothing", "study_name",
         "subjects_group"), link_profiles)
    self.linkParameters(
        "normed_individual_profiles", "mean_individual_profiles")
    self.linkParameters("ROIs_segmentation", ["subjects_group", "method"],
                        linkROIsegmentation)
    self.linkParameters("average_mesh", "ROIs_segmentation", linkMesh)

    # visibility level for the user
    self.signature["mean_individual_profiles"].userLevel = 3
    self.signature["normed_individual_profiles"].userLevel = 3

    # define the main node of a pipeline
    eNode = SerialExecutionNode(self.name, parameterized=self)

    ###########################################################################
    #        link of parameters for the "Creation of a mask" process          #
    ###########################################################################

    eNode.addChild("CreateMask",
                   ProcessExecutionNode(
                       "constel_group_mask",
                       optional=1))

    eNode.addDoubleLink("CreateMask.subjects_group", "subjects_group")
    eNode.addDoubleLink("CreateMask.new_study_name", "new_study_name")
    eNode.addDoubleLink(
        "CreateMask.mean_individual_profiles", "mean_individual_profiles")

    ###########################################################################
    #   link of parameters for the "Connectivity Profile of Group" process    #
    ###########################################################################

    eNode.addChild("GroupConnectivityProfile",
                   ProcessExecutionNode(
                       "constel_group_profile",
                       optional=1))

    eNode.addDoubleLink(
        "GroupConnectivityProfile.subjects_group", "subjects_group")
    eNode.addDoubleLink(
        "GroupConnectivityProfile.new_study_name", "new_study_name")
    eNode.addDoubleLink(
        "GroupConnectivityProfile.normed_individual_profiles",
        "normed_individual_profiles")

    ###########################################################################
    #link of parameters for the "Normed Connectivity Profile of Group" process#
    ###########################################################################

    eNode.addChild("NormedGroupProfile",
                   ProcessExecutionNode(
                       "constel_group_mask_normalize_profile",
                       optional=1))

    eNode.addDoubleLink(
        "NormedGroupProfile.group_mask", "CreateMask.group_mask")

    ###########################################################################
    #        link of parameters for the "Watershed of Group" process          #
    ###########################################################################

    eNode.addChild("GroupRegionsFiltering",
                   ProcessExecutionNode("constel_group_regions_filtering",
                                        optional=1))

    eNode.addDoubleLink("GroupRegionsFiltering.average_mesh", "average_mesh")
    eNode.addDoubleLink("GroupRegionsFiltering.normed_group_profile",
                        "NormedGroupProfile.normed_group_profile")

    ###########################################################################
    #    link of parameters for the "Reduced Connectivity Matrix" process     #
    ###########################################################################

    eNode.addChild(
        "ReducedGroupMatrix",
        ProcessExecutionNode(
            "constel_reduced_individual_matrices_from_group_regions",
            optional=1))

    eNode.addDoubleLink("ReducedGroupMatrix.subjects_group", "subjects_group")
    eNode.addDoubleLink("ReducedGroupMatrix.study_name",
                        "study_name")
    eNode.addDoubleLink("ReducedGroupMatrix.average_mesh", "average_mesh")
    eNode.addDoubleLink(
        "ReducedGroupMatrix.ROIs_segmentation", "ROIs_segmentation")
    eNode.addDoubleLink("ReducedGroupMatrix.filtered_reduced_group_profile",
                        "GroupRegionsFiltering.filtered_reduced_group_profile")

    ###########################################################################
    #        link of parameters for the "Clustering of Group" process         #
    ###########################################################################

    eNode.addChild("GroupClustering",
                   ProcessExecutionNode("constel_group_clustering",
                                        optional=1))

    eNode.addDoubleLink("GroupClustering.subjects_group", "subjects_group")
    eNode.addDoubleLink("GroupClustering.method", "method")
    eNode.addDoubleLink("GroupClustering.average_mesh", "average_mesh")
    eNode.addDoubleLink(
        "GroupClustering.ROIs_segmentation", "ROIs_segmentation")
    eNode.addDoubleLink("GroupClustering.intersubject_reduced_matrices",
                        "ReducedGroupMatrix.intersubject_reduced_matrices")

    self.setExecutionNode(eNode)
