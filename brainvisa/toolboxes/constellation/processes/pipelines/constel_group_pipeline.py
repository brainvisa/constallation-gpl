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
from brainvisa.processes import String
from brainvisa.processes import Choice
from brainvisa.processes import ListOf
from brainvisa.group_utils import Subject
from brainvisa.processes import Signature
from brainvisa.processes import OpenChoice
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import neuroHierarchy
from brainvisa.configuration import neuroConfig
from brainvisa.processes import ValidationError
from brainvisa.processes import SerialExecutionNode
from brainvisa.processes import ProcessExecutionNode


# Soma module
from soma.minf.api import registerClass, readMinf

# Package import
try:
    from constel.lib.utils.filetools import read_file
except:
    raise ValidationError("Please make sure that constel module is installed.")


# ---------------------------Header--------------------------------------------


name = "Constellation Group Pipeline"
userLevel = 1

if neuroConfig.gui:
    import types
    from soma.qt_gui.qt_backend import QtGui, QtCore
    from brainvisa.data.qt4gui.readdiskitemGUI import DiskItemEditor
    from brainvisa.processing.qt4gui.neuroProcessesGUI import showProcess
    from soma.wip.application.api import findIconFile
    from brainvisa.data.qtgui.neuroDataGUI import buttonIconSize, buttonMargin

    class GroupCreatorEditor(DiskItemEditor):
        def __init__(self, parameter, parent, name,
                     write=False, context=None):
            super(GroupCreatorEditor, self).__init__(parameter, parent, name,
                                                     write, context)
            if not hasattr(GroupCreatorEditor, "new_icon"):
                GroupCreatorEditor.new_icon \
                    = QtGui.QIcon(findIconFile("folder_new.png"))
            create_btn = QtGui.QPushButton()
            create_btn.setIcon(GroupCreatorEditor.new_icon)
            create_btn.setIconSize(buttonIconSize)
            create_btn.setToolTip(_t_("Create new group"))
            create_btn.setFixedSize(buttonIconSize + buttonMargin)
            create_btn.setFocusPolicy(QtCore.Qt.NoFocus)
            self.layout().addWidget(create_btn)
            create_btn.clicked.connect(self.create_group)

        def create_group(self):
            showProcess("createGroup")


signature = Signature(
    "regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "region", OpenChoice(),
    "study_name", OpenChoice(),
    "method", Choice(
        ("averaged approach", "avg"),
        ("concatenated approach", "concat")),
    "new_study_name", String(),
    "smoothing", Float(),
    "constellation_subjects_group", ReadDiskItem(
        "Group definition", "XML", exactType=True),
    "mean_individual_profiles", ListOf(
        ReadDiskItem("Connectivity Profile Texture", "Aims texture formats",
                     requiredAttributes={"ends_labelled": "all",
                                         "normed": "no",
                                         "intersubject": "no"})),
    "normed_individual_profiles", ListOf(
        ReadDiskItem("Connectivity Profile Texture", "Aims texture formats",
                     requiredAttributes={"ends_labelled": "all",
                                         "normed": "yes",
                                         "intersubject": "no"})),
    "average_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes",
                            "averaged": "Yes"}),
    "regions_parcellation", ListOf(
        ReadDiskItem("ROI Texture", "Aims texture formats",
                     requiredAttributes={"side": "both",
                                         "vertex_corr": "Yes"})),
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
    self.addLink(None, "constellation_subjects_group", self.linkGroup)

    # default value
    self.smoothing = 3.0
    self.regions_nomenclature = self.signature[
        "regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    # optional value
    self.setOptional("new_study_name")

    if neuroConfig.gui:
        self.signature[
            "constellation_subjects_group"].editor = types.MethodType(
            lambda self, parent, name, context:
            GroupCreatorEditor(self, parent, name,
                               context=context,
                               write=self._write),
            self.signature["constellation_subjects_group"])

    def fill_study_choice(self, dummy=None):
        """
        """
        databases = [h.name for h in neuroHierarchy.hierarchies()
                     if h.fso.name == "brainvisa-3.2.0"]
        choices = set()
        for db_name in databases:
            database = neuroHierarchy.databases.database(db_name)
            sel = {"method": self.method}
            choices.update(
                [x[0] for x in database.findAttributes(
                    ["studyname"], selection=sel,
                    _type="Filtered Fascicles Bundles")])
        self.signature['study_name'].setChoices(*sorted(choices))
        if len(choices) != 0 and self.isDefault("study_name") \
                and self.study_name not in choices:
            self.setValue("study_name", list(choices)[0], True)

    def reset_label(self, dummy):
        """ This callback reads the ROIs nomenclature and proposes them in the
        signature 'region' of process.
        It also resets the region paramter to default state after
        the nomenclature changes.
        """
        current = self.region
        self.setValue('region', current, True)
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

    def method_changed(self, dummy):
        """
        """
        if self.method == "avg":
            pass
        else:
            pass
        fill_study_choice(self)

    def link_profiles(self, dummy):
        """Function of link to determine the connectivity profiles
        """
        if (self.constellation_subjects_group and self.region
                and self.method and self.smoothing and self.study_name):
            registerClass("minf_2.0", Subject, "Subject")
            groupOfSubjects \
                = readMinf(self.constellation_subjects_group.fullPath())
            profiles = []
            for subject in groupOfSubjects:
                atts = {}
                atts["method"] = self.method
                atts["gyrus"] = str(self.region)
                atts["smoothing"] = str(self.smoothing)
                atts["studyname"] = self.study_name
                atts["_database"] \
                    = self.constellation_subjects_group.get("_database")
                atts.update(subject.attributes())
                profile = self.signature[
                    "mean_individual_profiles"].contentType.findValue(atts)
                if profile is not None:
                    profiles.append(profile)
            return profiles

    def link_regions_parcellation(self, dummy):
        if self.average_mesh is None:
            return []
        roi_type = self.signature["regions_parcellation"].contentType
        if self.method == "avg":
            roi_seg = roi_type.findValue(self.average_mesh)
            if roi_seg is not None:
                return [roi_seg]
        else:
            group = ReadDiskItem("Group definition", "XML").findValue(
                self.average_mesh)
            if group:
                registerClass("minf_2.0", Subject, "Subject")
                groupOfSubjects = readMinf(group.fullPath())
                roi_seg = []
                rdi = signature["regions_parcellation"].contentType
                for subject in groupOfSubjects:
                    req = {"averaged": "No", "subject": subject.subject}
                    req.update(rdi.requiredAttributes)
                    items = list(rdi.findValues({}, req, False))
                    if len(items) == 1:
                        roi_seg.append(items[0])
                    elif len(items) > 1:
                        # ambiguous. Find FS gyri (arbitrarily)
                        prio = [item for item in items
                                if ".aparc.annot." in item.fullPath()]
                        if prio:
                            roi_seg.append(prio[0])
                        else:
                            roi_seg.append(items[0])
                return roi_seg
        return []

    def link_mesh(self, dummy):
        """
        """
        mesh_type = self.signature["average_mesh"]
        mesh = None
        if mesh is None and self.constellation_subjects_group is not None:
            mesh = mesh_type.findValue(self.constellation_subjects_group)
            if mesh is None:
                atts = {
                    "freesurfer_group_of_subjects":
                    self.constellation_subjects_group.get("group_of_subjects"),
                    "group_of_subjects":
                    self.constellation_subjects_group.get("group_of_subjects")
                    }
                mesh = mesh_type.findValue(atts)
        return mesh

    # link of parameters for autocompletion
    self.linkParameters(None, "regions_nomenclature", reset_label)
    self.linkParameters(None, "method", method_changed)
    self.linkParameters("mean_individual_profiles",
                        ("method", "region", "smoothing",
                         "study_name", "constellation_subjects_group"),
                        link_profiles)
    self.linkParameters("normed_individual_profiles",
                        "mean_individual_profiles")
    self.linkParameters("average_mesh", "constellation_subjects_group",
                        link_mesh)
    self.linkParameters("regions_parcellation",
                        ["average_mesh", "method"],
                        link_regions_parcellation)

    # visibility level for the user
    self.signature["mean_individual_profiles"].userLevel = 2
    self.signature["normed_individual_profiles"].userLevel = 2

    # define the main node of a pipeline
    eNode = SerialExecutionNode(self.name, parameterized=self)

    ###########################################################################
    #        link of parameters for the "Creation of a mask" process          #
    ###########################################################################

    eNode.addChild("CreateMask",
                   ProcessExecutionNode(
                       "constel_group_mask",
                       optional=1))

    eNode.addDoubleLink("CreateMask.subjects_group",
                        "constellation_subjects_group")
    eNode.addDoubleLink("CreateMask.new_study_name", "new_study_name")
    eNode.addDoubleLink("CreateMask.mean_individual_profiles",
                        "mean_individual_profiles")

    ###########################################################################
    #   link of parameters for the "Connectivity Profile of Group" process    #
    ###########################################################################

    eNode.addChild("GroupConnectivityProfile",
                   ProcessExecutionNode(
                       "constel_group_profile",
                       optional=1))

    eNode.addDoubleLink(
        "GroupConnectivityProfile.subjects_group",
        "constellation_subjects_group")
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

    eNode.addDoubleLink("ReducedGroupMatrix.subjects_group",
                        "constellation_subjects_group")
    eNode.addDoubleLink("ReducedGroupMatrix.study_name",
                        "study_name")
    eNode.addDoubleLink("ReducedGroupMatrix.average_mesh", "average_mesh")
    eNode.addDoubleLink("ReducedGroupMatrix.regions_parcellation",
                        "regions_parcellation")
    eNode.addDoubleLink("ReducedGroupMatrix.filtered_reduced_group_profile",
                        "GroupRegionsFiltering.filtered_reduced_group_profile")

    ###########################################################################
    #        link of parameters for the "Clustering of Group" process         #
    ###########################################################################

    eNode.addChild("GroupClustering",
                   ProcessExecutionNode("constel_group_clustering",
                                        optional=1))

    eNode.addDoubleLink("GroupClustering.subjects_group",
                        "constellation_subjects_group")
    eNode.addDoubleLink("GroupClustering.method", "method")
    eNode.addDoubleLink("GroupClustering.average_mesh", "average_mesh")
    eNode.addDoubleLink("GroupClustering.regions_parcellation",
                        "regions_parcellation")
    eNode.addDoubleLink("GroupClustering.intersubject_reduced_matrices",
                        "ReducedGroupMatrix.intersubject_reduced_matrices")

    self.setExecutionNode(eNode)

    fill_study_choice(self)
    if len(self.signature["study_name"].values) != 0:
        self.study_name = self.signature["study_name"].values[0][0]
    self.constellation_subjects_group = self.signature[
        "constellation_subjects_group"].findValue({})
