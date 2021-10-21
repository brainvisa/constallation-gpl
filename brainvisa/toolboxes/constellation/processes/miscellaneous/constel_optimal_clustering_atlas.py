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
from brainvisa.processes import OpenChoice

# soma module
from soma.path import find_in_path

# ---------------------------Imports-------------------------------------------


def validation(self):
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constel_select_optimal_clustering.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")

# ---------------------------Header--------------------------------------------


name = "Constellation Optimal Clustering From Atlas"
userLevel = 1

signature = Signature(
    # inputs
    "individual_clustering", ReadDiskItem("Connectivity ROI Texture",
                                          "Aims texture formats",
                                          requiredAttributes={
                                            "roi_autodetect": "no",
                                            "roi_filtered": "no",
                                            "intersubject": "yes",
                                            "step_time": "yes",
                                            "measure": "no"},
                                          section="Clustering inputs"),
    "region", OpenChoice(section="Clustering inputs"),
    "atlas_silhouette", ReadDiskItem("Clustering Silhouette",
                                     "JSON file",
                                     section="Atlas inputs"),

    # outputs
    "optimal_clustering", WriteDiskItem("Connectivity ROI Texture",
                                        "Aims texture formats",
                                        requiredAttributes={
                                            "roi_autodetect": "no",
                                            "roi_filtered": "no",
                                            "intersubject": "yes",
                                            "step_time": "yes",
                                            "measure": "no",
                                            "optimal": "silhouette"},
                                        section="Optimal result"),
)

# ---------------------------Functions-----------------------------------------


def initialization(self):
    """
    """

    def link_optimal_cluster(self, dummy):
        """
        """
        if self.individual_clustering:
            match = dict(self.individual_clustering.hierarchyAttributes())
            return self.signature["optimal_clustering"].findValue(match)

    def link_region(self, dummy):
        """
        """
        if self.individual_clustering:
            return self.individual_clustering.hierarchyAttributes()['gyrus']

    self.linkParameters("optimal_clustering",
                        "individual_clustering",
                        link_optimal_cluster)

    self.linkParameters("region",
                        "individual_clustering",
                        link_region)


def execution(self, context):
    """Run the command 'constel_select_optimal_clustering_from_atlas.py'.
    """

    cmd = ["constel_select_optimal_clustering_from_atlas.py",
           self.individual_clustering,
           self.region,
           self.atlas_silhouette,
           self.optimal_clustering]

    context.pythonSystem(*cmd)
