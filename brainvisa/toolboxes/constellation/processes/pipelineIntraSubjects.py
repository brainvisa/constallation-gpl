# -*- coding: utf-8 -*-
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
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security.
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.
############################################################################

from brainvisa.processes import *
from freesurfer.brainvisaFreesurfer import testFreesurferCommand

try:
    import constel
except:
    raise ValidationError('Please make sure that constel module is intalled.')
testFreesurferCommand()

name = 'Freesurfer/Constellation within-subject pipeline'
userLevel = 2

signature = Signature(
    'raw_t1_image', ReadDiskItem('Raw T1 MRI', getAllFormats()),
    'study', Choice('avg', 'concat'),
    'texture', String(),
    'patch', Integer(),
    'database', Choice(),
    'subject', ReadDiskItem('subject', 'directory'),
    'subset_of_tract', ReadDiskItem('Fascicles bundles', 'Aims bundles'),
    'dw_to_t1', ReadDiskItem('Transformation matrix', 
                             'Transformation matrix'),
    'smoothing', Float(),
)

def initialization(self):
    self.smoothing = 3.0  

    databases = [h.name for h in neuroHierarchy.hierarchies() 
                 if h.fso.name == 'brainvisa-3.2.0']
    self.signature['database'].setChoices(*databases)
    if len(databases) != 0:
        self.database=databases[0]
    else:
        self.signature['database'] = OpenChoice()
        
    eNode = SerialExecutionNode(self.name, parameterized=self)
    
############################################################################
# (1) FreeSurfer
############################################################################
    
    # link of parameters with the "FreeSurfer" pipeline
    eNode.addChild('FreeSurferPipeline',
                   ProcessExecutionNode('freesurferPipelineComplete',
                   optional = 1))  
                    
    eNode.addDoubleLink('FreeSurferPipeline.RawT1Image', 
                        'raw_t1_image')

############################################################################
# (2) BrainVisa
############################################################################
                                 
    # link of parameters with the "Cleaning Isolated Vertices" process
    eNode.addChild('GyriTextureCleaning',
                   ProcessExecutionNode('gyriTextureCleaningIsolatedVertices',
                   optional = 1))

    eNode.addDoubleLink('FreeSurferPipeline.FreeSurferPipeline.freesurferConcatTex.Gyri',
                        'GyriTextureCleaning.gyri_texture')

############################################################################
# (3) Constellation
############################################################################                      
                        
    # link of parameters with the "Constellation within-subject" pipeline
    eNode.addChild('ConstellationIntra',
                   ProcessExecutionNode('pipelineIntraBrainvisa',
                   optional = 1))

    eNode.addDoubleLink('ConstellationIntra.study',
                        'study')
    eNode.addDoubleLink('ConstellationIntra.texture',
                        'texture')
    eNode.addDoubleLink('ConstellationIntra.gyrus',
                        'patch')
    eNode.addDoubleLink('ConstellationIntra.database',
                        'database')                     
    eNode.addDoubleLink('ConstellationIntra.subject',
                        'subject')
    eNode.addDoubleLink('ConstellationIntra.Filter.subset_of_tract',
                        'subset_of_tract')
    eNode.addDoubleLink('ConstellationIntra.gyri_texture',
                        'GyriTextureCleaning.gyri_texture_clean')
    eNode.addDoubleLink('ConstellationIntra.white_mesh',
                        'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatenate.BothWhite')
    eNode.addDoubleLink('ConstellationIntra.Filter.dw_to_t1',
                        'dw_to_t1')
    eNode.addDoubleLink('ConstellationIntra.smoothing',
                        'smoothing')

    self.setExecutionNode(eNode)