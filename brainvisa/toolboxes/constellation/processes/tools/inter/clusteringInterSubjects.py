# -*- coding: utf-8 -*-
############################################################################
# This software and supporting documentation are distributed by
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the 
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info". 
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
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
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.
############################################################################

# BrainVisa modules
from brainvisa.processes import *
from brainvisa.group_utils import Subject
from soma.minf.api import registerClass, readMinf
from soma.path import find_in_path

# Plot constel module
def validation():
    if not find_in_path('constelInterSubjectClustering.py'):
        raise ValidationError('Please make sure that constel module'
                              'is installed.')

name = 'Clustering of Group'
userLevel = 2

# Argument declaration
signature = Signature(
    'study', Choice('avg', 'concat'), # TO DO: change name (averaged, concatenated)
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
    'reduced_connectivity_matrix', ListOf( 
        ReadDiskItem('Group Reduced Connectivity Matrix', 'GIS image')),
    'gyri_texture', ListOf( 
        ReadDiskItem('FreesurferResampledBothParcellationType', 
                     'Aims texture formats')),
    'average_mesh', ReadDiskItem('BothAverageBrainWhite', 
                                 'BrainVISA mesh formats'),
    'group_matrix', WriteDiskItem('Group Matrix', 'GIS image'),
    'kmax', Integer(),
    #'clustering_time', ListOf(WriteDiskItem('Group Clustering Time', 
                                            #'BrainVISA texture formats')),
)

# Default values
def initialization(self):
    self.study = 'avg'
    self.texture_group = 'fsgroup'
    self.smoothing = 3.0
    self.kmax = 12   
    
    # function of link between group and several individual reduced 
    # connectivity matrix
    def linkIndividual(self, dummy):
        if self.group is not None:
            registerClass('minf_2.0', Subject, 'Subject')
            groupOfSubjects = readMinf(self.group.fullPath())
            profiles = []
            for subject in groupOfSubjects:
                atts = dict(self.group.hierarchyAttributes())
                atts['study'] = self.study
                atts['texture'] = self.texture_group
                atts['gyrus'] = 'G' + str(self.patch_label)
                atts['smoothing'] = 'smooth' + str(self.smoothing)
                profile = ReadDiskItem('Group Reduced Connectivity Matrix', 
                                       'GIS image').findValue(atts, 
                                       subject.attributes())
                if profile is not None:
                    profiles.append(profile)
            return profiles
    
    # function of link between group and group matrix
    def linkMatrix(self, dummy):
        if self.group is not None:
            atts = dict(self.group.hierarchyAttributes())
            atts['study'] = self.study
            atts['texture'] = self.texture_group
            atts['gyrus'] = 'G' + str(self.patch_label)
            atts['smoothing'] = 'smooth' + str(self.smoothing)
            filename = self.signature['group_matrix'].findValue(atts)
            return filename
    
    # function of link between clustering time and individualm reduced 
    # connectivity matrices
    def linkClustering(self, dummy):
        if self.reduced_connectivity_matrix and self.group is not None:
            if self.study == 'avg':
                atts = dict(self.group.hierarchyAttributes())
                atts['subject'] = 'avgSubject'
                atts['study'] = self.study
                atts['texture'] = self.texture_group
                atts['gyrus'] = 'G' + str(self.patch_label)
                atts['smoothing'] = 'smooth' + str(self.smoothing)
                return self.signature['clustering_time'].findValue(atts)
            elif self.study == 'concat':
                registerClass('minf_2.0', Subject, 'Subject')
                groupOfSubjects = readMinf(self.group.fullPath())
                profiles = []
                i = 0
                for subject in groupOfSubjects:
                    atts = dict(self.group.hierarchyAttributes())
                    atts['subject'] = self.reduced_connectivity_matrix[i]
                    atts['study'] = self.study
                    atts['texture'] = self.texture_group
                    atts['gyrus'] = 'G' + str(self.patch_label)
                    atts['smoothing'] = 'smooth' + str(self.smoothing)
                    profiles.append(
                        ReadDiskItem('Group Clustering Time', 
                                     'BrainVISA texture formats').findValue(
                                                                  atts))
                    i += 1
                return profiles
                
    # function of link between group and average_mesh
    def linkMesh(self, dummy):
        if self.group is not None:
            atts = {'freesurfer_group_of_subjects': 
                self.group.get('group_of_subjects')}
            return self.signature['average_mesh'].findValue(atts)
    
    # function of link between group and gyri_texture
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
    self.linkParameters('reduced_connectivity_matrix', 
                        ('group', 'study', 'texture_group', 
                         'patch_label', 'smoothing'), 
                        linkIndividual)                                    
    self.linkParameters('group_matrix', 
                        ('group', 'study', 'texture_group', 
                         'patch_label', 'smoothing'), 
                        linkMatrix)
    #self.linkParameters('clustering_time', 
                        #('group', 'study', 'reduced_connectivity_matrix', 
                         #'texture_group', 'patch_label', 'smoothing'), 
                        #linkClustering)
    self.linkParameters('gyri_texture', ('group', 'study'), linkGyri)
    self.linkParameters('average_mesh', 'group', linkMesh)
    
    # visibility level
    self.signature['texture_group'].userLevel = 2
    self.signature['gyri_texture'].userLevel = 2
    self.signature['reduced_connectivity_matrix'].userLevel = 2
    
def execution(self, context):
    '''
    The gyrus vertices connectivity profiles of all the subjects are 
    concatenated into a big matrix. The clustering is performed with the 
    classical kmedoids algorithm and the Euclidean distance between profiles
    as dissimilarity measure.
    '''
    registerClass('minf_2.0', Subject, 'Subject')
    groupOfSubjects = readMinf(self.group.fullPath())

    # TO DO: put condition for self.patch_label...
    patch_label = os.path.basename( os.path.dirname(
                    os.path.dirname(os.path.dirname( 
                    self.reduced_connectivity_matrix[0].fullPath()))))
    patch_label = patch_label.strip('G')

    # show the reduced connectivity matrices
    context.write(str([i.fullPath() 
        for i in self.reduced_connectivity_matrix]))
        
    # show list of gyri segmentation
    context.write(str([i.fullPath()
        for i in self.gyri_texture]))
    
    args = []
    for x in self.reduced_connectivity_matrix:
        args += ['-m', x]
    args += ['-o', self.group_matrix, '-s', self.study]
    context.system('python', find_in_path('constelCalculateGroupMatrix.py'),
        *args
    )

#    cmd_args = []
#    for t in self.clustering_time:
#        cmd_args += ['-p', t]
#    for y in self.gyri_texture:
#        cmd_args += ['-t', y]
#    cmd_args += ['-m', self.average_mesh, '-l', patch_label, 
#                 '-s', self.study, '-g',self.group_matrix, '-a', self.kmax]
#    context.system('python', find_in_path('constelInterSubjectClustering.py'),
#        *cmd_args
#    )