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
    - the signature of the inputs/ouputs,
    - the initialization (by default) of the inputs,
    - the interlinkages between inputs/outputs.
* executes the commands 'constelCalculateGroupMatrix' and
  'constelInterSubjectClustering'.

Main dependencies: Axon python API, Soma-base, constel

Author: Sandrine Lefranc, 2015
"""

#----------------------------Imports-------------------------------------------

# python module
import os

# axon python API modules
from brainvisa.processes import Signature, ListOf, Choice, Integer, String, \
    ReadDiskItem, WriteDiskItem, ValidationError

# soma-base module
from soma.path import find_in_path

# constel module
try:
    from constel.lib.utils.files import select_ROI_number
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
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "cortical_region", String(),
    "subjects_group", ReadDiskItem("Group definition", "XML"),
    "cortical_parcellation", ListOf(ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"})),
    "average_mesh", ReadDiskItem(
        "White Mesh", "BrainVISA mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes",
                            "averaged": "Yes"}),
    "nb_clusters", Integer(),
    "clustering_algorithms", Choice(
        ("K-medoids clustering", "kmedoids"), ("Ward's method", "ward")),

    # --outputs--
    "reduced_group_matrix", WriteDiskItem(
        "Connectivity Matrix", "Gis image",
        requiredAttributes={"ends_labelled": "mixed",
                            "reduced": "No",
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
    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_matrix2label(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'cortical_region'.
        """
        if self.intersubject_reduced_matrices:
            s = self.intersubject_reduced_matrices[0].get("gyrus")
            name = self.signature["cortical_region"].findValue(s)
            return name

    def link_matrices(self, dummy):
        """Function of link between the reduced connectivity matrices and
        the group matrix
        """
        if self.subjects_group and self.intersubject_reduced_matrices:
            atts = dict(
                self.intersubject_reduced_matrices[0].hierarchyAttributes())
            for att_name in [
                    "name_serie", "tracking_session",
                    "_declared_attributes_location", "analysis", "_ontology",
                    "acquisition", "subject"]:
                if att_name in atts:
                    del atts[att_name]
            atts["group_of_subjects"] = os.path.basename(
                os.path.dirname(self.subjects_group.fullPath()))
            if self.method == "avg":
                atts["study"] = "avg"
            else:
                atts["study"] = "concat"
            return self.signature["reduced_group_matrix"].findValue(atts)

    def link_clustering(self, dummy):
        """function of link between clustering time and individual reduced
        connectivity matrices
        """
        if self.subjects_group and self.intersubject_reduced_matrices:
            if self.method == "avg":
                atts = dict(
                    self.intersubject_reduced_matrices[0].hierarchyAttributes()
                    )
                atts["subject"] = "avgSubject"
                atts["study"] = "avg"
                atts["tracking_session"] = None
                filename = self.signature[
                    "ROI_clustering"].contentType.findValue(atts)
                return filename
            else:
                profiles = []
                for matrix in self.intersubject_reduced_matrices:
                    atts = dict(matrix.hierarchyAttributes())
                    atts["study"] = "concat"
                    atts["tracking_session"] = None
                    profile = self.signature[
                        'ROI_clustering'].contentType.findValue(atts)
                    if profile is not None:
                        profiles.append(profile)
                return profiles

    # link of parameters for autocompletion
    self.linkParameters(
        "cortical_region", "intersubject_reduced_matrices", link_matrix2label)
    self.linkParameters(
        "reduced_group_matrix",
        ("subjects_group", "intersubject_reduced_matrices", "method"),
        link_matrices)
    self.linkParameters(
        "ROI_clustering",
        ("subjects_group", "intersubject_reduced_matrices", "method"),
        link_clustering)


#----------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constelInterSubjectClustering'.

    The gyrus vertices connectivity profiles of all the subjects are
    concatenated into a big matrix. The clustering is performed with the
    classical kmedoids algorithm and the Euclidean distance between profiles
    as dissimilarity measure.
    """
    # selects the label number corresponding to label name
    label_number = select_ROI_number(
        self.cortical_regions_nomenclature.fullPath(), self.cortical_region)

    args = []
    for x in self.intersubject_reduced_matrices:
        args += ["-m", x]

    args += ["-o", self.reduced_group_matrix, "-s", self.method]
    context.system("python", find_in_path("constelCalculateGroupMatrix.py"),
                   *args)

    cmd_args = []
    for t in self.ROI_clustering:
        cmd_args += ["-p", t]
    for y in self.cortical_parcellation:
        cmd_args += ["-t", y]
    cmd_args += ["-m", self.average_mesh,
                 "-l", str(label_number),
                 "-s", self.method,
                 "-g", self.reduced_group_matrix,
                 "-a", self.nb_clusters]
    context.system("python", find_in_path("constelInterSubjectClustering.py"),
                   *cmd_args)
