###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################


# ---------------------------Imports-------------------------------------------


# System modules
import os
import shutil

# Axon python API module
from brainvisa.processes import Float
from brainvisa.processes import Choice
from brainvisa.processes import String
from brainvisa.processes import Signature
from brainvisa.processes import OpenChoice
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import getAllFormats
from brainvisa.processes import neuroHierarchy
from brainvisa.processes import ValidationError


# Soma module
from soma.path import find_in_path

# Package import
try:
    from constel.lib.utils.filetools import read_file
except:
    pass


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    cmd = "constelBundlesFiltering"
    if not find_in_path(cmd):
        raise ValidationError(
            "'{0}' is not contained in PATH environnement variable. "
            "Please make sure that constel package is installed.".format(cmd))


# ---------------------------Header--------------------------------------------


name = "Import Connectomes."
userLevel = 2

signature = Signature(
    # --inputs--
    "outputs_database", Choice(),
    "study_name", OpenChoice(),
    "method", Choice(("averaged approach", "avg"),
                     ("concatenated approach", "concat")),
    "regions_nomenclature", ReadDiskItem("Nomenclature ROIs File",
                                         "Text File"),
    "region", OpenChoice(),
    "min_fibers_length", Float(),
    "fsl_connectome", ReadDiskItem('Any Type', getAllFormats()),

    # --outputs--
    "complete_individual_matrix", WriteDiskItem("Connectivity Matrix",
                                                "Sparse Matrix",
                                                requiredAttributes={
                                                    "ends_labelled": "all",
                                                    "reduced": "no",
                                                    "intersubject": "no"}),
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and links between parameters.
    """
    # Define the default values
    self.min_fibers_length = 20.  # in mm
    self.regions_nomenclature = self.signature[
        "regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    # Get a list of possible databases, while respecting the ontology
    databases = [h.name for h in neuroHierarchy.hierarchies()
                 if h.fso.name == "brainvisa-3.2.0"]
    self.signature["outputs_database"].setChoices(*databases)
    if len(databases) != 0:
        self.outputs_database = databases[0]
    else:
        self.signature["outputs_database"] = OpenChoice()

    def link_matrix(self, dummy):
        """
        """
        if (self.outputs_database is not None and
           self.study_name is not None and self.method is not None and
           self.region is not None):
            attrs = dict()
            attrs["_database"] = self.outputs_database
            attrs["center"] = "subjects"
            attrs["method"] = self.method
            attrs["tracking_session"] = None
            attrs["studyname"] = self.study_name
            attrs["smoothing"] = str(0.0)
            attrs["smallerlength"] = str(self.min_fibers_length)
            attrs["greaterlength"] = str(500.0)
            attrs["tracking_session"] = "default_tracking_session"
            attrs["subject"] = os.path.basename(
               os.path.dirname(self.fsl_connectome.fullPath()))
            attrs["gyrus"] = str(self.region)
            filename = self.signature[
                "complete_individual_matrix"].findValue(attrs)
            return filename

    def fill_study_choice(self, dummy=None):
        """
        """
        choices = set()
        if self.outputs_database is not None:
            if neuroHierarchy.databases.hasDatabase(self.outputs_database):
                database = neuroHierarchy.databases.database(
                    self.outputs_database)
                sel = {"method": self.method}
                choices.update(
                    [x[0] for x in database.findAttributes(
                        ["studyname"], selection=sel,
                        _type="Filtered Fascicles Bundles")])
            else:
                choices = []
        self.signature["study_name"].setChoices(*sorted(choices))
        if len(choices) != 0 and self.isDefault("study_name") \
                and self.study_name not in choices:
            self.setValue("study_name", list(choices)[0], True)

    def reset_region(self, dummy):
        """Read and/or reset the region parameter.

        This callback reads the labels nomenclature and proposes them in the
        signature 'region' of process.
        It also resets the region parameter to default state after
        the nomenclature changes.
        """
        current = self.region
        self.setValue('region', current, True)
        if self.regions_nomenclature is not None:
            s = [("Select a region in this list", None)]
            # Temporarily set a value which will remain valid
            self.region = s[0][1]
            s += read_file(
                self.regions_nomenclature.fullPath(), mode=2)
            self.signature["region"].setChoices(*s)
            if isinstance(self.signature["region"], OpenChoice):
                self.signature["region"] = Choice(*s)
                self.changeSignature(self.signature)
            if current not in s:
                self.setValue("region", s[0][1], True)
            else:
                self.setValue("region", current, True)

    # Link of parameters for autocompletion
    self.linkParameters(None,
                        "regions_nomenclature",
                        reset_region)
    self.linkParameters(None,
                        "outputs_database",
                        fill_study_choice)
    self.linkParameters("complete_individual_matrix",
                        ("outputs_database",
                         "study_name",
                         "method",
                         "region",
                         "fsl_connectome",
                         "min_fibers_length"),
                        link_matrix)

    fill_study_choice(self)


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """
    """
    subject = os.path.basename(
        os.path.dirname(self.fsl_connectome.fullPath()))
    src = self.fsl_connectome.fullPath()
    matrix_name = (subject +
                   "_" +
                   self.study_name +
                   "_" +
                   self.region +
                   "_complete_matrix_smooth0.0_" +
                   str(self.min_fibers_length) +
                   "to500.0mm.imas")

    dstdir = os.path.join(self.outputs_database,
                          "subjects",
                          subject,
                          "diffusion",
                          "default_acquisition",
                          "default_analysis",
                          "default_tracking_session",
                          "connectivity_parcellation",
                          self.method,
                          self.study_name,
                          self.region,
                          "matrix")
    if not os.path.isdir(dstdir):
        os.makedirs(dstdir)

    dst = os.path.join(dstdir, matrix_name)
    print dst

    shutil.copy2(src, dst)
