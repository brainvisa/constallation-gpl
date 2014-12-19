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

# BrainVisa module
from brainvisa.processes import *
from soma import aims

# System module
import numpy


# Plot constel module
def validation():
    try:
        import constel
    except:
        raise ValidationError("Please make sure that constel module"
                              "is installed.")

try:
    from constel.lib.texturetools import remove_labels
except:
    pass


name = "Watershed of Group"
userLevel = 2

signature = Signature(
    "normed_connectivity_profile", ReadDiskItem(
        "Avg Normed Connectivity Profile", "Aims texture formats"),
    "average_mesh", ReadDiskItem("Mesh", "MESH mesh"),
    "watershed", WriteDiskItem(
        "Avg Watershed Texture", "Aims texture formats"),
    "filtered_watershed", WriteDiskItem(
        "Avg Filtered Watershed", "Aims texture formats"),
)


def initialization(self):
    # function of link between group and average_mesh
    def linkMesh(self, dummy):
        if self.normed_connectivity_profile is not None:
            group = os.path.basename(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.dirname(
                        self.normed_connectivity_profile.fullPath())))))))
            atts = {"freesurfer_group_of_subjects": group}
            print atts
            return self.signature["average_mesh"].findValue(atts)

    # link of parameters
    self.linkParameters("watershed", "normed_connectivity_profile")
    self.linkParameters("filtered_watershed", "normed_connectivity_profile")
    self.linkParameters(
        "average_mesh", "normed_connectivity_profile", linkMesh)


def execution(self, context):
    """ A watershed was computed on the joint patch cortical connectivity
    profile texture in order to split the cortical surface into catchment
    basins. Small basins are agglomerated to larger ones based on their
    depth and area. This set of T regions will be called atrget regions.
    A watershed is performed to obtain different patches of interest.
    """
    context.system("AimsMeshWatershed.py",
                   "-i", self.normed_connectivity_profile,
                   "-m", self.average_mesh,
                   "-k", 10,
                   "-q", 0.05,
                   "-z", "or",
                   "-t", 0.05,
                   "-o", self.watershed)

    # Low connections to gyrus : filtered watershed with "minVertex_nb"
    minVertex_nb = 20
    basins_tex = aims.read(self.watershed.fullPath())
    basinTex_ar = basins_tex[0].arraydata()
    basins_labels = numpy.unique(basinTex_ar).tolist()
    labelsToRemove_list = []
    for basin_label in basins_labels:
        if numpy.where(basinTex_ar == basin_label)[0].size < minVertex_nb:
            labelsToRemove_list.append(basin_label)
    filteredBasins = remove_labels(basins_tex, labelsToRemove_list)
    aims.write(filteredBasins, self.filtered_watershed.fullPath())