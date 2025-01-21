###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import Integer
from brainvisa.processes import OpenChoice

# soma module
from soma.path import find_in_path

# ---------------------------Imports-------------------------------------------


def validation(self):
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constel_clean_clusters.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")

# ---------------------------Header--------------------------------------------


name = "Constellation Clean Clustering"
userLevel = 1

signature = Signature(
    # inputs
    "reduced_individual_matrix", ReadDiskItem(
        "Connectivity Matrix", "Aims matrix formats",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "yes",
                            "intersubject": "yes"},
        section="Clustering inputs"),
    "individual_clustering", ReadDiskItem("Connectivity ROI Texture",
                                          "Aims texture formats",
                                          requiredAttributes={
                                            "roi_autodetect": "no",
                                            "roi_filtered": "no",
                                            "intersubject": "yes",
                                            "step_time": "yes",
                                            "measure": "no"},
                                          section="Clustering inputs"),
    "atlas_matrix", ReadDiskItem(
        "Connectivity Matrix", "Aims matrix formats",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "yes",
                            "intersubject": "yes",
                            "individual": "no"},
        section="Atlas inputs"),
    "group_clustering", ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "no",
                            "roi_filtered": "no",
                            "intersubject": "yes",
                            "step_time": "yes",
                            "measure": "no"},
        section="Atlas inputs"),
    "min_size", Integer(section="Options"),
    # outputs
    "cleaned_clustering", WriteDiskItem("Connectivity ROI Texture",
                                        "Aims texture formats",
                                        requiredAttributes={
                                            "roi_autodetect": "no",
                                            "roi_filtered": "no",
                                            "intersubject": "yes",
                                            "step_time": "yes",
                                            "measure": "no",
                                            "clean": "yes"},
                                        section="Cleaned result"),
)

# ---------------------------Functions-----------------------------------------


def initialization(self):
    """
    """
    # default values
    self.min_size = 30

    def link_cleaned_cluster(self, dummy):
        """
        """
        if self.individual_clustering:
            match = dict(self.individual_clustering.hierarchyAttributes())
            return self.signature["cleaned_clustering"].findValue(match)

    def link_clusters(self, dummy):
        if self.reduced_individual_matrix:
            match = dict(self.reduced_individual_matrix.hierarchyAttributes())
            for att in ["name_serie", "tracking_session",
                        "analysis", "acquisition", "ends_labelled", "reduced",
                        "individual"]:
                if att in match:
                    del match[att]
            # artificially add format in match. If we do not do this, existing
            # (GIFTI) files and potential output ones (.tex) do not appear to
            # have the same attributes, and findValue() cannot decide.
            # strangely, findValues() returns 1 element....
            match["_format"] = 'GIFTI file'
            return self.signature["individual_clustering"].findValue(match)

    def link_atlas_matrix(self, dummy):
        if self.reduced_individual_matrix:
            d = dict(self.reduced_individual_matrix.hierarchyAttributes())
            if 'gyrus' in d:
                match = {
                    "method": "avg",
                    "gyrus": d['gyrus'],
                }
                return self.signature["atlas_matrix"].findValue(match)

    def link_group_clustering(self, dummy):
        if self.atlas_matrix:
            match = dict(self.atlas_matrix.hierarchyAttributes())
            match["sid"] = 'avgSubject'
            return self.signature["group_clustering"].findValue(match)

    self.linkParameters("individual_clustering",
                        "reduced_individual_matrix",
                        link_clusters)

    self.linkParameters("atlas_matrix",
                        "reduced_individual_matrix",
                        link_atlas_matrix)

    self.linkParameters("group_clustering",
                        "atlas_matrix",
                        link_group_clustering)

    self.linkParameters("cleaned_clustering",
                        "individual_clustering",
                        link_cleaned_cluster)


def execution(self, context):
    """Run the command 'constel_clean_clusters.py'.
    """

    cmd = ["constel_clean_clusters.py",
           self.individual_clustering,
           self.reduced_individual_matrix,
           self.group_clustering,
           self.atlas_matrix,
           self.min_size,
           self.cleaned_clustering]

    context.pythonSystem(*cmd)
