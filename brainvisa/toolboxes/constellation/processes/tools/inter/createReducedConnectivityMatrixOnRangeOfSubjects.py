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

# BrainVisa module
from brainvisa.processes import *
from soma.path import find_in_path
from brainvisa.group_utils import Subject
from soma.minf.api import registerClass, readMinf
from soma.functiontools import partial

# Plot constel module
def validation():
    if not find_in_path('constelConnectionDensityTexture'):
        raise ValidationError('Please make sure that constel module'
                              'is installed.')

name = 'Reduced Connectivity Matrix'
userLevel = 2

# Argument declaration
signature = Signature(
    'study', Choice('avg', 'concat'), # TO DO: change name (averaged, concatenated)
    'patch_label', Choice( # TO DO: dynamic
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
    'texture_group', String(),
    'smoothing', Float(),
    'group', ReadDiskItem('Group definition', 'XML'),
    'filtered_watershed', ReadDiskItem('Avg Filtered Watershed', 
                                       'Aims texture formats'),
    'complete_connectivity_matrix', ListOf( 
        ReadDiskItem('Gyrus Connectivity Matrix', 'Matrix sparse')),
    'average_mesh', ReadDiskItem('BothAverageBrainWhite', 
                                 'BrainVISA mesh formats'),
    'gyri_texture', ListOf(
        ReadDiskItem('FreesurferResampledBothParcellationType', 
                     'Aims texture formats')),
    'reduced_connectivity_matrix', ListOf(
        WriteDiskItem('Group Reduced Connectivity Matrix','GIS image')),
)

#TO DO: remove this function? 
#def linkGyri(self, key, value):
#    if self.gyri_texture:
#        eNode = self.executionNode()
#        isnode = [x == key for x in eNode.childrenNames()]
#        ind = isnode.index(True)
#        if len(self.gyri_texture) <= ind:
#            ind = len(self.gyri_texture) - 1
#        return self.gyri_texture[ind]

def afterChildAddedCallback(self, parent, key, child):
    # Set default values
    child.removeLink('filtered_watershed', 'complete_connectivity_matrix')
    child.removeLink('reduced_connectivity_matrix', 'filtered_watershed')

    child.signature['filtered_watershed'] = parent.signature[ 'filtered_watershed']
    child.signature['white_mesh'] = parent.signature['average_mesh']
    child.signature['gyri_texture'] = parent.signature['gyri_texture']
    child.signature['reduced_connectivity_matrix'] \
        = WriteDiskItem('Group Reduced Connectivity Matrix', 'GIS image')

    child.gyrus = parent.patch_label
    child.filtered_watershed = parent.filtered_watershed
    child.white_mesh = parent.average_mesh

    ## Add link between eNode.ListOf_Input_3dImage and pNode.Input_3dImage
    parent.addLink(key + '.filtered_watershed', 'filtered_watershed')
    parent.addLink(key + '.patch', 'patch_label')
    parent.addLink(key + '.white_mesh', 'average_mesh')
    parent.addLink(key + '.gyri_texture', 'gyri_texture')
#        partial(self.linkGyri, key))


def beforeChildRemovedCallback(self, parent, key, child):
    parent.removeLink(key + '.filtered_watershed', 'filtered_watershed')
    parent.removeLink(key + '.patch', 'patch_label')
    parent.removeLink(key + '.white_mesh', 'average_mesh')

def initialization (self):
    self.texture_group = 'fsgroup'
    self.smoothing = 3.0
    
    # function of link
    def linkIndividualMatrices(self, dummy):
        if self.group is not None:
            registerClass('minf_2.0', Subject, 'Subject')
            groupOfSubjects = readMinf(self.group.fullPath())
            profiles = []
            for subject in groupOfSubjects:
                atts = dict(self.group.hierarchyAttributes())
                atts['study'] = self.study
                atts['texture'] = 'fs' + os.path.basename(
                                         os.path.dirname(self.group.fullPath()))
                atts['gyrus'] = 'G' + str(self.patch_label)
                atts['smoothing'] = str(self.smoothing)
                profile = ReadDiskItem('Gyrus Connectivity Matrix', 
                                       'Matrix sparse').findValue(atts, 
                                       subject.attributes())
                if profile is not None:
                    profiles.append(profile)
            return profiles

    def linkProfiles(self, dummy):
        if self.complete_connectivity_matrix and self.group is not None:
            profiles = []
            for p in self.complete_connectivity_matrix:
                if p is None:
                    continue
                atts = dict(self.group.hierarchyAttributes())
                atts['study'] = p.get('study')
                atts['texture'] = self.texture_group
                atts['gyrus'] = p.get('gyrus')
                atts['subject'] = p.get('subject')
                atts['smoothing'] = 'smooth' + str(self.smoothing)
                profiles.append(WriteDiskItem('Group Reduced Connectivity Matrix', 
                                              'GIS image').findValue(atts))
            return profiles
            
    def linkWatershed(self, dummy):
        if self.group is not None and self.patch_label and self.texture_group \
            and self.study:
            atts = self.group.hierarchyAttributes()
            atts['texture'] = self.texture_group
            atts['gyrus'] = 'G' + str(self.patch_label)
            atts['study'] = self.study
            atts['smoothing'] = 'smooth' + str(self.smoothing)
            return ReadDiskItem('Avg Filtered Watershed', 
                                'Aims texture formats').findValue(atts)
    def linkMesh(self, dummy):
        if self.group is not None:
            atts = {'freesurfer_group_of_subjects' : 
                    self.group.get('group_of_subjects')}
            return self.signature['average_mesh'].findValue(atts)

    def linkGyri(self, dummy):
        if self.group is not None:
            if self.study == 'avg':
                atts = {'freesurfer_group_of_subjects': 
                    self.group.get('group_of_subjects')}
                return self.signature['gyri_texture'].findValue(atts)
            elif self.study == 'concat':
                registerClass('minf_2.0', Subject, 'Subject')
                groupOfSubjects = readMinf(self.group.fullPath())
                gyrus_segmentation = []
                i = 0
                for subject in groupOfSubjects:
                    g_s = ReadDiskItem('BothResampledGyri', 
                                       'Aims texture formats').findValue(
                                       subject.attributes())
                    gyrus_segmentation.append(g_s)
                    i += 1
                return gyrus_segmentation

    # link of parameters
    self.linkParameters('complete_connectivity_matrix', ('group', 
                        'study', 'patch_label', 
                        'smoothing'), linkIndividualMatrices 
                        )
    self.linkParameters('filtered_watershed', ('group', 'patch_label', 
                        'texture_group', 'study', 'smoothing'), 
                        linkWatershed 
                        )
    self.linkParameters('reduced_connectivity_matrix', 
                        ('complete_connectivity_matrix', 'texture_group', 
                        'group', 'smoothing'), 
                        linkProfiles 
                        )
    self.linkParameters('average_mesh', 'group', linkMesh)
    self.linkParameters('gyri_texture', ('group', 'study'), linkGyri)
    
    # visibility level
    self.signature['complete_connectivity_matrix'].userLevel = 3
    self.signature['reduced_connectivity_matrix'].userLevel = 3
    self.signature['texture_group'].userLevel = 3
    self.signature['gyri_texture'].userLevel = 3

    eNode = ParallelExecutionNode(\
        'Reduced_connectivity_matrix',
        parameterized = self,
        possibleChildrenProcesses = ['createReducedConnectivityMatrix'],
        notify = True)
    eNode = ParallelExecutionNode(\
        'gyri_texture',
        parameterized = self,
        possibleChildrenProcesses = ['createReducedConnectivityMatrix'],
        notify = True)                                
    self.setExecutionNode(eNode)

    # Add callback to warn about child add and remove
    eNode.afterChildAdded.add(\
        ExecutionNode.MethodCallbackProxy(self.afterChildAddedCallback))
    eNode.beforeChildRemoved.add(\
        ExecutionNode.MethodCallbackProxy(self.beforeChildRemovedCallback))
    #eNode.afterChildRemoved.add(\
        #ExecutionNode.MethodCallbackProxy(self.afterChildRemovedCallback))

    # Add links to refresh child nodes when main lists are modified
    eNode.addLink(None,
                  'complete_connectivity_matrix',
                  partial(brainvisa.processes.mapValuesToChildrenParameters,
                          eNode,
                          eNode,
                          'complete_connectivity_matrix',
                          'complete_connectivity_matrix',
                          defaultProcess = 'createReducedConnectivityMatrix',
                          name='createReducedConnectivityMatrix'))

    eNode.addLink(None,
                  'reduced_connectivity_matrix',
                  partial(brainvisa.processes.mapValuesToChildrenParameters,
                          eNode,
                          eNode,
                          'reduced_connectivity_matrix',
                          'reduced_connectivity_matrix',
                          defaultProcess = 'createReducedConnectivityMatrix',
                          name='createReducedConnectivityMatrix'))

    eNode.addLink(None,
                  'gyri_texture',
                  partial(brainvisa.processes.mapValuesToChildrenParameters,
                          eNode,
                          eNode,
                          'gyri_texture',
                          'gyri_texture',
                          defaultProcess = 'createReducedConnectivityMatrix',
                          name='createReducedConnectivityMatrix'))