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

name = 'Freesurfer/Constellation within-subject pipeline'
userLevel = 2

# Argument declaration
signature = Signature(
    "raw_t1_image", ReadDiskItem("Raw T1 MRI", getAllFormats()),
    "study", Choice(
        ("averaged approach", "avg"), ("concatenated approach", "concat")),
    "formats_fiber_tracts", Choice("bundles", "trk"),
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
    'database', Choice(),
    'subject', ReadDiskItem('subject', 'directory'),
    'dw_to_t1', ReadDiskItem('Transformation matrix', 
                             'Transformation matrix'),
    'smoothing', Float(),
)


def initialization(self):
    """Provides default values and link of parameters
    """
     
    # list of possible databases, while respecting the ontology
    # ontology: brainvisa-3.2.0
    databases = [h.name for h in neuroHierarchy.hierarchies() 
                 if h.fso.name == 'brainvisa-3.2.0']
    self.signature['database'].setChoices(*databases)
    if len(databases) != 0:
        self.database=databases[0]
    else:
        self.signature['database'] = OpenChoice()

    # default value
    self.smoothing = 3.0 

    # define the main node of a pipeline
    eNode = SerialExecutionNode(self.name, parameterized=self)
    
    ###########################################################################
    #        link of parameters with the "FreeSurfer" pipeline                #
    ###########################################################################
    eNode.addChild('FreeSurferPipeline',
                   ProcessExecutionNode('freesurferPipelineComplete',
                   optional = 1))  
                    
    eNode.addDoubleLink('FreeSurferPipeline.RawT1Image', 
                        'raw_t1_image')

    ###########################################################################
    #    link of parameters with the "Cleaning Isolated Vertices" process     #
    ###########################################################################
    eNode.addChild('GyriTextureCleaning',
                   ProcessExecutionNode('gyriTextureCleaningIsolatedVertices',
                   optional = 1))

    eNode.addDoubleLink(
        'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatTex.Gyri',
        "GyriTextureCleaning.gyri_texture")

    ###########################################################################
    #    link of parameters with the "Constellation within-subject" pipeline  #
    ###########################################################################
    eNode.addChild("ConstellationIntra",
                   ProcessExecutionNode("pipelineIntraBrainvisa",
                   optional = 1))
    eNode.addDoubleLink("ConstellationIntra.formats_fiber_tracts",
                        "formats_fiber_tracts")
    eNode.addDoubleLink("ConstellationIntra.study",
                        "study")
    eNode.addDoubleLink("ConstellationIntra.segmentation_name_used",
                        "segmentation_name_used")
    eNode.addDoubleLink("ConstellationIntra.patch",
                        "patch")
    eNode.addDoubleLink("ConstellationIntra.new_patch",
                        "new_patch")
    eNode.addDoubleLink("ConstellationIntra.database",
                        "database")
    eNode.addDoubleLink("ConstellationIntra.subject",
                        "subject")
    eNode.addDoubleLink("ConstellationIntra.filter.dw_to_t1",
                        "dw_to_t1")
    eNode.addDoubleLink("ConstellationIntra.smoothing",
                        "smoothing")

    self.setExecutionNode(eNode)
