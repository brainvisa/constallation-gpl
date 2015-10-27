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
* defines a Brainvisa process
    - the parameters of a process (Signature),
    - the parameters initialization
    - the linked parameters
* this process executes the commands 'constelCalculateGroupMatrix' and
  'constelInterSubjectClustering'.

Main dependencies: Axon python API, Soma-base, constel

Author: sandrine.lefranc@cea.fr
"""

#----------------------------Imports-------------------------------------------

# python module
import os

# axon python API modules
from brainvisa.processes import Signature, ListOf, Choice, Integer, \
    ReadDiskItem, WriteDiskItem, ValidationError

# soma-base module
from soma.path import find_in_path
from soma import aims

# constel module
try:
    from constel.lib.texturetools import identify_patch_number
except:
    pass


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constelInterSubjectClustering.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


#----------------------------Header--------------------------------------------


name = "Clustering of Group"
userLevel = 2

signature = Signature(
    # --inputs--
    "reduced_connectivity_matrix", ListOf(ReadDiskItem(
        "Connectivity Matrix", "Aims writable volume formats",
        requiredAttributes={"ends_labelled": "mixed",
                            "reduced": "Yes",
                            "dense": "No",
                            "intersubject": "Yes"})),
    "study", Choice(
        ("averaged approach", "avg"), ("concatenated approach", "concat")),
    "group", ReadDiskItem("Group definition", "XML"),
    "gyri_texture", ListOf(ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"})),
    "average_mesh", ReadDiskItem(
        "White Mesh", "BrainVISA mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes",
                            "averaged": "Yes"}),
    "kmax", Integer(),

    # --outputs--
    "group_matrix", WriteDiskItem(
        "Connectivity Matrix", "Aims writable volume formats",
        requiredAttributes={"ends_labelled": "mixed",
                            "reduced": "No",
                            "dense": "No",
                            "intersubject": "Yes"}),
    "clustering_time", ListOf(WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "No",
                            "roi_filtered": "No",
                            "averaged": "No",
                            "intersubject": "Yes",
                            "step_time": "Yes"})),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters"""
    
    # default value
    self.kmax = 12

    def link_matrices(self, dummy):
        """Function of link between the reduced connectivity matrices and
        the group matrix
        """
        if (self.group and self.reduced_connectivity_matrix) is not None:
            atts = dict(
                self.reduced_connectivity_matrix[0].hierarchyAttributes())
            atts["group_of_subjects"] = os.path.basename(
                os.path.dirname(self.group.fullPath()))
            return self.signature["group_matrix"].findValue(atts)

    def linkClustering(self, dummy):
        """function of link between clustering time and individualm reduced
        connectivity matrices
        """
        if (self.group and self.reduced_connectivity_matrix) is not None:
            tmp = dict(
                self.reduced_connectivity_matrix[0].hierarchyAttributes())
            if tmp["study"] == "avg":
                atts = dict(
                    self.reduced_connectivity_matrix[0].hierarchyAttributes())
                atts["subject"] = "avgSubject"
                return self.signature["clustering_time"].findValue(atts)
            elif tmp["study"] == "concat":
                profiles = []
                for matrix in self.reduced_connectivity_matrix:
                    atts = dict(matrix.hierarchyAttributes())
                    profile = ReadDiskItem(
                        "Group Clustering Time",
                        "BrainVISA texture formats").findValue(atts)
                    if profile is not None:
                        profiles.append(profile)
                return profiles

    # link of parameters for autocompletion
    self.linkParameters(
        "group_matrix", ("group", "reduced_connectivity_matrix"),
        link_matrices)
    self.linkParameters(
        "clustering_time", ("group", "reduced_connectivity_matrix",),
        linkClustering)


#----------------------------Main program--------------------------------------


def execution(self, context):
    """
    The gyrus vertices connectivity profiles of all the subjects are
    concatenated into a big matrix. The clustering is performed with the
    classical kmedoids algorithm and the Euclidean distance between profiles
    as dissimilarity measure.
    """
    # provides the patch name
    patch = identify_patch_number(self.group_matrix.fullPath())

    args = []
    for x in self.reduced_connectivity_matrix:
        args += ["-m", x]

    args += ["-o", self.group_matrix, "-s", self.study]
    context.system("python", find_in_path("constelCalculateGroupMatrix.py"),
                   *args)
    ma = aims.read(self.group_matrix.fullPath())
    context.write(ma.header())

    cmd_args = []
    for t in self.clustering_time:
        cmd_args += ["-p", t]
    for y in self.gyri_texture:
        cmd_args += ["-t", y]
    cmd_args += ["-m", self.average_mesh, "-l", str(patch),
                 "-s", self.study, "-g", self.group_matrix, "-a", self.kmax]
    context.system("python", find_in_path("constelInterSubjectClustering.py"),
                   *cmd_args)
