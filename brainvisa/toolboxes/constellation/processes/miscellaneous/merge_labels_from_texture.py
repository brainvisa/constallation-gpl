#!/usr/bin/env python
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
"""


# ----------------------------Imports------------------------------------------


# axon python API module
from __future__ import absolute_import
from brainvisa.processes import Signature, String, ReadDiskItem, Boolean,\
    WriteDiskItem, OpenChoice, ValidationError, Choice, ListOf

# soma module
from soma.path import find_in_path


def validation():
    """
    This function is executed at BrainVisa startup when the process is loaded.
    It checks some conditions for the process to be available.
    """
    if not find_in_path("AimsMergeLabelsFromTexture.py"):
        raise ValidationError("aims module is not here.")
    if not find_in_path("AimsExtractLabelsFromTexture.py"):
        raise ValidationError("aims module is not here.")
    try:
        from constel.lib.utils.filetools import read_nomenclature_file,\
            select_ROI_number, add_region_in_nomenclature,\
            delete_regions_in_nomenclature
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ----------------------------Header-------------------------------------------


name = "Merge Labels From texture"
userLevel = 2

signature = Signature(
    # inputs
    "cortical_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "cortical_regions", OpenChoice(),
    "new_cortical_region", String(),

    # outputs
    "new_cortical_parcellation", WriteDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "new_nomenclature", WriteDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "keep_only_merged_regions", Boolean(),)


# ----------------------------Functions----------------------------------------


def initialization(self):
    """
    """

    self.keep_only_merged_regions = False
    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

    def link_cortical_regions(self, dummy):
        """
        """
        from constel.lib.utils.filetools import read_nomenclature_file
        if self.cortical_regions_nomenclature is not None:
            s = []
            s += read_nomenclature_file(
                self.cortical_regions_nomenclature.fullPath(), mode=2)
            self.signature["cortical_regions"] = ListOf(Choice(*s))
            self.changeSignature(self.signature)

    self.linkParameters(
        "cortical_regions", "cortical_regions_nomenclature",
        link_cortical_regions)

# ----------------------------Main Program-------------------------------------


def execution(self, context):
    """
    """
    from constel.lib.utils.filetools import select_ROI_number,\
        add_region_in_nomenclature, delete_regions_in_nomenclature

    cmd_args = []
    nb = []
    for region in self.cortical_regions:
        # Select the region number corresponding to region name
        region_number = select_ROI_number(
            self.cortical_regions_nomenclature.fullPath(),
            region)
        cmd_args += ["-l", region_number]
        nb.append(region_number)
    min_nb = min(nb)
    cmd_args += ["-i", self.cortical_parcellation,
                 "-n", min_nb,
                 "-o", self.new_cortical_parcellation]
    if not self.keep_only_merged_regions:
        context.system("python",
                       find_in_path("AimsMergeLabelsFromTexture.py"),
                       *cmd_args)
    else:
        context.system("python",
                       find_in_path("AimsExtractLabelsFromTexture.py"),
                       *cmd_args)
    up_nom = delete_regions_in_nomenclature(
        self.cortical_regions_nomenclature.fullPath(),
        nb,
        self.new_nomenclature.fullPath())
    add_region_in_nomenclature(up_nom,
                               self.new_cortical_region,
                               min_nb)
