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
*
*

Main dependencies:

Author: Sandrine Lefranc, 2016
"""

#----------------------------Imports-------------------------------------------


# system module
import sys

# soma-base module
from soma.path import find_in_path

# axon python API module
from brainvisa.processes import Signature, ReadDiskItem, ListOf, Choice, \
    WriteDiskItem, neuroHierarchy, OpenChoice, String, ValidationError, Boolean

# constel modules
try:
    from constel.lib.utils.files import read_file
except:
    pass

def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constel_datacheck.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


#----------------------------Header--------------------------------------------


name = "Remove Individual Constellation Files"
userLevel = 2

signature = Signature(
    # --inputs--
    "database", Choice(),
    "method", Choice(("averaged approach", "avg"),
                     ("concatenated approach", "concat")),
    "study_name", String(),
    "ROIs_nomenclature", ReadDiskItem("Nomenclature ROIs File", "Text File"),
    "ROI", OpenChoice(),

    "fibers _near_cortex", Boolean(),
    "outside_fibers_of_cortex", Boolean(),
    "fibers_oversampled", Boolean(),
    "matrix_fibers_near_cortex", Boolean(),
    "matrix_outside_fibers_of_cortex", Boolean(),
    "smoothed_matrix", Boolean(),
    "profile_fibers_near_cortex", Boolean(),
    "profile_outside_fibers_of_cortex", Boolean(),
    "mean_profile", Boolean(),
    "normed_mean_profile", Boolean(),

    # --outputs--
    "rm_textfile", WriteDiskItem("Text file", "Text file"),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters.
    """
    # default values
    self.ROIs_nomenclature = self.signature["ROIs_nomenclature"].findValue({
        "atlasname": "desikan_freesurfer"})
    self.fibers_near_cortex = False
    self.outside_fibers_of_cortex = True
    self.fibers_oversampled = False
    self.matrix_fibers_near_cortex = True
    self.matrix_outside_fibers_of_cortex = True
    self.smoothed_matrix = False
    self.profile_fibers_near_cortex = True
    self.profile_outside_fibers_of_cortex = True
    self.mean_profile = False
    self.normed_mean_profile = False

    def link_roi(self, dummy):
        """Reads the ROIs nomenclature and proposes them in the signature 'ROI'
        of process.
        """
        if self.ROIs_nomenclature is not None:
            s = ["Select a ROI in this list"]
            s += read_file(self.ROIs_nomenclature.fullPath(), mode=2)
            self.signature["ROI"].setChoices(*s)
            if isinstance(self.signature['ROI'], OpenChoice):
                self.signature["ROI"] = Choice(*s)
                self.changeSignature(self.signature)

    def link_ofile(self, dummy):
        """
        """
        if self.database and self.ROI and self.study_name and self.method:
            filename = self.database + "/rmdata/" + self.method + "_" + \
                self.study_name + "_" + self.ROI + "_rmdata.txt"
            return filename

    # list of possible databases, while respecting the ontology
    databases = [h.name for h in neuroHierarchy.hierarchies()
                 if h.fso.name == "brainvisa-3.2.0"]
    self.signature["database"].setChoices(*databases)
    if len(databases) != 0:
        self.database = databases[0]
    else:
        self.signature["database"] = OpenChoice()

    # link of parameters for autocompletion
    self.linkParameters("ROI", "ROIs_nomenclature", link_roi)
    self.linkParameters(
        "rm_textfile", ("ROI", "database", "method", "study_name"),
        link_ofile)


#----------------------------Main program--------------------------------------


def execution(self, context):
    """
    """
    """Remove the Constellation files and write a text file on the status of
    the database.
    """
    # name of the command
    cmd = [sys.executable, find_in_path("constel_remove_data.py")]

    # declare the file status
    if self.fibers_near_cortex:
        cmd += ["--ifibers"]
    if self.outside_fibers_of_cortex:
        cmd += ["--ofibers"]
    if self.fibers_oversampled:
        cmd += ["--ovfibers"]
    if self.matrix_fibers_near_cortex:
        cmd += ["--imatrix"]
    if self.matrix_outside_fibers_of_cortex:
        cmd += ["--omatrix"]
    if self.smoothed_matrix:
        cmd += ["--smatrix"]
    if self.profile_fibers_near_cortex:
        cmd += ["--ifiberp"]
    if self.profile_outside_fibers_of_cortex:
        cmd += ["--ofiberp"]
    if self.mean_profile:
        cmd += ["--meanp"]
    if self.normed_mean_profile:
        cmd += ["--normp"]

    cmd += [self.database,
            self.method,
            self.study_name,
            self.ROI,
            self.rm_textfile]

    context.system(*cmd)