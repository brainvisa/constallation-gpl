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
* this process executes the command 'AimsMeshWatershed.py' and
  'constel_filtering_watershed.py': the ROI profile is computede from the mean
   profile.

Main dependencies: Axon python API, Soma-base, constel

Author: Sandrine Lefranc
"""


#----------------------------Imports-------------------------------------------


# Axon python API module
from brainvisa.processes import *

# Soma-base module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded.

    It checks some conditions for the process to be available.
    """
    if not find_in_path("constelConnectionDensityTexture"):
        raise ValidationError(
            "Please make sure that constel module is installed.")

name = "Ward Hierarchical Clustering Method"
userLevel = 2

signature = Signature(
    "kmax", Integer(),
    "patch", Integer(), # TODO: to put a label to a name?
    "group_matrix", String(), # TODO: to define a type
    "distance_matrix_file", String(), # TODO: to define a type
    "average_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side":"both",
                            "vertex_corr":"Yes",
                            "averaged":"Yes"}),
    "gyri_texture", ListOf(ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side":"both",
                            "vertex_corr":"Yes"})),
    "tex_time", ListOf(
        WriteDiskItem("Connectivity ROI Texture", "Aims texture formats",
                      requiredAttributes={"roi_autodetect":"no",
                                          "roi_filtered":"no",
                                          "intersubject":"yes",
                                          "step_time":"yes",
                                          "individual": "no"})),
)


#----------------------------Header--------------------------------------------


def initialization(self):
   '''Declare the default value.
   '''
   # Default value
   self.kmax = 12


def execution(self, context):
    """Run th command "constel_clustering_ward".
    
    Run a Ward's hierarchical clustering method.
    """
    args = ["constel_clustering_ward.py"]
    for x in self.gyri_texture:
        args += ["-g", x]
    for t in self.tex_time:
        args += ["-t", t]
    args += ["-k", self.kmax, "-l", self.patch, "-x", self.group_matrix,
             "-c", self.distance_matrix_file, "-m", self.average_mesh]
    context.pythonSystem(*args)
