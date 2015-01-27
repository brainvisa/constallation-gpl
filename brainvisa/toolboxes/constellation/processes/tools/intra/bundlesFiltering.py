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
from soma.path import find_in_path

# System module
import glob


# Plot constel module
def validation():
    """This function is executed at BrainVisa startup when the process is loaded.

    It checks some conditions for the process to be available.
    """
    if not find_in_path("constelBundlesFiltering"):
        raise ValidationError("Please make sure that constel is installed.")


name = "Bundles Filtering"
userLevel = 2


# Arguments declaration
signature = Signature(
    "database", Choice(),
    "formats_fiber_tracts", Choice("bundles", "trk"),
    "study", Choice(("averaged approach", "avg"),
                    ("concatenated approach", "concat")),
    "patch", Choice(
        ("*** use_new_patch ***", 0),
        ("left corpus callosum", 1), ("left bankssts", 2),
        ("left caudal anterior cingulate", 3),
        ("left caudal middle frontal", 4), ("left cuneus", 6),
        ("left entorhinal", 7), ("left fusiform", 8),
        ("left inferior parietal", 9), ("left inferior temporal", 10),
        ("left isthmus cingulate", 11), ("left lateral occipital", 12),
        ("left lateral orbitofrontal", 13), ("left lingual", 14),
        ("left medial orbitofrontal", 15), ("left middle temporal", 16),
        ("left parahippocampal", 17), ("left paracentral", 18),
        ("left pars opercularis", 19), ("left pars orbitalis", 20),
        ("left pars triangularis", 21), ("left pericalcarine", 22),
        ("left postcentral", 23), ("left posterior cingulate", 24),
        ("left precentral", 25), ("left precuneus", 26),
        ("left rostral anterior cingulate", 27),
        ("left rostral middle frontal", 28), ("left superior frontal", 29),
        ("left superior parietal", 30), ("left superior temporal", 31),
        ("left supramarginal", 32), ("left frontal pole", 33),
        ("left temporal pole", 34), ("left transverse temporal", 35),
        ("left insula", 36), ("right corpus callosum", 37),
        ("right bankssts", 38), ("right caudal anterior cingulate", 39),
        ("right caudal middle frontal", 40), ("right cuneus", 42),
        ("right entorhinal", 43), ("right fusiform", 44),
        ("right inferior parietal", 45), ("right inferior temporal", 46),
        ("right isthmus cingulate", 47), ("right lateral occipital", 48),
        ("right lateral orbitofrontal", 49), ("right lingual", 50),
        ("right medial orbitofrontal", 51), ("right middle temporal", 52),
        ("right parahippocampal", 53), ("right paracentral", 54),
        ("right pars opercularis", 55), ("right pars orbitalis", 56),
        ("right pars triangularis", 57), ("right pericalcarine", 58),
        ("right postcentral", 59), ("right posterior cingulate", 60),
        ("right precentral", 61), ("right precuneus", 62),
        ("right rostral anterior cingulate", 63),
        ("right rostral middle frontal", 64), ("right superior frontal", 65),
        ("right superior parietal", 66), ("right superior temporal", 67),
        ("right supramarginal", 68), ("right frontal pole", 69),
        ("right temporal pole", 70), ("right transverse temporal", 71),
        ("right insula", 72)),
    "new_patch", Integer(),
    "segmentation_name_used", String(),
    "subject", ReadDiskItem("subject", "directory"),
    "gyri_texture", ReadDiskItem("Label Texture", "Aims texture formats"),
    "white_mesh", ReadDiskItem("Mesh", "Aims mesh formats"),
    "dw_to_t1", ReadDiskItem("Transformation matrix",
                             "Transformation matrix"),
    "min_length_of_fibers_near_cortex", Float(),
    "max_length_of_fibers_near_cortex", Float(),
    "min_distant_fibers_length", Float(),
    "max_distant_fibers_length", Float(),
    "subsets_of_fibers_near_cortex", WriteDiskItem(
        "Fibers Near Cortex", "Aims writable bundles formats"),
    "subsets_of_distant_fibers", WriteDiskItem(
        "Very OutSide Fibers Of Cortex", "Aims writable bundles formats"),
)


def initialization(self):
    """Provides default values and link of parameters
    """
    # default values
    self.min_length_of_fibers_near_cortex = 30.
    self.max_length_of_fibers_near_cortex = 500.
    self.min_distant_fibers_length = 20.
    self.max_distant_fibers_length = 500.

    # optional parameter
    self.setOptional("new_patch")

    # list of possible databases, while respecting the ontology
    # ontology: brainvisa-3.2.0
    databases = [h.name for h in neuroHierarchy.hierarchies()
                 if h.fso.name == "brainvisa-3.2.0"]
    self.signature["database"].setChoices(*databases)
    if len(databases) != 0:
        self.database = databases[0]
    else:
        self.signature["database"] = OpenChoice()

    def link_filtered_bundles(self, dummy):
        if self.database is not None and self.subject is not None:
            attrs = dict()
            attrs["_database"] = self.database
            attrs["study"] = self.study
            attrs["texture"] = self.segmentation_name_used
            attrs["subject"] = os.path.basename(self.subject.fullPath())
            if self.new_patch is not None:
                attrs["gyrus"] = "G" + str(self.new_patch)
            else:
                attrs["gyrus"] = "G" + str(self.patch)
            attrs["minlengthoffibersIn"] = str(
                int(self.min_length_of_fibers_near_cortex))
            attrs["maxlengthoffibersOut"] = str(
                int(self.max_length_of_fibers_near_cortex))
            filename = self.signature[
                "subsets_of_fibers_near_cortex"].findValue(attrs)
            return filename

    def link_between_filtered_bundles(self, dummy):
        if self.subsets_of_fibers_near_cortex is not None:
            attrs = dict(
                self.subsets_of_fibers_near_cortex.hierarchyAttributes())
            attrs["minlengthoffibersOut"] = str(
                int(self.min_distant_fibers_length))
            attrs["maxlengthoffibersOut"] = str(
                int(self.max_distant_fibers_length))
            filename = self.signature[
                "subsets_of_distant_fibers"].findValue(attrs)
            return filename

    self.linkParameters("subsets_of_fibers_near_cortex", (
        "database", "subject", "study", "segmentation_name_used", "patch",
        "new_patch", "min_length_of_fibers_near_cortex",
        "max_length_of_fibers_near_cortex"), link_filtered_bundles)
    self.linkParameters(
        "subsets_of_distant_fibers", (
            "subsets_of_fibers_near_cortex", "max_distant_fibers_length",
            "min_distant_fibers_length"), link_between_filtered_bundles)
    self.linkParameters("dw_to_t1", "subject")


def load_fiber_tracts(directory, formats):
    """Load all fiber tracts from patterns for one subject.

    Parameters
    ----------
    directory: str (mandatory)
        pattern of fiber tracts files to download
    formats: str (mandatory)
        fiber tracts formats (.bundles or .trk)

    Return
    ------
    fnames: list
        list of bundles files
    """
    if formats == "bundles":
        patterns = [os.path.join(directory, "*.bundles")]
    elif formats == "trk":
        patterns = [os.path.join(directory), "*.trk"]
    fnames = []
    for pattern in patterns:
        fnames.extend(glob.glob(pattern))
    return fnames


def execution(self, context):
    """Run the bundles filtering by giving a min and max length of fibers.
    """
    # Users have the opportunity to force the number of gyrus
    # For this, patch should be "use_new_patch"
    if self.new_patch is not None:
        patch = self.new_patch
    else:
        patch = self.patch

    list_fiber_tracts = load_fiber_tracts(
        self.subject.fullPath(), self.formats_fiber_tracts)

    # name of the command
    cmd = ["constelBundlesFiltering"]

    # options of the command
    for fiber_tract in list_fiber_tracts:
        cmd += ["-i", fiber_tract]
    cmd += [
        "-o", self.subsets_of_fibers_near_cortex,
        "-n", self.subsets_of_distant_fibers,
        "--mesh", self.white_mesh,
        "--tex", self.gyri_texture,
        "--trs", self.dw_to_t1,
        "--mode", "Name1_Name2orNotInMesh",
        "--names", "^" + str(patch) + "_[0-9]+$",
        "--names", "^[0-9]+_" + str(patch) + "$",
        "-g", patch,
        "-r",
        "-l", self.min_length_of_fibers_near_cortex,
        "-L", self.max_length_of_fibers_near_cortex,
        "--nimlmin", self.min_distant_fibers_length,
        "--nimlmax", self.max_distant_fibers_length,
    ]

    # executing the command
    context.system(*cmd)
