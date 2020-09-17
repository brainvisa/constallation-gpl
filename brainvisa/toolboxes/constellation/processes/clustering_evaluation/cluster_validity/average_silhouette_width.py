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
    - the interlinkages between inputs/outputs.
* executes the command "constel_calculate_asw.py": calculate the average
  silhouette width in order to obtain the optimal number of clusters.

Main dependencies: axon python API, soma-base, constel

Author: Sandrine Lefranc, 2015
"""

# ---------------------------Imports-------------------------------------------


# system module
from __future__ import absolute_import

# axon python API module
from brainvisa.processes import Integer
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError

# soma module
from soma.path import find_in_path


def validate(self):
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constel_calculate_asw.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ---------------------------Header--------------------------------------------


name = "Average Silhouette Width"
userLevel = 2

signature = Signature(
    # --inputs
    "reduced_matrix", ReadDiskItem("Connectivity Matrix",
                                   "Aims matrix formats",
                                   requiredAttributes={"ends_labelled": "all",
                                                       "reduced": "yes",
                                                       "intersubject": "yes",
                                                       "individual": "yes"},
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
    "kmin", Integer(section="Options"),
    "kmax", Integer(section="Options"),

    # --outputs--
    "clustering_silhouette", WriteDiskItem("Clustering Silhouette",
                                           "JSON file",
                                           section="Silhouette"),
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """
    """
    self.kmin = 2
    self.kmax = 12

    def link_silhouette(self, dummy):
        """
        """
        # if self.reduced_matrix:
        #     path = os.path.dirname(self.reduced_matrix.fullPath())
        #     # path = self.reduced_matrix.fullPath()
        #     # matrix_name = '.'.join(path.split('.')[:-2])
        #     filename = os.path.join(path, "asw.json")
        #     return filename
        if self.individual_clustering:
            match = dict(self.individual_clustering.hierarchyAttributes())
            return self.signature["clustering_silhouette"].findValue(match)

    def link_clusters(self, dummy):
        if self.reduced_matrix:
            match = dict(self.reduced_matrix.hierarchyAttributes())
            for att in ["name_serie", "tracking_session",  # "subject",
                        "analysis", "acquisition", "ends_labelled", "reduced",
                        "individual"]:
                if att in match:
                    del match[att]
            # artificially add format in match. If we do not do this, existing
            # (GIFTI) files and potential output ones (.tex) do not appear to
            # have the same attributes, and findValue() cannot decide.
            # strangely, findValues() returns 1 element...
            match["_format"] = 'GIFTI file'
            return self.signature["individual_clustering"].findValue(match)

    self.linkParameters(
        "individual_clustering", "reduced_matrix", link_clusters)
    self.linkParameters(
        "clustering_silhouette", "individual_clustering", link_silhouette)

# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constel_calculate_asw.py'.
    """
    base_cmd = ["constel_calculate_asw.py"]

    parameters = [self.reduced_matrix,
                  self.individual_clustering,
                  self.kmax,
                  self.clustering_silhouette]

    options = ["--kmin", str(self.kmin)]

    cmd = base_cmd + parameters + options

    context.pythonSystem(*cmd)
