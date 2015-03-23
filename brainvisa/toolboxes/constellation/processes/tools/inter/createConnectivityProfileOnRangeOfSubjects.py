###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

# Axon python API module
from brainvisa.processes import *
from brainvisa.group_utils import Subject

# Soma-base module
from soma.minf.api import registerClass, readMinf


# Plot aims module
def validation():
    """This function is executed at BrainVisa startup when the process is loaded.

    It checks some conditions for the process to be available.
    """
    try:
        from soma import aims
    except:
        raise ValidationError(
            "Please make sure that constel module is installed.")

name = "Connectivity Profile of Group"
userLevel = 2

# Argument declaration
signature = Signature(
    "normed_connectivity_profiles", ListOf(
        ReadDiskItem("Normed Connectivity Profile", "Aims texture formats")),
    "group", ReadDiskItem("Group definition", "XML"),
    "new_name", String(),
    "normed_connectivity_profile_nb", ListOf(
        WriteDiskItem("Group Normed Connectivity Profile", "Aims texture formats")),
    "group_connectivity_profile", WriteDiskItem(
        "Avg Connectivity Profile", "Aims texture formats"),
)



def initialization(self):
    """Provides default values and link of parameters"""

    # optional value
    self.setOptional("new_name")
    
    def link_profiles(self, dummy):
        """Function of link between individual profiles and normed profiles.
        """
        profiles = []
        if self.group is not None:
            for profile in self.normed_connectivity_profiles:
                atts = dict(profile.hierarchyAttributes())
                atts["group_of_subjects"] = os.path.basename(
                    os.path.dirname(self.group.fullPath()))
                if self.new_name is not None:
                    atts["texture"] = self.new_name
                profile = WriteDiskItem(
                    "Group Normed Connectivity Profile",
                    "Aims texture formats").findValue(atts)
                if profile is not None:
                    profiles.append(profile)
            return profiles


    def link_group_profiles(self, dummy):
        """Function of link between individual profiles and group profile.
        """
        if (self.group and self.normed_connectivity_profiles) is not None:
            atts = dict(self.normed_connectivity_profiles[0].hierarchyAttributes())
            atts["group_of_subjects"] = os.path.basename(
                    os.path.dirname(self.group.fullPath()))
            if self.new_name is not None:
                atts["texture"] = self.new_name
            return self.signature["group_connectivity_profile"].findValue(atts)

    # link of parameters
    self.linkParameters("normed_connectivity_profile_nb", (
        "normed_connectivity_profiles", "group", "new_name"), link_profiles)
    self.linkParameters(
        "group_connectivity_profile",
        ("normed_connectivity_profiles", "group", "new_name"), link_group_profiles)


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
