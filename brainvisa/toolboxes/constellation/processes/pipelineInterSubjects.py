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

try:
   import constel
except:
   raise ValidationError('Please make sure that constel module is installed.')

name = 'Freesurfer/Constellation inter-subject pipeline'
userLevel = 2

signature = Signature(
    'list_of_subjects_FS', ListOf(ReadDiskItem('Subject', 'Directory')),
    'group_FS', ReadDiskItem('Group definition', 'XML'),
    'list_of_subjects_BV', ListOf(ReadDiskItem('Subject', 'Directory')),
    'group_BV', ReadDiskItem('Group definition', 'XML'),
    'study', Choice('avg', 'concat'),
    'patch', Integer(),
    'texture_ind', String(),
    'texture_group', String(),
    'gyri_texture', ListOf(
                    ReadDiskItem('FreesurferResampledBothParcellationType', 
                                 'Aims texture formats')),
)

def initialization(self):

    eNode = SerialExecutionNode(self.name, parameterized=self)

############################################################################
# (1) FreeSurfer
############################################################################

    # link of parameters with the "Creation of a group subject" process
    eNode.addChild('GroupFreesurfer',
                   ProcessExecutionNode('freesurferCreateGroup',
                   optional = 1))

    eNode.addDoubleLink('GroupFreesurfer.list_of_subjects',
                        'list_of_subjects_FS')
    eNode.addDoubleLink('GroupFreesurfer.group_definition',
                        'group_FS')

    # link of parameters with "Average brain mesh" process
    eNode.addChild('AverageBrain',
                   ProcessExecutionNode('freesurferMeanMesh',
                   optional = 1))

    eNode.addDoubleLink('AverageBrain.group',
                        'GroupFreesurfer.group_definition')
    
############################################################################
# (2) BrainVisa
############################################################################

    # link of parameters with "Creation of a group subject" process
    eNode.addChild('GroupBrainvisa',
                   ProcessExecutionNode('createGroup',
                   optional = 1))

    eNode.addDoubleLink('GroupBrainvisa.list_of_subjects',
                        'list_of_subjects_BV')
    eNode.addDoubleLink('GroupBrainvisa.group_definition',
                        'group_BV')
                        
############################################################################
# (3) Constellation
############################################################################

    # link of parameters with the "Constellation Inter Pipeline" pipeline
    eNode.addChild('ConstellationInter',
                   ProcessExecutionNode('pipelineInterBrainvisa',
                   optional = 1))

    eNode.addDoubleLink('ConstellationInter.study_name',
                        'study')
    eNode.addDoubleLink('ConstellationInter.patch_label',
                        'patch')
    eNode.addDoubleLink('ConstellationInter.texture_ind',
                        'texture_ind')
    eNode.addDoubleLink('ConstellationInter.texture_group',
                        'texture_group')
    eNode.addDoubleLink('ConstellationInter.group',
                        'group_BV')
    eNode.addDoubleLink('ConstellationInter.average_mesh',
                        'AverageBrain.BothAverageMesh')                  
    eNode.addDoubleLink('ConstellationInter.ReducedMatrixGroup.gyri_texture',
                        'gyri_texture')

    self.setExecutionNode(eNode)