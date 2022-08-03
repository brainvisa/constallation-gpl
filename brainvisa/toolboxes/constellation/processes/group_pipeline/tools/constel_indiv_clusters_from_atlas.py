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
* defines a Brainvisa process
    - the signature of the inputs/ouputs,
    - the initialization (by default) of the inputs,
    - the interlinkages between inputs/outputs.
* executes the command 'constel_clusters_from_atlas.py':

Main dependencies: axon python API, soma, constel
"""

# ---------------------------Imports-------------------------------------------


# axon python API module
from __future__ import absolute_import
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError
from brainvisa.processes import OpenChoice
from brainvisa.processes import Choice

# soma module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("constel_clusters_from_atlas.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")
    try:
        from constel.lib.utils.filetools import read_nomenclature_file,\
            select_ROI_number
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")


# ---------------------------Header--------------------------------------------


name = "Individual clusters from atlas"
userLevel = 2

signature = Signature(
    # inputs
    "reduced_individual_matrix", ReadDiskItem(
        "Connectivity Matrix", "Aims matrix formats",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "yes",
                            "intersubject": "yes"},
        section="Inputs"),
    "atlas_matrix", ReadDiskItem(
        "Connectivity Matrix", "Aims matrix formats",
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "yes",
                            "intersubject": "yes"},
        section="Atlas inputs"),
    "group_clustering", ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "no",
                            "roi_filtered": "no",
                            "intersubject": "yes",
                            "step_time": "yes",
                            "measure": "no"},
        section="Atlas inputs"),
    "regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File", section="Nomenclature"),
    "region", OpenChoice(section="Study parameters"),
    "individual_regions_parcellation", ReadDiskItem(
        "ROI Texture", "aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"},
        section="Freesurfer data"),

    # outputs
    "individual_clustering", WriteDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "no",
                            "roi_filtered": "no",
                            "intersubject": "yes",
                            "step_time": "yes",
                            "measure": "no"},
        section="Outputs")
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides link of parameters"""

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
            self.region = s[0][1]
            s += read_nomenclature_file(
                self.regions_nomenclature.fullPath(), mode=2)
            self.signature["region"].setChoices(*s)
            if isinstance(self.signature["region"], OpenChoice):
                self.signature["region"] = Choice(*s, section="nomenclature")
                self.changeSignature(self.signature)
            if current not in s:
                self.setValue("region", s[0][1], True)
            else:
                self.setValue("region", current, True)

    self.linkParameters(None,
                        "regions_nomenclature",
                        reset_label)
    self.regions_nomenclature = self.signature[
        "regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})

# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'constel_clusters_from_atlas'.
    """
    from constel.lib.utils.filetools import select_ROI_number

    sup_args = []
    if self.individual_regions_parcellation is not None:
        sup_args.append(self.individual_regions_parcellation)
        # Selects the label number corresponding to label name
        label_number = select_ROI_number(self.regions_nomenclature.fullPath(),
                                         self.region)
        sup_args.append(label_number)

    context.pythonSystem("constel_clusters_from_atlas.py",
                         self.reduced_individual_matrix,
                         self.atlas_matrix,
                         self.group_clustering,
                         self.individual_clustering,
                         *sup_args)
