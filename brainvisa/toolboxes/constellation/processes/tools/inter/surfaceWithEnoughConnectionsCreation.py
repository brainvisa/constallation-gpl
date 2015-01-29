###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

# Axon python API module
from brainvisa.processes import *
from brainvisa.group_utils import Subject

# Soma-base module
from soma.minf.api import registerClass, readMinf
from soma.path import find_in_path


# Plot constel module
def validation():
    """This function is executed at BrainVisa startup when the process is loaded.

    It checks some conditions for the process to be available.
    """
    if not find_in_path("constelConnectivityProfileOverlapMask.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")

name = "Creation of a mask"
userLevel = 2

# Argument declaration
signature = Signature(
    "connectivity_profiles", ListOf(
        ReadDiskItem("Gyrus Connectivity Profile", "Aims texture formats")),
    "group", ReadDiskItem("Group definition", "XML"),
    "mask", WriteDiskItem("Avg Connectivity Mask", "Aims texture formats"), )


def initialization(self):
    """Provides default values and link of parameters
    """

    
    def link_mask(self, dummy):
        """Function of link between mask and group parameters.
        """
        if (self.group and self.connectivity_profiles) is not None:
            atts = dict(self.connectivity_profiles[0].hierarchyAttributes())
            atts["group_of_subjects"] = os.path.basename(
                os.path.dirname(self.group.fullPath()))
            return self.signature["mask"].findValue(atts)

    self.linkParameters("mask", ("connectivity_profiles", "group"), link_mask)


def execution(self, context):

    args = []
    for x in self.connectivity_profiles:
        args += ["-p", x]
    args += ["-o", self.mask]
    context.system(sys.executable,
                   find_in_path("constelConnectivityProfileOverlapMask.py"),
                   *args)
