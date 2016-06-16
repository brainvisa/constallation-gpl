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
    - the interlinkages between inputs/outputs.
* executes the command 'comistFiberOversampler': the semilabeled fibers are
  oversampled.

Main dependencies: axon python API, soma-base, comist

Author: Sandrine Lefranc, 2015
"""

#----------------------------Imports-------------------------------------------


# axon python API module
from brainvisa.processes import Signature, ReadDiskItem, WriteDiskItem, \
    ValidationError

# soma module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    if not find_in_path("comistFiberOversampler"):  # checks command (C++)
        raise ValidationError(
            "comistFiberOversampler is not contained in PATH environnement "
            "variable. Please make sure that connectomist is installed.")


#----------------------------Header--------------------------------------------


name = "Fiber Oversampler"
userLevel = 2


signature = Signature(
    # --input--
    "semilabeled_fibers", ReadDiskItem(
        "Filtered Fascicles bundles", "Aims readable bundles formats",
        requiredAttributes={"both_ends_labelled": "No", "oversampled": "No"}),

    # --output--
    "oversampled_semilabeled_fibers", WriteDiskItem(
        "Fascicles bundles", "Aims writable bundles formats",
        requiredAttributes={"both_ends_labelled": "No", "oversampled": "Yes"}),
)


#----------------------------Functions-----------------------------------------


def initialization(self):
    """Provides link of parameters for autocompletion.
    """
    self.linkParameters("oversampled_semilabeled_fibers", "semilabeled_fibers")


#----------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'comistFiberOversampler'.

    The fiber tracts with only one end identified on the mesh are oversampled.
    """
    context.system("comistFiberOversampler",
                   "-i", self.semilabeled_fibers,
                   "-o", self.oversampled_semilabeled_fibers,
                   "-points", 3,  # number of pts to intercalate between 2 pts
                   "-verbose", 1)
