###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################


# ---------------------------Imports-------------------------------------------


# Axon python API module
from __future__ import absolute_import
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError

# Soma module
from soma.path import find_in_path


def validation():
    """This function is executed at BrainVisa startup when the process is
    loaded. It checks some conditions for the process to be available.
    """
    cmd = "AimsFiberOversampler"
    if not find_in_path(cmd):
        raise ValidationError(
            "'{0}' is not contained in PATH environnement variable. Please "
            "make sure that AIMS library C++ is installed.".format(cmd))


# ---------------------------Header--------------------------------------------


name = "Fiber Oversampler"
userLevel = 2


signature = Signature(
    # --input--
    "semilabeled_fibers", ReadDiskItem(
        "Filtered Fascicles bundles", "Aims readable bundles formats",
        requiredAttributes={"ends_labelled": "one",
                            "oversampled": "no"},
        section="Filtered tracts"),

    # --output--
    "oversampled_semilabeled_fibers", WriteDiskItem(
        "Filtered Fascicles bundles", "Aims writable bundles formats",
        requiredAttributes={"ends_labelled": "one",
                            "oversampled": "yes"},
        section="Oversampled filtered tracts"),
)


# ---------------------------Functions-----------------------------------------


def initialization(self):
    """Provides link of parameters for autocompletion.
    """
    self.linkParameters("oversampled_semilabeled_fibers",
                        "semilabeled_fibers")


# ---------------------------Main program--------------------------------------


def execution(self, context):
    """Run the command 'AimsFiberOversampler'.

    The fiber tracts with only one end identified on the mesh are oversampled.
    """
    context.system("AimsFiberOversampler",
                   "-i", self.semilabeled_fibers,
                   "-o", self.oversampled_semilabeled_fibers,
                   "-points", 3,  # number of pts to intercalate between 2 pts
                   "-verbose", 1)
