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
from brainvisa.processes import ListOf
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
        from constel.lib.utils.filetools import read_nomenclature_file
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
    "regions", ListOf(OpenChoice(), section="Inputs"),

    # outputs
    "cut_texture", WriteDiskItem("Connectivity ROI Texture",
                                 "Aims texture formats",
                                 section="Outputs"),

    "cut_regions", WriteDiskItem("Connectivity ROI Texture",
                                 "Aims texture formats",
                                 section="Outputs"),
    "keep_cut_texture", Boolean(section="Options"),
    "keep_cut_regions", Boolean(section="Options"),
)

# ---------------------------Functions-----------------------------------------


def initialization(self):
    """
    """
    from constel.lib.utils.filetools import read_nomenclature_file

    self.keep_cut_texture = True
    self.keep_cut_regions = True

    def link_regions(self, dummy):
        """
        """
        if self.regions_nomenclature is not None:
            self.regions = None
            s = []
            s += read_nomenclature_file(
                self.regions_nomenclature.fullPath(), mode=2)
            self.signature["regions"] = ListOf(Choice(*s), section="Inputs")
            self.changeSignature(self.signature)

    def link_cut_texture(self, dummy):
        """
        """
        if self.regions and self.original_texture:
            ext = os.path.splitext(self.original_texture.fullPath())[1]
            filename = self.original_texture.fullName() + '_cut' + ext
            return filename

    def link_cut_region(self, dummy):
        """
        """
        if self.regions and self.original_texture:
            ext = os.path.splitext(self.original_texture.fullPath())[1]
            filename = self.original_texture.fullName() + '_cut'
            for region in self.regions:
                filename += '-' + region
            filename += ext
            return filename

    self.linkParameters(None,
                        "regions_nomenclature",
                        link_regions)

    self.linkParameters("cut_texture",
                        ["regions", "original_texture"],
                        link_cut_texture)

    self.linkParameters("cut_regions",
                        ["regions", "original_texture"],
                        link_cut_region)


def execution(self, context):
    """Run the command 'constel_cut_region.py'.
    """
    from constel.lib.utils.filetools import select_ROI_number

    # Selects the label numbers corresponding to label names
    labels = []
    for region in self.regions:
        label = select_ROI_number(self.regions_nomenclature.fullPath(),
                                  region)
        labels.append(int(label))

    cmd = ["constel_cut_region.py",
           self.original_texture,
           labels,
           self.cut_texture,
           self.cut_regions]

    context.pythonSystem(*cmd)

    if not self.keep_cut_texture:
        self.cut_texture.eraseFiles()

    if not self.keep_cut_regions:
        self.cut_regions.eraseFiles()
