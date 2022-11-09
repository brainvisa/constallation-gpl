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
from __future__ import absolute_import
import os

# Axon python API module
from brainvisa.processes import Float
from brainvisa.processes import Choice
from brainvisa.processes import Signature
from brainvisa.processes import OpenChoice
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import neuroHierarchy
from brainvisa.processes import ValidationError
from brainvisa.processes import getAllFormats

# Soma module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    cmd = "constelBundlesFiltering"
    if not find_in_path(cmd):
        raise ValidationError(
            "'{0}' is not contained in PATH environnement variable. "
            "Please make sure that constel package is installed.".format(cmd))
    try:
        from constel.lib.utils.filetools import read_nomenclature_file,\
            select_ROI_number
        from constel.lib.utils.fibertools import load_fiber_tracts
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ---------------------------Header--------------------------------------------


name = "Brain Tracts Filtering - MRtrix"
userLevel = 2

signature = Signature(
    "regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File", section="Nomenclature"),
    "outputs_database", Choice(section="Study parameters"),
    "study_name", OpenChoice(section="Study parameters"),
    "method", Choice(
        ("averaged approach", "avg"),
        ("concatenated approach", "concat"),
        section="Study parameters"),
    "region", OpenChoice(section="Study parameters"),

    # inputs
    "tractography", ReadDiskItem(
        "Fascicles bundles", "Aims readable bundles formats",
        section="Tractography inputs"),
    "weights_file", ReadDiskItem("Fiber weights", "Text File",
                                 section="Tractography inputs"),
    "dw_to_mesh", ReadDiskItem(
        "Transform T2 Diffusion MR to Raw T1 MRI",
        "Transformation matrix",
        section="Tractography inputs"),
    "individual_white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"},
        section="Freesurfer data"),
    "regions_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"},
        section="Freesurfer data"),
    "min_fibers_length", Float(section="Options"),
    "max_fibers_length", Float(section="Options"),

    # outputs
    "labeled_fibers", WriteDiskItem(
        "Filtered Fascicles Bundles", "Aims writable bundles formats",
        requiredAttributes={"ends_labelled": "both",
                            "oversampled": "no"},
        section="Filtered tracts"),
    "semilabeled_fibers", WriteDiskItem(
        "Filtered Fascicles Bundles", "Aims writable bundles formats",
        requiredAttributes={"ends_labelled": "one",
                            "oversampled": "no"},
        section="Filtered tracts"),
    "labeled_fibers_weights", WriteDiskItem("Fiber weights", "Text File",
                                            section="Weights outputs"),
    "semilabeled_fibers_weights", WriteDiskItem("Fiber weights", "Text File",
                                                section="Weights outputs"),
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and links between parameters.
    """
    # Define the default values
    self.min_fibers_length = 20.  # in mm
    self.max_fibers_length = 500.  # in mm
    self.regions_nomenclature = self.signature[
        "regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    self.setOptional("weights_file")
    self.setOptional("labeled_fibers_weights")
    self.setOptional("semilabeled_fibers_weights")

    # Get a list of possible databases while respecting the ontology
    databases = [h.name for h in neuroHierarchy.hierarchies()
                 if h.fso.name == "brainvisa-3.2.0"]
    self.signature["outputs_database"].setChoices(*databases)
    if len(databases) != 0:
        self.outputs_database = databases[0]
    else:
        self.signature["outputs_database"] = OpenChoice(
                                                section="Study parameters"
        )

    def link_labeled_weights(self, dummy):
        """Set the name of weights file. Hard coded for now.
        """
        if self.labeled_fibers:
            filename = os.path.splitext(self.labeled_fibers.fullPath())[0]
            weights_filename = filename + '_weights.txt'
            return weights_filename

    def link_semilabeled_weights(self, dummy):
        """Set the name of weights file. Hard coded for now.
        """
        if self.semilabeled_fibers:
            filename = os.path.splitext(self.semilabeled_fibers.fullPath())[0]
            weights_filename = filename + '_weights.txt'
            return weights_filename

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
        from constel.lib.utils.filetools import read_nomenclature_file
        current = self.region
        self.setValue('region', current, True)
        if self.regions_nomenclature is not None:
            s = [("Select a region in this list", None)]
            self.region = s[0][1]
            s += read_nomenclature_file(
                self.regions_nomenclature.fullPath(), mode=2)
            self.signature["region"].setChoices(*s)
            if isinstance(self.signature["region"], OpenChoice):
                self.signature["region"] = Choice(*s,
                                                  section="Study parameters")
                self.changeSignature(self.signature)
            if current not in s:
                self.setValue("region", s[0][1], True)
            else:
                self.setValue("region", current, True)

    def link_filtered_bundles(self, dummy):
        """Defines all attributs of 'labeled_fibers' and return a filename.

        This function automatically creates the signature of 'labeled_fibers'.
        """
        if (self.outputs_database and self.study_name
                and self.region and self.tractography) is not None:
            attrs = dict()
            attrs["_database"] = self.outputs_database
            attrs["method"] = self.method
            attrs["studyname"] = self.study_name
            attrs["subject"] = os.path.basename(
                os.path.dirname(self.tractography.fullPath()))
            attrs["gyrus"] = str(self.region)
            attrs["smallerlength"] = str(int(self.min_fibers_length))
            attrs["greaterlength"] = str(int(self.max_fibers_length))
            filename = self.signature["labeled_fibers"].findValue(attrs)
            return filename

    # Link of parameters for autocompletion
    self.linkParameters(None,
                        "regions_nomenclature",
                        reset_region)
    self.linkParameters(None,
                        "outputs_database",
                        fill_study_choice)
    self.linkParameters("dw_to_mesh",
                        "tractography")
    self.linkParameters("labeled_fibers",
                        ("outputs_database", "tractography", "method",
                         "study_name", "region", "min_fibers_length",
                         "max_fibers_length"),
                        link_filtered_bundles)
    self.linkParameters("semilabeled_fibers",
                        "labeled_fibers")
    self.linkParameters("labeled_fibers_weights",
                        "labeled_fibers",
                        link_labeled_weights)
    self.linkParameters("semilabeled_fibers_weights",
                        "semilabeled_fibers",
                        link_semilabeled_weights)
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
    from constel.lib.utils.filetools import select_ROI_number

    # Select the region number corresponding to region name.
    region_number = select_ROI_number(self.regions_nomenclature.fullPath(),
                                      self.region)

    # Give the command name.
    cmd = ["constelBundlesFiltering"]

    # Give the command options.
    cmd += [
        "-i", self.tractography,
        "-o", self.labeled_fibers,
        "-n", self.semilabeled_fibers,
        "--mesh", self.individual_white_mesh,
        "--tex", self.regions_parcellation,
        "--trs", self.dw_to_mesh,
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

    if self.weights_file:
        cmd += ["--weightsFilename", self.weights_file]

    # Execute the command.
    context.system(*cmd)
