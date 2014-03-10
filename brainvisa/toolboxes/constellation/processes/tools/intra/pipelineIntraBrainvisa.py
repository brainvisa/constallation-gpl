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

name = 'Constellation within-subject pipeline'
userLevel = 2

signature = Signature(
    'study', Choice('avg', 'concat'),
    'texture', String(),
    'gyrus', String(),
    'database', Choice(),
    'subject', ReadDiskItem('subject', 'directory'),
    'gyri_texture', ReadDiskItem('FreesurferResampledBothParcellationType', 
                                 'Aims texture formats'),
    'white_mesh', ReadDiskItem('AimsBothWhite', 'Aims mesh formats'),
    'smoothing', Float(),
)

def initialization(self):
    databases=[h.name for h in neuroHierarchy.hierarchies() 
               if h.fso.name == 'brainvisa-3.2.0']
    self.signature['database'].setChoices(*databases)
    if len(databases) != 0:
        self.database = databases[0]
    else:
        self.signature['database'] = OpenChoice()
    
    eNode = SerialExecutionNode(self.name, parameterized=self)

    # link of parameters with the "Bundles Filtering" process
    eNode.addChild('Filter',
                   ProcessExecutionNode('bundlesFiltering',
                   optional = 1))

    eNode.addDoubleLink('Filter.study',
                        'study')
    eNode.addDoubleLink('Filter.texture',
                        'texture')
    eNode.addDoubleLink('Filter.gyrus',
                        'gyrus')
    eNode.addDoubleLink('Filter.database',
                        'database')
    eNode.addDoubleLink('Filter.subject',
                        'subject')
    eNode.addDoubleLink('Filter.gyri_texture',
                        'gyri_texture')

    # link of parameters with the "Fiber Oversampled" process
    eNode.addChild('Oversampler',
                   ProcessExecutionNode('fiberOversampler',
                   optional = 1))

    eNode.addDoubleLink('Oversampler.filtered_length_distant_fibers',
                        'Filter.subsets_of_distant_fibers')

    # link of parameters with the "Connectivity Matrix" process
    eNode.addChild('ConnectivityMatrix',
                   ProcessExecutionNode('createConnectivityMatrix',
                   optional = 1))

    eNode.addDoubleLink('ConnectivityMatrix.oversampled_distant_fibers',
                        'Oversampler.oversampled_distant_fibers')
    eNode.addDoubleLink('ConnectivityMatrix.filtered_length_fibers_near_cortex',
                        'Filter.subsets_of_fibers_near_cortex')
    eNode.addDoubleLink('ConnectivityMatrix.gyri_texture',
                        'gyri_texture')
    eNode.addDoubleLink('ConnectivityMatrix.white_mesh',
                        'white_mesh')
    eNode.addDoubleLink('ConnectivityMatrix.dw_to_t1',
                        'Filter.dw_to_t1')

    # link of parameters with the "Sum Sparse Matrix Smoothing" process
    eNode.addChild('Smoothing',
                   ProcessExecutionNode('sumSparseMatrix',
                   optional = 1))

    eNode.addDoubleLink('Smoothing.matrix_of_fibers_near_cortex',
                        'ConnectivityMatrix.matrix_of_fibers_near_cortex')
    eNode.addDoubleLink('Smoothing.white_mesh',
                        'white_mesh')
    eNode.addDoubleLink('Smoothing.gyri_texture',
                        'gyri_texture')
    eNode.addDoubleLink('Smoothing.gyrus',
                        'gyrus')
    eNode.addDoubleLink('Smoothing.smoothing',
                        'smoothing')

    # link of parameters with the "Mean Connectivity Profile" process
    eNode.addChild('MeanProfile',
                   ProcessExecutionNode('createMeanConnectivityProfile',
                   optional = 1))

    eNode.addDoubleLink('MeanProfile.complete_connectivity_matrix',
                        'Smoothing.complete_connectivity_matrix')
    eNode.addDoubleLink('MeanProfile.gyri_texture',
                        'gyri_texture')

    # link of parameters with the "Remove Internal Connections" process
    eNode.addChild('InternalConnections',
                   ProcessExecutionNode('removeInternalConnections',
                   optional = 1))

    eNode.addDoubleLink('InternalConnections.patch_connectivity_profile',
                        'MeanProfile.patch_connectivity_profile')
    eNode.addDoubleLink('InternalConnections.gyri_texture',
                        'gyri_texture')
    eNode.addDoubleLink('InternalConnections.white_mesh',
                        'white_mesh')

    # link of parameters with the "Watershed" process
    eNode.addChild('Watershed',
                   ProcessExecutionNode('watershedReflectingConnectionsToGyrus',
                   optional = 1))

    eNode.addDoubleLink('Watershed.normed_connectivity_profile',
                        'InternalConnections.normed_connectivity_profile')
    eNode.addDoubleLink('Watershed.white_mesh',
                        'white_mesh')

    # link of parameters with the "Filtering Watershed" process
    eNode.addChild('FilteringWatershed',
                    ProcessExecutionNode('filteringWatershed',
                    optional = 1))

    eNode.addDoubleLink('FilteringWatershed.watershed',
                        'Watershed.watershed')
    eNode.addDoubleLink('FilteringWatershed.complete_connectivity_matrix',
                        'MeanProfile.complete_connectivity_matrix')
    eNode.addDoubleLink('FilteringWatershed.gyri_texture',
                        'gyri_texture')
    eNode.addDoubleLink('FilteringWatershed.white_mesh',
                        'white_mesh')

    # link of parameters with the "Reduced Connectivity Matrix" process
    eNode.addChild('ReducedMatrix',
                    ProcessExecutionNode('createReducedConnectivityMatrix',
                    optional = 1))

    eNode.addDoubleLink('ReducedMatrix.complete_connectivity_matrix',
                        'FilteringWatershed.complete_connectivity_matrix')
    eNode.addDoubleLink('ReducedMatrix.gyri_texture',
                        'gyri_texture')
    eNode.addDoubleLink('ReducedMatrix.white_mesh',
                        'white_mesh')

    # link of parameters with the "Clustering" process
    eNode.addChild('ClusteringIntraSubjects',
                    ProcessExecutionNode('ClusteringIntrasubject',
                    optional = 1))

    eNode.addDoubleLink('ClusteringIntraSubjects.reduced_connectivity_matrix',
                        'ReducedMatrix.reduced_connectivity_matrix')
    eNode.addDoubleLink('ClusteringIntraSubjects.gyri_texture',
                        'gyri_texture')
    eNode.addDoubleLink('ClusteringIntraSubjects.white_mesh',
                        'white_mesh')

    self.setExecutionNode(eNode)