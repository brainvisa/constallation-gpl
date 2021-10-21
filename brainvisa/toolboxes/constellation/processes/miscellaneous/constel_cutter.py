###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################
import os

from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import OpenChoice
from brainvisa.processes import Choice
from brainvisa.processes import ValidationError
from brainvisa.processes import Boolean

# soma module
from soma.path import find_in_path

# ---------------------------Imports-------------------------------------------


def validation(self):
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constel_cut_region.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")
    try:
        from constel.lib.utils.filetools import select_ROI_number
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")

# ---------------------------Header--------------------------------------------


name = "Constellation Cutter"
userLevel = 1

signature = Signature(
    # inputs
    "regions_nomenclature", ReadDiskItem("Nomenclature ROIs File",
                                         "Text File",
                                         section="Inputs"),
    "original_texture", ReadDiskItem("Connectivity ROI Texture",
                                     "Aims texture formats",
                                     section="Inputs"),
    "region", OpenChoice(section="Inputs"),

    # outputs
    "cut_texture", WriteDiskItem("Connectivity ROI Texture",
                                 "Aims texture formats",
                                 section="Outputs"),

    "cut_region", WriteDiskItem("Connectivity ROI Texture",
                                "Aims texture formats",
                                section="Outputs"),
    "keep_cut_texture", Boolean(section="Options"),
    "keep_cut_region", Boolean(section="Options"),
)

# ---------------------------Functions-----------------------------------------


def initialization(self):
    """
    """
    self.keep_cut_texture = True
    self.keep_cut_region = True

    def reset_label(self, dummy):
        """Read and/or reset the region parameter.

        This callback reads the labels nomenclature and proposes them in the
        signature 'region' of process.
        It also resets the region parameter to default state after
        the nomenclature changes.
        """
        from constel.lib.utils.filetools import read_nomenclature_file
        current = self.region
        self.setValue("region", current, True)
        if self.regions_nomenclature is not None:
            s = [("Select a region in this list", None)]
            # temporarily set a value which will remain valid
            self.region = s[0][1]
            s += read_nomenclature_file(
                self.regions_nomenclature.fullPath(), mode=2)
            self.signature["region"].setChoices(*s)
            if isinstance(self.signature["region"], OpenChoice):
                self.signature["region"] = Choice(*s)
                self.changeSignature(self.signature)
            if current not in s:
                self.setValue("region", s[0][1], True)
            else:
                self.setValue("region", current, True)

    def link_cut_texture(self, dummy):
        """
        """
        if self.region and self.original_texture:
            ext = os.path.splitext(self.original_texture.fullPath())[1]
            filename = self.original_texture.fullName() + '_cut' + ext
            return filename

    def link_cut_region(self, dummy):
        """
        """
        if self.region and self.original_texture:
            ext = os.path.splitext(self.original_texture.fullPath())[1]
            region = '_' + self.region
            filename = self.original_texture.fullName() + '_cut' + region + ext
            return filename

    self.linkParameters(None,
                        "regions_nomenclature",
                        reset_label)

    self.linkParameters("cut_texture",
                        ["region", "original_texture"],
                        link_cut_texture)

    self.linkParameters("cut_region",
                        ["region", "original_texture"],
                        link_cut_region)


def execution(self, context):
    """Run the command 'constel_cut_region.py'.
    """
    from constel.lib.utils.filetools import select_ROI_number

    # Selects the label number corresponding to label name
    label = select_ROI_number(self.regions_nomenclature.fullPath(),
                              self.region)
    cmd = ["constel_cut_region.py",
           self.original_texture,
           label,
           self.cut_texture,
           self.cut_region]

    context.pythonSystem(*cmd)

    if not self.keep_cut_texture:
        self.cut_texture.eraseFiles()

    if not self.keep_cut_region:
        self.cut_region.eraseFiles()
