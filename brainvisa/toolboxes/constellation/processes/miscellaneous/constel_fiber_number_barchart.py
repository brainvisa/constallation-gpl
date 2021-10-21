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

Main dependencies:
"""


# ----------------------------Imports------------------------------------------


# axon python API module
from __future__ import absolute_import
from brainvisa.processes import String
from brainvisa.processes import Boolean
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import ValidationError

# soma
from soma.path import find_in_path


def validation(self):
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constel_write_fibers_barchart.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")
    try:
        from constel.lib.utils.texturetools import select_ROI_number
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")

# ----------------------------Header-------------------------------------------


name = 'Fiber number by region'
userLevel = 2

signature = Signature(
    # inputs
    "fiber_tracts", ReadDiskItem(
        "Fascicles Bundles", "Aims writable bundles formats"),
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "cortical_region", String(),
    "sort", Boolean(),

    # ouput
    "filename", String(),
)


# ----------------------------Functions----------------------------------------


def initialization(self):
    """
    """

    self.sort = False
    # default value
    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_fiber2label(self, dummy):
        """Define the attribut 'gyrus' from fibertracts pattern for the
        signature 'cortical_region'.
        """
        if self.fiber_tracts is not None:
            s = str(self.fiber_tracts.get("gyrus"))
            name = self.signature["cortical_region"].findValue(s)
        return name

    self.linkParameters(
        "cortical_region", "fiber_tracts", link_fiber2label)


# ----------------------------Main Program-------------------------------------


def execution(self, context):
    """Execute the python command "constel_fibers_histogram".
    """
    from constel.lib.utils.texturetools import select_ROI_number

    # selects the label number corresponding to label name
    label_number = select_ROI_number(
        self.cortical_regions_nomenclature.fullPath(), self.cortical_region)

    # Give the name of the command
    cmd = ["constel_write_fibers_barchart.py"]

    # Give the options of the command
    cmd += [self.fiber_tracts,
            self.filename,
            label_number]

    if self.sort:
        cmd += ["-s"]

    # Execute the command
    context.system(*cmd)
