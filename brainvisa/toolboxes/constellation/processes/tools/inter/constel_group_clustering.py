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


name = "Clustering From Reduced Group Matrix"
userLevel = 2

signature = Signature(
    # --inputs--
    "intersubject_reduced_matrices", ListOf(ReadDiskItem(
        "Connectivity Matrix", "Aims matrix formats",
        requiredAttributes={"ends_labelled": "mixed",
                            "reduced": "Yes",
                            "dense": "No",
                            "intersubject": "Yes"})),
    "method", Choice(
        ("averaged approach", "avg"), ("concatenated approach", "concat")),
    "subjects_group", ReadDiskItem("Group definition", "XML"),
    "ROIs_segmentation", ListOf(ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"})),
    "average_mesh", ReadDiskItem(
        "White Mesh", "BrainVISA mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes",
                            "averaged": "Yes"}),
    "nb_clusters", Integer(),

    # --outputs--
    "reduced_group_matrix", WriteDiskItem(
        "Connectivity Matrix", "Aims matrix formats",
        requiredAttributes={"ends_labelled": "mixed",
                            "reduced": "Yes",
                            "dense": "No",
                            "intersubject": "Yes"}),
    "ROI_clustering", ListOf(WriteDiskItem(
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
    self.nb_clusters = 12

    def link_matrices(self, dummy):
        """Function of link between the reduced connectivity matrices and
        the group matrix
        """
        if self.subjects_group and self.intersubject_reduced_matrices:
            atts = dict(
                self.intersubject_reduced_matrices[0].hierarchyAttributes())
            for att_name in [
                    'name_serie', 'tracking_session',
                    '_declared_attributes_location', 'analysis', '_ontology',
                    'acquisition']:
                if att_name in atts:
                    del atts[att_name]
            atts["group_of_subjects"] = os.path.basename(
                os.path.dirname(self.subjects_group.fullPath()))
            return self.signature["reduced_group_matrix"].findValue(atts)

    def linkClustering(self, dummy):
        """function of link between clustering time and individualm reduced
        connectivity matrices
        """
        if self.subjects_group and self.intersubject_reduced_matrices:
            tmp = dict(
                self.intersubject_reduced_matrices[0].hierarchyAttributes())
            if tmp["study"] == "avg":
                atts = dict(
                    self.intersubject_reduced_matrices[0].hierarchyAttributes())
                atts["subject"] = "avgSubject"
                for att_name in [
                        'name_serie', 'tracking_session',
                        '_declared_attributes_location', 'analysis',
                        '_ontology', 'acquisition']:
                    if att_name in atts:
                        del atts[att_name]
                return self.signature[
                    "ROI_clustering"].contentType.findValue(atts)
            elif tmp["study"] == "concat":
                profiles = []
                for matrix in self.intersubject_reduced_matrices:
                    atts = dict(matrix.hierarchyAttributes())
                    for att_name in [
                            'name_serie', 'tracking_session',
                            '_declared_attributes_location', 'analysis',
                            '_ontology', 'acquisition']:
                        if att_name in atts:
                            del atts[att_name]
                    profile = self.signature[
                        'ROI_clustering'].contentType.findValue(atts)
                    if profile is not None:
                        profiles.append(profile)
                return profiles

    # link of parameters for autocompletion
    self.linkParameters(
        "reduced_group_matrix", ("subjects_group",
                                 "intersubject_reduced_matrices"),
        link_matrices)
    self.linkParameters(
        "ROI_clustering", ("subjects_group", "intersubject_reduced_matrices",),
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
    patch = identify_patch_number(self.reduced_group_matrix.fullPath())

    args = []
    for x in self.intersubject_reduced_matrices:
        args += ["-m", x]

    args += ["-o", self.reduced_group_matrix, "-s", self.method]
    context.system("python", find_in_path("constelCalculateGroupMatrix.py"),
                   *args)
    ma = aims.read(self.reduced_group_matrix.fullPath())
    context.write(ma.header())

    cmd_args = []
    for t in self.ROI_clustering:
        cmd_args += ["-p", t]
    for y in self.ROIs_segmentation:
        cmd_args += ["-t", y]
    cmd_args += ["-m", self.average_mesh, "-l", str(patch),
                 "-s", self.method, "-g", self.reduced_group_matrix, "-a", self.nb_clusters]
    context.system("python", find_in_path("constelInterSubjectClustering.py"),
                   *cmd_args)
