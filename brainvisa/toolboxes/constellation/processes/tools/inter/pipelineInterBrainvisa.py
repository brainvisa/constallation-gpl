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

name = 'Constellation inter-subject pipeline'
userLevel = 2

signature = Signature(
    'study_name', Choice('avg','concat'),
    'texture_ind', String(),
    'texture_group', String(),
    'patch_label', Choice(
        ('left bankssts', 1), ('left caudal anterior cingulate', 2),
        ('left caudal middle frontal', 3), ('left corpus callosum', 4),
        ('left cuneus', 6), ('left entorhinal', 7),
        ('left fusiform', 8), ('left inferior parietal', 9),
        ('left inferior temporal', 10), ('left isthmus cingulate', 11),
        ('left lateral occipital', 12), ('left lateral orbitofrontal', 13),
        ('left lingual', 14), ('left medial orbitofrontal', 15),
        ('left middle temporal', 16), ('left parahippocampal', 17),
        ('left paracentral', 18), ('left pars opercularis', 19),
        ('left pars orbitalis', 20), ('left pars triangularis', 21),
        ('left pericalcarine', 22), ('left postcentral', 23),
        ('left posterior cingulate', 24), ('left precentral', 25),
        ('left precuneus', 26), ('left rostral anterior cingulate', 27),
        ('left rostral middle frontal', 28), ('left superior frontal', 29),
        ('left superior parietal', 30), ('left superior temporal', 31),
        ('left supramarginal', 32), ('left frontal pole', 33),
        ('left temporal pole', 34), ('left transverse temporal', 35),
        ('left insula', 36), 
        ('right bankssts', 37), ('right caudal anterior cingulate', 38), 
        ('rightcaudal middle frontal', 39), ('right corpus callosum', 40), 
        ('right cuneus', 42), ('right entorhinal', 43), 
        ('right fusiform', 44), ('right inferior parietal', 45), 
        ('right inferior temporal', 46), ('right isthmus cingulate', 47), 
        ('right lateral occipital', 48), ('right lateral orbitofrontal', 49), 
        ('right lingual', 50), ('right medial orbitofrontal', 51), 
        ('right middle temporal', 52), ('right parahippocampal', 53), 
        ('right paracentral', 54), ('right pars opercularis', 55), 
        ('right pars orbitalis', 56), ('right pars triangularis', 57), 
        ('right pericalcarine', 58), ('right postcentral', 59), 
        ('right posterior cingulate', 60), ('right precentral', 61), 
        ('right precuneus', 62), ('right rostral anterior cingulate', 63), 
        ('right rostral middle frontal', 64), ('right superior frontal', 65), 
        ('right superior parietal', 66), ('right superior temporal', 67), 
        ('right supramarginal', 68), ('right frontal pole', 69), 
        ('right temporal pole', 70), ('right transverse temporal', 71), 
        ('right insula', 72)
                        ),
    'smoothing', Float(),
    'group', ReadDiskItem('Group definition', 'XML'),
    'average_mesh', ReadDiskItem('BothAverageBrainWhite', 
                                 'BrainVISA mesh formats'),
    'gyri_texture', ListOf(ReadDiskItem('FreesurferResampledBothParcellationType', 
                                        'Aims texture formats')),
)

def linkGroup(self, param1):
  self.smoothing = 3.0
  eNode = self.executionNode()
  for node in eNode.children():
    if node.name() == 'Parallel Node':
      node.addChild('N%d' % len(list(node.children())), ProcessExecutionNode( 'createReducedConnectivityMatrixOnRangeOfSubjects',
                  optional = 1))

def initialization( self ):

  self.addLink( None, 'group', self.linkGroup )
  self.texture_group = 'fsgroup'
  self.smoothing = 3.0
  eNode = SerialExecutionNode( self.name, parameterized=self )

  # link of parameters with teh "Creation of a mask" process
  eNode.addChild('CreateMask',
                 ProcessExecutionNode('surfaceWithEnoughConnectionsCreation',
                 optional = 1))

  eNode.addDoubleLink('CreateMask.study_name',
                      'study_name')
  eNode.addDoubleLink('CreateMask.texture_ind',
                      'texture_ind')
  eNode.addDoubleLink('CreateMask.texture_group',
                      'texture_group')                     
  eNode.addDoubleLink('CreateMask.patch_label',
                      'patch_label')
  eNode.addDoubleLink('CreateMask.smoothing',
                      'smoothing')
  eNode.addDoubleLink('CreateMask.group',
                      'group')

  # link of parameters with the "Connectivity Profile of Group" process
  eNode.addChild('ConnectivityProfileGroup',
                 ProcessExecutionNode('createConnectivityProfileOnRangeOfSubjects',
                 optional = 1))

  eNode.addDoubleLink('ConnectivityProfileGroup.study_name',
                      'study_name')
  eNode.addDoubleLink('ConnectivityProfileGroup.texture_ind',
                      'texture_ind')
  eNode.addDoubleLink('ConnectivityProfileGroup.texture_group',
                      'texture_group')
  eNode.addDoubleLink('ConnectivityProfileGroup.patch_label',
                      'patch_label') 
  eNode.addDoubleLink('ConnectivityProfileGroup.smoothing',
                      'smoothing')
  eNode.addDoubleLink('ConnectivityProfileGroup.group',
                      'group')

  # link of parameters with the "Normed Connectivity Profile of Group" process
  eNode.addChild('NormedProfileGroup',
                 ProcessExecutionNode('removeInternalConnectionsOnRangeOfSubjects',
                 optional = 1))

  eNode.addDoubleLink('NormedProfileGroup.mask',
                      'CreateMask.mask')
  eNode.addDoubleLink('NormedProfileGroup.connectivity_profiles',
                      'ConnectivityProfileGroup.group_connectivity_profile')

  # link of parameters with the "Watershed of Group" process
  eNode.addChild('WatershedGroup',
                 ProcessExecutionNode('filteringWatershedOnRangeOfSubjects',
                 optional = 1))

  eNode.addDoubleLink('WatershedGroup.average_mesh',
                      'average_mesh')
  eNode.addDoubleLink('WatershedGroup.normed_connectivity_profile',
                      'NormedProfileGroup.normed_connectivity_profile')

  # link of parameters with the "Reduced Connectivity Matrix" process
  eNode.addChild('ReducedMatrixGroup',
                 ProcessExecutionNode('createReducedConnectivityMatrixOnRangeOfSubjects',
                 optional = 1))

  eNode.addDoubleLink('ReducedMatrixGroup.study_name',
                      'study_name')
  eNode.addDoubleLink('ReducedMatrixGroup.texture_ind',
                      'texture_ind')
  eNode.addDoubleLink('ReducedMatrixGroup.texture_group',
                      'texture_group')
  eNode.addDoubleLink('ReducedMatrixGroup.patch_label',
                      'patch_label')
  eNode.addDoubleLink('ReducedMatrixGroup.smoothing',
                      'smoothing')                     
  eNode.addDoubleLink('ReducedMatrixGroup.group',
                      'group')
  eNode.addDoubleLink('ReducedMatrixGroup.average_mesh',
                      'average_mesh')
  eNode.addDoubleLink('ReducedMatrixGroup.gyri_texture',
                      'gyri_texture')
  eNode.addDoubleLink('ReducedMatrixGroup.filtered_watershed',
                      'WatershedGroup.filtered_watershed')

  # link of parameters with the "Clustering of Group" process
  eNode.addChild('ClusteringGroup',
                 ProcessExecutionNode('clusteringInterSubjects',
                 optional = 1))

  eNode.addDoubleLink('ClusteringGroup.study_name',
                      'study_name')
  eNode.addDoubleLink('ClusteringGroup.texture_ind',
                      'texture_ind')
  eNode.addDoubleLink('ClusteringGroup.texture_group',
                      'texture_group')
  eNode.addDoubleLink('ClusteringGroup.patch_label',
                      'patch_label')
  eNode.addDoubleLink('ClusteringGroup.smoothing',
                      'smoothing')
  eNode.addDoubleLink('ClusteringGroup.group',
                      'group')
  eNode.addDoubleLink('ClusteringGroup.average_mesh',
                      'average_mesh')
  eNode.addDoubleLink('ClusteringGroup.gyri_texture',
                      'ReducedMatrixGroup.gyri_texture')
  eNode.addDoubleLink('ClusteringGroup.reduced_connectivity_matrix',
                      'ReducedMatrixGroup.reduced_connectivity_matrix')

  self.setExecutionNode(eNode)