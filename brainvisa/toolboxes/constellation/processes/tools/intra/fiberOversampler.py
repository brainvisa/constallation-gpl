############################################################################
#  This software and supporting documentation are distributed by
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
############################################################################

# Axon python API module
from brainvisa.processes import *
from soma.path import find_in_path


# Plot connectomist module
def validation():
    """This function is executed at BrainVisa startup when the process is loaded.

    It checks some conditions for the process to be available.
    """
    if not find_in_path("comistFiberOversampler"):
        raise ValidationError(
            "Please make sure that connectomist module is installed.")

name = "Fiber Oversampler"
userLevel = 2


# Argument declaration
signature = Signature(
    "filtered_length_distant_fibers", ReadDiskItem(
        "Very OutSide Fibers Of Cortex", "Aims readable bundles formats"),
    "oversampled_distant_fibers", WriteDiskItem(
        "Oversampled Fibers", "Aims writable bundles formats"),
)


def initialization(self):
    self.linkParameters(
        "oversampled_distant_fibers", "filtered_length_distant_fibers")


def execution(self, context):
    """Run the oversampling on fibers with one end only identified
    """
    context.system("comistFiberOversampler",
                   "-i", self.filtered_length_distant_fibers,
                   "-o", self.oversampled_distant_fibers,
                   "-points", 3,  # number of pts to intercalate between 2 pts
                   "-verbose", 1)