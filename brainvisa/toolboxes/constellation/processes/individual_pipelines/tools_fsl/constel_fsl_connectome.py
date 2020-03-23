###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################


# ---------------------------Imports-------------------------------------------

# System module
from __future__ import absolute_import
import os

# axon python API module
from brainvisa.processes import Choice
from brainvisa.processes import String
from brainvisa.processes import Signature
from brainvisa.processes import OpenChoice
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError

# soma.path module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    cmd = "constel_reorganize_fsl_connectome.py"
    if not find_in_path(cmd):  # checks command
        raise ValidationError(
            "'{0}' is not contained in PATH environnement variable. "
            "Please make sure that constel module is installed.".format(cmd))
    try:
        from constel.lib.utils.filetools import read_file, select_ROI_number
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ---------------------------Header--------------------------------------------


name = "FSL Connectome."
userLevel = 2

signature = Signature(
    "regions_nomenclature", ReadDiskItem("Nomenclature ROIs File",
                                         "Text File",
                                         section="Nomenclature"),

    "region", OpenChoice(section="Study parameters"),

    # --inputs--
    "probtrackx_indir", ReadDiskItem("directory",
                                     "directory",
                                     section="FSL import"),

    "regions_parcellation", ReadDiskItem("ROI Texture",
                                         "Aims texture formats",
                                         section="Freesurfer data"),

    # --outputs--
    "temp_outdir", WriteDiskItem("directory", "directory",
                                 section="Temporary outputs"),
    "output_connectome", String(section="Temporary outputs"),
)

# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters"""
    self.regions_nomenclature = self.signature[
        "regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    self.signature["output_connectome"].userLevel = 3

    def reset_label(self, dummy):
        """Read and/or reset the region parameter.

        This callback reads the labels nomenclature and proposes them in the
        signature 'region' of process.
        It also resets the region parameter to default state after
        the nomenclature changes.
        """
        from constel.lib.utils.filetools import read_file
        current = self.region
        self.setValue("region", current, True)
        if self.regions_nomenclature is not None:
            s = [("Select a region in this list", None)]
            # temporarily set a value which will remain valid
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

    def link_connectome(self, dummy):
        """
        """
        from constel.lib.utils.filetools import select_ROI_number
        if (self.probtrackx_indir is not None
            and self.regions_nomenclature is not None
                and self.region is not None and self.temp_outdir is not None):
            subject = os.path.basename(self.probtrackx_indir.fullPath())
            sdir = os.path.join(self.temp_outdir.fullPath(), subject)
            label_nb = select_ROI_number(self.regions_nomenclature.fullPath(),
                                         self.region)
            name = "connectome_label" + str(label_nb) + ".imas"
            connectome = os.path.join(sdir, name)
            return connectome

    # link of parameters for autocompletion
    self.linkParameters(None,
                        "regions_nomenclature",
                        reset_label)
    self.linkParameters("output_connectome",
                        ("probtrackx_indir",
                         "regions_nomenclature",
                         "region",
                         "temp_outdir"),
                        link_connectome)


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constel_reorganize_fsl_connectome.py'.

    Compute connectome from the FSL outputs (probtrackx2)."""
    from constel.lib.utils.filetools import select_ROI_number
    # Selects the label number corresponding to label name
    label_number = select_ROI_number(self.regions_nomenclature.fullPath(),
                                     self.region)

    # matrix smoothing: -s in millimetres
    context.pythonSystem("constel_reorganize_fsl_connectome.py",
                         self.probtrackx_indir,
                         self.regions_parcellation,
                         label_number,
                         self.temp_outdir)
