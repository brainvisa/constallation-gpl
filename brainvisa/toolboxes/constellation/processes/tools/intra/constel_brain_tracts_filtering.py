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
* define a Brainvisa process.
* execute the command 'constelBundlesFiltering'.

Main dependencies: axon python API, soma-base, constel
"""

# ---------------------------Imports-------------------------------------------


# python modules
import os

# axon python API module
from brainvisa.processes import Float
from brainvisa.processes import Choice
from brainvisa.processes import Signature
from brainvisa.processes import OpenChoice
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import neuroHierarchy
from brainvisa.processes import ValidationError

# soma module
from soma.path import find_in_path

# constel modules
try:
    from constel.lib.utils.filetools import read_file
    from constel.lib.utils.filetools import select_ROI_number
    from constel.lib.utils.fibertools import load_fiber_tracts
except:
    pass


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    cmd_name = "constelBundlesFiltering"
    if not find_in_path(cmd_name):  # checks command (C++)
        raise ValidationError(
            "'{0}' is not contained in PATH environnement variable. "
            "Please make sure that constel is installed.".format(cmd_name))


# ---------------------------Header--------------------------------------------


name = "Brain Tracts Filtering"
userLevel = 2

signature = Signature(
    # --inputs--
    "method", Choice(("averaged approach", "avg"),
                     ("concatenated approach", "concat")),
    "outputs_database", Choice(),
    "study_name", OpenChoice(),
    "fiber_tracts_format", Choice("bundles", "trk"),
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "cortical_region", OpenChoice(),
    "subject_directory", ReadDiskItem("subject", "directory"),
    "cortical_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),
    "dw_to_t1", ReadDiskItem(
        "Transform T2 Diffusion MR to Raw T1 MRI", "Transformation matrix"),
    "min_fibers_length", Float(),
    "max_fibers_length", Float(),

    # --outputs--
    "labeled_fibers", WriteDiskItem(
        "Filtered Fascicles Bundles", "Aims writable bundles formats",
        requiredAttributes={"ends_labelled": "both",
                            "oversampled": "no"}),
    "semilabeled_fibers", WriteDiskItem(
        "Filtered Fascicles Bundles", "Aims writable bundles formats",
        requiredAttributes={"ends_labelled": "one",
                            "oversampled": "no"}),
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and links between parameters.
    """
    # Define the default values
    self.min_fibers_length = 20.  # in mm
    self.max_fibers_length = 500.  # in mm
    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    # Get a list of possible databases, while respecting the ontology
    databases = [h.name for h in neuroHierarchy.hierarchies()
                 if h.fso.name == "brainvisa-3.2.0"]
    self.signature["outputs_database"].setChoices(*databases)
    if len(databases) != 0:
        self.outputs_database = databases[0]
    else:
        self.signature["outputs_database"] = OpenChoice()

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

    def reset_cortical_region(self, dummy):
        """Read and/or reset the cortical_region parameter.

        This callback reads the labels nomenclature and proposes them in the
        signature 'cortical_region' of process.
        It also resets the cortical_region parameter to default state after
        the nomenclature changes.
        """
        current = self.cortical_region
        self.setValue('cortical_region', current, True)
        if self.cortical_regions_nomenclature is not None:
            s = [("Select a cortical_region in this list", None)]
            # Temporarily set a value which will remain valid
            self.cortical_region = s[0][1]
            s += read_file(
                self.cortical_regions_nomenclature.fullPath(), mode=2)
            self.signature["cortical_region"].setChoices(*s)
            if isinstance(self.signature["cortical_region"], OpenChoice):
                self.signature["cortical_region"] = Choice(*s)
                self.changeSignature(self.signature)
            if current not in s:
                self.setValue('cortical_region', s[0][1], True)
            else:
                self.setValue('cortical_region', current, True)

    def link_filtered_bundles(self, dummy):
        """Defines all attributs of 'labeled_fibers' and return a filename.

        This function automatically creates the signature of 'labeled_fibers'.
        """
        if (self.outputs_database and self.study_name and
                self.cortical_region and self.subject_directory) is not None:
            attrs = dict()
            attrs["_database"] = self.outputs_database
            attrs["method"] = self.method
            attrs["studyname"] = self.study_name
            attrs["subject"] = os.path.basename(
                self.subject_directory.fullPath())
            attrs["gyrus"] = str(self.cortical_region)
            attrs["smallerlength"] = str(int(self.min_fibers_length))
            attrs["greaterlength"] = str(int(self.max_fibers_length))
            filename = self.signature["labeled_fibers"].findValue(attrs)
            return filename

    def link_between_filtered_bundles(self, dummy):
        """Defines all attributs of 'semilabeled_fibers' and return a filename.

        This function automatically creates the signature of
        'semilabeled_fibers'.
        """
        if (self.outputs_database and self.study_name and
                self.cortical_region and self.subject_directory) is not None:
            attrs = dict()
            attrs["_database"] = self.outputs_database
            attrs["method"] = self.method
            attrs["studyname"] = self.study_name
            attrs["subject"] = os.path.basename(
                self.subject_directory.fullPath())
            attrs["gyrus"] = str(self.cortical_region)
            attrs["smallerlength"] = str(int(self.min_fibers_length))
            attrs["greaterlength"] = str(int(self.max_fibers_length))
            filename = self.signature["semilabeled_fibers"].findValue(attrs)
            return filename

    # Link of parameters for autocompletion
    self.linkParameters(
        None, "cortical_regions_nomenclature", reset_cortical_region)
    self.linkParameters(None, "outputs_database", fill_study_choice)
    self.linkParameters("dw_to_t1", "subject_directory")
    self.linkParameters(
        "labeled_fibers", (
            "outputs_database", "subject_directory", "method", "study_name",
            "cortical_region", "min_fibers_length", "max_fibers_length"),
        link_filtered_bundles)
    self.linkParameters(
        "semilabeled_fibers", "labeled_fibers")

    fill_study_choice(self)


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constelBundlesFiltering'.

    This command filters the fiber tracts according to length.

    Two type of fiber tracts files are to be considered in this process:
        - the fibers near cortex are defined as having both ends attached to
          the mesh (and are consequently labelled)
        - the distant fibers are defined as having only one end attached to the
          mesh (the other being not identified)
    """
    # Select all fiber tracts of the given subject.
    list_fiber_tracts = load_fiber_tracts(
        self.subject_directory.fullPath(), self.fiber_tracts_format)

    # Select the region number corresponding to region name.
    region_number = select_ROI_number(
        self.cortical_regions_nomenclature.fullPath(), self.cortical_region)

    # Give the command name.
    cmd = ["constelBundlesFiltering"]

    # Give the command options.
    for fiber_tract in list_fiber_tracts:
        cmd += ["-i", fiber_tract]
    cmd += [
        "-o", self.labeled_fibers,
        "-n", self.semilabeled_fibers,
        "--mesh", self.white_mesh,
        "--tex", self.cortical_parcellation,
        "--trs", self.dw_to_t1,
        "--mode", "Name1_Name2orNotInMesh",
        "--names", "^" + str(region_number) + "_[+-]?[0-9]+$",
        "--names", "^[+-]?[0-9]+_" + str(region_number) + "$",
        "-g", region_number,
        "-r",
        "-l", self.min_fibers_length,
        "-L", self.max_fibers_length,
        "--nimlmin", self.min_fibers_length,
        "--nimlmax", self.max_fibers_length,
        "--verbose"
    ]

    # Execute the command.
    context.system(*cmd)
