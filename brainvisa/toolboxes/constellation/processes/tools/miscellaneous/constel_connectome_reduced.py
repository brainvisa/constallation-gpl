###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

"""
Compute the connectome of a given parcellation.
"""


#----------------------------Imports-------------------------------------------


# axon python API module
from brainvisa.processes import String
from brainvisa.processes import Boolean
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem


#----------------------------Header--------------------------------------------


name = 'Write the connectome of a given parcellation.'
userLevel = 2

signature = Signature(
    # --inputs--
    "subject_gyri_path", ReadDiskItem("directory", "directory"),
    "cortical_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),
    "freesurfer_cortical_parcellation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes"}),
    "cortical_regions_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "freesurfer_nomenclature", ReadDiskItem(
        "Nomenclature ROIs File", "Text File"),
    "freesurfer_regions", Boolean(),
    "aal_regions", Boolean(),
    "constellation_regions", Boolean(),

    # --ouput--
    "reduced_individual_connectome", String(),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters
    """
    # default value
    self.cortical_regions_nomenclature = self.signature[
        "cortical_regions_nomenclature"].findValue(
        {"atlasname": "desikan_freesurfer"})
    self.freesurfer_regions = True
    self.aal_regions = False
    self.constellation_regions = False


#----------------------------Main Program--------------------------------------


def execution(self, context):
    """
    """
    # define the command parameters
    cmd = ["constel_calculate_reduced_connectome.py",
           self.cortical_parcellation,
           self.freesurfer_cortical_parcellation,
           self.subject_gyri_path,
           self.cortical_regions_nomenclature,
           self.freesurfer_nomenclature,
           self.reduced_individual_connectome]

    # optional option
    if self.freesurfer_regions:
        cmd += ["-f"]
    elif self.aal_regions:
        cmd += ["-a"]
    elif self.constellation_regions:
        cmd += ["-c"]

    # execute the command
    context.pythonSystem(*cmd)
