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

# Axon python API modules
from brainvisa.processes import *
from soma.path import find_in_path


# Plot constel module
def validation():
    """This function is executed at BrainVisa startup when the process is loaded.

    It checks some conditions for the process to be available.
    """
    if not find_in_path("constelIntraSubjectClustering.py"):
        raise ValidationError(
            "Please make sure that constel module is installed.")

name = "Clustering"
userLevel = 2

# Argument declaration
signature = Signature(
    "reduced_connectivity_matrix", ReadDiskItem(
        "Reduced Connectivity Matrix", "GIS image"),
    "gyri_texture", ReadDiskItem("Label Texture", "Aims texture formats"),
    "white_mesh", ReadDiskItem("Mesh", "Aims mesh formats"),
    "patch", Integer(),
    "kmax", Integer(),
    "clustering_time", WriteDiskItem(
        "Clustering Time", "Aims texture formats"),
)


def initialization(self):
    """Provides default values and link of parameters
    """
    self.kmax = 12
    self.setOptional("patch")
    self.linkParameters("clustering_time", "reduced_connectivity_matrix")
    self.linkParameters("gyri_texture", "white_mesh")


def execution(self, context):
    """Reduced connectivity matrix is clustered using the kmedoids algorithm
    """
    # provides the patch name
    if self.patch is not None:
        patch = self.patch  # keep internal connections, put 0
    else:
        patch = os.path.basename(os.path.dirname(os.path.dirname(
            os.path.dirname(self.reduced_connectivity_matrix.fullPath()))))
        patch = patch.strip("G")

    context.system(sys.executable,
                   find_in_path("constelIntraSubjectClustering.py"),
                   "-m", self.reduced_connectivity_matrix,
                   "-p", patch,
                   "-g", self.gyri_texture,
                   "-w", self.white_mesh,
                   "-a", self.kmax,
                   "-t", self.clustering_time)