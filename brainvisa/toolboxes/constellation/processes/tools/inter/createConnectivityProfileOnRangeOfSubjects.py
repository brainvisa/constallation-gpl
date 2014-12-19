############################################################################
#  This software and supporting documentation are distributed by
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
############################################################################

# Axon python API module
from brainvisa.processes import *
from brainvisa.group_utils import Subject

# Soma-base module
from soma.minf.api import registerClass, readMinf


# Plot aims module
def validation():
    try:
        from soma import aims
    except:
        raise ValidationError(
            "Please make sure that constel module is installed.")

name = "Connectivity Profile of Group"
userLevel = 2

# Argument declaration
signature = Signature(
    "study", Choice("avg", "concat"), # TODO: change name (averaged, concatenated)
    "texture_group", String(),
    "patch_label", Choice(
        ("left bankssts", 1), ("left caudal anterior cingulate", 2),
        ("left caudal middle frontal", 3), ("left corpus callosum", 4),
        ("left cuneus", 6), ("left entorhinal", 7),
        ("left fusiform", 8), ("left inferior parietal", 9),
        ("left inferior temporal", 10), ("left isthmus cingulate", 11),
        ("left lateral occipital", 12), ("left lateral orbitofrontal", 13),
        ("left lingual", 14), ("left medial orbitofrontal", 15),
        ("left middle temporal", 16), ("left parahippocampal", 17),
        ("left paracentral", 18), ("left pars opercularis", 19),
        ("left pars orbitalis", 20), ("left pars triangularis", 21),
        ("left pericalcarine", 22), ("left postcentral", 23),
        ("left posterior cingulate", 24), ("left precentral", 25),
        ("left precuneus", 26), ("left rostral anterior cingulate", 27),
        ("left rostral middle frontal", 28), ("left superior frontal", 29),
        ("left superior parietal", 30), ("left superior temporal", 31),
        ("left supramarginal", 32), ("left frontal pole", 33),
        ("left temporal pole", 34), ("left transverse temporal", 35),
        ("left insula", 36),
        ("right bankssts", 37), ("right caudal anterior cingulate", 38),
        ("rightcaudal middle frontal", 39), ("right corpus callosum", 40),
        ("right cuneus", 42), ("right entorhinal", 43),
        ("right fusiform", 44), ("right inferior parietal", 45),
        ("right inferior temporal", 46), ("right isthmus cingulate", 47),
        ("right lateral occipital", 48), ("right lateral orbitofrontal", 49),
        ("right lingual", 50), ("right medial orbitofrontal", 51),
        ("right middle temporal", 52), ("right parahippocampal", 53),
        ("right paracentral", 54), ("right pars opercularis", 55),
        ("right pars orbitalis", 56), ("right pars triangularis", 57),
        ("right pericalcarine", 58), ("right postcentral", 59),
        ("right posterior cingulate", 60), ("right precentral", 61),
        ("right precuneus", 62), ("right rostral anterior cingulate", 63),
        ("right rostral middle frontal", 64), ("right superior frontal", 65),
        ("right superior parietal", 66), ("right superior temporal", 67),
        ("right supramarginal", 68), ("right frontal pole", 69),
        ("right temporal pole", 70), ("right transverse temporal", 71),
        ("right insula", 72)),
    "smoothing", Float(),
    "group", ReadDiskItem("Group definition", "XML"),
    "normed_connectivity_profiles", ListOf(
        ReadDiskItem("Normed Connectivity Profile", "Aims texture formats")),
    "normed_connectivity_profile_nb", ListOf(
        WriteDiskItem("Group Normed Connectivity Profile",
                      "Aims texture formats")),
    "group_connectivity_profile", WriteDiskItem(
        "Avg Connectivity Profile", "Aims texture formats"),
)


# Default values
def initialization(self):
    self.texture_group = "fsgroup"
    self.smoothing = 3.0

    # function of link between individual profiles and normed profiles
    def linkIndividualProfiles(self, dummy):
        if self.group is not None:
            registerClass("minf_2.0", Subject, "Subject")
            groupOfSubjects = readMinf(self.group.fullPath())
            profiles = []
            for subject in groupOfSubjects:
                atts = dict(self.group.hierarchyAttributes())
                atts["study"] = self.study
                atts["texture"] = "fs" + os.path.basename(
                    os.path.dirname(self.group.fullPath()))
                atts["gyrus"] = "G" + str(self.patch_label)
                atts["smoothing"] = "smooth" + str(self.smoothing)
                profile = ReadDiskItem("Normed Connectivity Profile",
                                       "Aims texture formats").findValue(
                                           atts, subject.attributes())
                if profile is not None:
                    profiles.append(profile)
            return profiles

    # function of link
    def linkProfiles(self, dummy):
        if self.normed_connectivity_profiles and self.group is not None:
            registerClass("minf_2.0", Subject, "Subject")
            groupOfSubjects = readMinf(self.group.fullPath())
            profiles = []
            for subject in groupOfSubjects:
                atts = dict(self.group.hierarchyAttributes())
                atts["study"] = self.study
                atts["texture"] = self.texture_group
                atts["gyrus"] = "G" + str(self.patch_label)
                atts["smoothing"] = "smooth" + str(self.smoothing)
                profile = WriteDiskItem("Group Normed Connectivity Profile",
                                        "Aims texture formats").findValue(
                                            atts, subject.attributes())
                if profile is not None:
                    profiles.append(profile)
            return profiles

    # function of link
    def linkGroupProfiles(self, dummy):
        if self.group is not None:
            atts = dict(self.group.hierarchyAttributes())
            atts["study"] = self.study
            atts["texture"] = self.texture_group
            atts["gyrus"] = "G" + str(self.patch_label)
            atts["smoothing"] = "smooth" + str(self.smoothing)
            return self.signature["group_connectivity_profile"].findValue(atts)

    # link of parameters
    self.linkParameters("normed_connectivity_profiles", (
        "group", "study", "patch_label", "smoothing"), linkIndividualProfiles)
    self.linkParameters("normed_connectivity_profile_nb", (
        "group", "study", "patch_label", "smoothing"), linkProfiles)
    self.linkParameters("group_connectivity_profile",
                        "normed_connectivity_profile_nb", linkGroupProfiles)

    # visibility level
    self.signature["texture_group"].userLevel = 3
    self.signature["normed_connectivity_profiles"].userLevel = 2
    self.signature["normed_connectivity_profile_nb"].userLevel = 2


def execution(self, context):
    """ A connectivity profile is determinated on a range of subjects
    (for a group of subjects)
    """
    registerClass("minf_2.0", Subject, "Subject")
    groupOfSubjects = readMinf(self.group.fullPath())

    listOfTex = []
    for texture, outtexname in zip(self.normed_connectivity_profiles,
                                   self.normed_connectivity_profile_nb):
        tex = aims.read(texture.fullPath())
        tex_ar = tex[0].arraydata()
        dividende_coef = 0
        dividende_coef = tex_ar.sum()
        if dividende_coef > 0:
            z = 1./dividende_coef
            for i in xrange(tex[0].nItem()):
                value = tex[0][i]
                tex[0][i] = z*value
        listOfTex.append(outtexname)
        aims.write(tex, outtexname.fullPath())

    count = 0
    for tex_filename in listOfTex:
        if count == 0:
            context.write(tex_filename)
            context.write(self.group_connectivity_profile)
            shutil.copyfile(
                str(tex_filename), str(self.group_connectivity_profile))
        else:
            context.system("AimsLinearComb",
                           "-i", tex_filename,
                           "-j", self.group_connectivity_profile,
                           "-o", self.group_connectivity_profile)
        count += 1

    averageTexture = aims.read(self.group_connectivity_profile.fullPath())
    subjects_nb = len(groupOfSubjects)
    if subjects_nb == 0:
        raise exceptions.ValueError("subjects_list is empty")
    for i in xrange(averageTexture.nItem()):
        val = averageTexture[0][i]
        averageTexture[0][i] = val/subjects_nb
    aims.write(averageTexture, self.group_connectivity_profile.fullPath())