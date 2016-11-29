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

#----------------------------Imports-------------------------------------------


# system module
import sys

# axon python API module
from brainvisa.processes import Float
from brainvisa.processes import ListOf
from brainvisa.processes import Integer
from brainvisa.processes import Boolean
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
    if not find_in_path("constel_calculate_scores.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


#----------------------------Header--------------------------------------------


name = "Scores"
userLevel = 2

signature = Signature(
    "clustering_1", ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "no",
                            "roi_filtered": "no",
                            "intersubject": "yes",
                            "step_time": "yes",
                            "measure": "no"}),
    "clustering_2", ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "no",
                            "roi_filtered": "no",
                            "intersubject": "yes",
                            "step_time": "yes",
                            "measure": "no"}),
    "time_step_max", Integer(),
    "output_dir", WriteDiskItem("Directory", "Directory"),
    "ybound", ListOf(Float()),
    "ignore_Kopt2",  Boolean(),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    pass
    self.time_step_max = 10
    self.setOptional("ybound")
    self.ignore_Kopt2 = False


def execution(self, context):
    """
    """
    cortical_region = self.clustering_1.get("gyrus")
    if self.clustering_1.get("subject") == "avgSubject":
        group1 = self.clustering_1.get("group_of_subjects")
        group2 = self.clustering_2.get("group_of_subjects")
        title = (cortical_region + "_" + group1 + "_" + group2 + "_"
                 + "avgSubject")
    else:
        subject1 = self.clustering_1.get("subject")
        subject2 = self.clustering_2.get("subject")
        group = self.clustering_1.get("group_of_subjects")
        print cortical_region
        print group
        print subject1
        print subject2
        title = str(cortical_region) + "_" + str(group) + "_" + str(subject1) + "_" + str(subject2)

    cmd = [sys.executable, find_in_path("constel_calculate_scores.py"),
           self.clustering_1,
           self.clustering_2,
           self.time_step_max,
           self.output_dir,
           title,
           cortical_region]

    if self.ybound:
        cmd += ["-s", self.ybound]

    if self.ignore_Kopt2:
        cmd += ["-r"]

    context.system(*cmd)
