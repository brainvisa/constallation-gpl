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

# ---------------------------Imports-------------------------------------------


def validation(self):
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """

# ---------------------------Header--------------------------------------------


name = "Constellation Cleaner"
userLevel = 1

signature = Signature(
    # --inputs
    "original_texture", ReadDiskItem("Connectivity ROI Texture",
                                     "Aims texture formats"),

    # outputs
    "cleaned_texture", WriteDiskItem("Connectivity ROI Texture",
                                     "Aims texture formats")
)

# ---------------------------Functions-----------------------------------------


def initialization(self):
    """
    """

    def link_cleaned_texture(self, dummy):
        """
        """
        if self.original_texture:
            ext = os.path.splitext(self.original_texture.fullPath())[1]
            filename = self.original_texture.fullName() + '_cleaned' + ext
            return filename

    self.linkParameters("cleaned_texture",
                        "original_texture",
                        link_cleaned_texture)


def execution(self, context):
    """Run the command 'constel_clean_texture.py'.
    """

    cmd = ["constel_clean_texture.py",
           self.original_texture,
           self.cleaned_texture]

    context.pythonSystem(*cmd)
