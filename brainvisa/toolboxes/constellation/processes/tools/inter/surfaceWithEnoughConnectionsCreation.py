############################################################################
# This software and supporting documentation are distributed by
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
############################################################################

# Axon python API modules
from brainvisa.processes import *
from brainvisa.group_utils import Subject

# Soma-base module
from soma.minf.api import registerClass, readMinf
from soma.path import find_in_path


# Plot constel module
def validation():
    if not find_in_path("constelConnectivityProfileOverlapMask.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")

name = "Creation of a mask"
userLevel = 2

# Argument declaration
signature = Signature(
    "study", Choice(
        ("averaged approach", "avg"), ("concatenated approach", "concat")),
    "texture_group", String(),
    "patch_label", Choice(
        ("left corpus callosum", 1), ("left bankssts", 2),
        ("left caudal anterior cingulate", 3),
        ("left caudal middle frontal", 4), ("left cuneus", 6),
        ("left entorhinal", 7), ("left fusiform", 8),
        ("left inferior parietal", 9), ("left inferior temporal", 10),
        ("left isthmus cingulate", 11), ("left lateral occipital", 12),
        ("left lateral orbitofrontal", 13), ("left lingual", 14),
        ("left medial orbitofrontal", 15), ("left middle temporal", 16),
        ("left parahippocampal", 17), ("left paracentral", 18),
        ("left pars opercularis", 19), ("left pars orbitalis", 20),
        ("left pars triangularis", 21), ("left pericalcarine", 22),
        ("left postcentral", 23), ("left posterior cingulate", 24),
        ("left precentral", 25), ("left precuneus", 26),
        ("left rostral anterior cingulate", 27),
        ("left rostral middle frontal", 28), ("left superior frontal", 29),
        ("left superior parietal", 30), ("left superior temporal", 31),
        ("left supramarginal", 32), ("left frontal pole", 33),
        ("left temporal pole", 34), ("left transverse temporal", 35),
        ("left insula", 36), ("right corpus callosum", 37),
        ("right bankssts", 38), ("right caudal anterior cingulate", 39),
        ("right caudal middle frontal", 40), ("right cuneus", 42),
        ("right entorhinal", 43), ("right fusiform", 44),
        ("right inferior parietal", 45), ("right inferior temporal", 46),
        ("right isthmus cingulate", 47), ("right lateral occipital", 48),
        ("right lateral orbitofrontal", 49), ("right lingual", 50),
        ("right medial orbitofrontal", 51), ("right middle temporal", 52),
        ("right parahippocampal", 53), ("right paracentral", 54),
        ("right pars opercularis", 55), ("right pars orbitalis", 56),
        ("right pars triangularis", 57), ("right pericalcarine", 58),
        ("right postcentral", 59), ("right posterior cingulate", 60),
        ("right precentral", 61), ("right precuneus", 62),
        ("right rostral anterior cingulate", 63),
        ("right rostral middle frontal", 64), ("right superior frontal", 65),
        ("right superior parietal", 66), ("right superior temporal", 67),
        ("right supramarginal", 68), ("right frontal pole", 69),
        ("right temporal pole", 70), ("right transverse temporal", 71),
        ("right insula", 72)),
    "smoothing", Float(),
    "group", ReadDiskItem("Group definition", "XML"),
    "connectivity_profiles", ListOf(
        ReadDiskItem("Gyrus Connectivity Profile", "Aims texture formats")),
    "mask", WriteDiskItem("Avg Connectivity Mask", "Aims texture formats"), )


# Default values
def initialization(self):
    self.smoothing = 3.0
    self.texture_group = "fsgroup"

    # function of link between individual profiles and group
    def linkIndProfiles(self, dummy):
        if self.group is not None:
            registerClass("minf_2.0", Subject, "Subject")
            groupOfSubjects = readMinf(self.group.fullPath())
            profiles = []
            for subject in groupOfSubjects:
                atts = dict(self.group.hierarchyAttributes())
                atts["study"] = self.study
                atts["gyrus"] = "G" + str(self.patch_label)
                atts["texture"] = "fs" + os.path.basename(
                    os.path.dirname(self.group.fullPath()))
                atts["smoothing"] = "smooth" + str(self.smoothing)
                profile = ReadDiskItem(
                    "Gyrus Connectivity Profile",
                    "Aims texture formats").findValue(
                        atts,
                        subject.attributes())
                if profile is not None:
                    profiles.append(profile)
            return profiles

    # function of link between mask and group
    def linkMask(self, dummy):
        if self.group is not None:
            atts = dict(self.group.hierarchyAttributes())
            atts["study"] = self.study
            atts["texture"] = self.texture_group
            atts["gyrus"] = "G" + str(self.patch_label)
            atts["smoothing"] = "smooth" + str(self.smoothing)
            return self.signature["mask"].findValue(atts)

    # link of parameters
    self.linkParameters(
        "connectivity_profiles", ("group", "study", "patch_label",
                                  "smoothing"), linkIndProfiles)
    self.linkParameters(
        "mask",
        ("connectivity_profiles",
         "texture_group",
         "smoothing"),
        linkMask)

    # visibility level
    self.signature["texture_group"].userLevel = 2
    self.signature["connectivity_profiles"].userLevel = 2


def execution(self, context):
    # show the connectivity profiles
    context.write(str([i.fullPath()
                  for i in self.connectivity_profiles]))

    args = []
    for x in self.connectivity_profiles:
        args += ["-p", x]
    args += ["-o", self.mask]
    context.system(sys.executable,
                   find_in_path("constelConnectivityProfileOverlapMask.py"),
                   *args)
