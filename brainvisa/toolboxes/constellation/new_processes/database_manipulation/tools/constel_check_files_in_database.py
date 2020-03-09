###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################


# ---------------------------Imports-------------------------------------------


# system module
from __future__ import absolute_import
import sys

# soma-base module
from soma.path import find_in_path

# axon python API module
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import Choice
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import neuroHierarchy
from brainvisa.processes import OpenChoice
from brainvisa.processes import String
from brainvisa.processes import ValidationError

# constel modules
try:
    from constel.lib.utils.filetools import read_file
except ImportError:
    raise ValidationError("Please make sure that constel module is installed.")


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constel_datacheck.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ---------------------------Header--------------------------------------------


name = "Check Constellation Files"
userLevel = 2

signature = Signature(
    # --inputs--
    "database", Choice(),
    "method", Choice(("averaged approach", "avg"),
                     ("concatenated approach", "concat")),
    "study_name", String(),
    "ROIs_nomenclature", ReadDiskItem("Nomenclature ROIs File", "Text File"),
    "ROI", OpenChoice(),

    # --outputs--
    "result_in_textfile", WriteDiskItem("Text file", "Text file"),
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters
    """
    # default values
    self.ROIs_nomenclature = self.signature["ROIs_nomenclature"].findValue({
        "atlasname": "desikan_freesurfer"})

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
            filename = self.database + "/datacheck/" + self.method + "_" + \
                self.study_name + "_" + self.ROI + "_datacheck.txt"
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
        "result_in_textfile", ("ROI", "database", "method", "study_name"),
        link_ofile)

# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Check the Constellation files and write a text file like report on the
    status of the database.
    """
    context.system(sys.executable,
                   find_in_path("constel_datacheck.py"),
                   self.database,
                   self.method,
                   self.study_name,
                   self.ROI,
                   self.result_in_textfile)
