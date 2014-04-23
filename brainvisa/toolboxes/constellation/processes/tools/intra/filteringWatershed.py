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

# BrainVisa modules
from brainvisa.processes import *
from soma import aims

# Sytem module
import numpy as np
import warnings

# Plot constel modules
try:
    import constel
    import constel.lib.texturetools as tt
except:
    warnings.warn('Please make sure that constellation module is installed.')

name = 'Filtering Watershed'
userLevel = 2

# Argument declaration
signature = Signature(
    'complete_connectivity_matrix', ReadDiskItem('Gyrus Connectivity Matrix', 
                                                 'Matrix sparse'),
    'watershed', ReadDiskItem('Watershed Texture', 'Aims texture formats'),
    'gyri_texture', ReadDiskItem('FreesurferResampledBothParcellationType', 
                                 'Aims texture formats'),
    'white_mesh', ReadDiskItem('AimsBothWhite', 'Aims mesh formats'),
    'patch', Integer(),
    'sum_vertices_patch', WriteDiskItem('Sum Values From Region', 
                                        'Aims texture formats'),
    'duplication_value_patch', WriteDiskItem('Spread Value On Region', 
                                             'Aims texture formats'),
    'filtered_watershed', WriteDiskItem('Filtered Watershed', 
                                        'Aims texture formats'),
)

# Default values
def initialization(self):
    self.setOptional('patch')
    def linkWat(self, dummy):
        if self.complete_connectivity_matrix is not None:
            attrs = dict(self.complete_connectivity_matrix.hierarchyAttributes())
            attrs['subject'] =  self.complete_connectivity_matrix.get('subject')
            attrs['study'] = self.complete_connectivity_matrix.get('study')
            attrs['texture'] = self.complete_connectivity_matrix.get('texture')
            attrs['patch'] = self.complete_connectivity_matrix.get('patch')
            attrs['smoothing'] = 'smooth' + str(self.complete_connectivity_matrix.get('smoothing'))
            filename = self.signature['watershed'].findValue(attrs)
            return filename
    self.linkParameters('watershed', 'complete_connectivity_matrix', linkWat)
    self.linkParameters('sum_vertices_patch', 'complete_connectivity_matrix')
    self.linkParameters('duplication_value_patch', 
                        'complete_connectivity_matrix')
    self.linkParameters('filtered_watershed', 'complete_connectivity_matrix')

def execution(self, context):
    if self.patch is not None:
        patch = self.patch
    else:
        patch = os.path.dirname(os.path.basename(os.path.dirname(
                os.path.dirname(self.complete_connectivity_matrix.fullPath()))))
        patch = patch.strip('G')
    
    # compute reduced connectivity matrix
    context.system('constelConnectionDensityTexture',
        '-mesh', self.white_mesh,
        '-connmatrixfile', self.complete_connectivity_matrix,
        '-targetregionstex', self.watershed, 
        '-seedregionstex', self.gyri_texture,
        '-seedlabel', patch,
        '-type', 'oneSeedRegion_to_targets',
        '-outconntex', self.sum_vertices_patch,
        '-outconntargets', self.duplication_value_patch,
        '-normalize', 1 
    )
    fibersNbByWatershedBasinsTarget_tex = aims.read( 
        self.duplication_value_patch.fullPath())
    subjectWatershedBasins_tex = aims.read(self.watershed.fullPath())
    
    # TO DO: assorted improvements (line 113-142)???? (it is not clear yet...)
    labelsToRemove_ar = fibersNbByWatershedBasinsTarget_tex[0].arraydata()
    watershedTargets_fibersThreshold = 95
    threshPercent = watershedTargets_fibersThreshold / 100.
    labels = labelsToRemove_ar.copy()
    labels_sort = labels.argsort()
    labelsToRemove_list = labelsToRemove_ar.tolist()
    labelsToRemove_list = sorted(labelsToRemove_list, reverse =True)
    labelsToRemove_ar = np.asarray(labelsToRemove_list)
    labelsSort_CumSum = labelsToRemove_ar.cumsum()
    invsort_labelsToRemove = np.where(labelsSort_CumSum > threshPercent)[0]
    invlabels_toRemove = labels.size -1 - invsort_labelsToRemove
    labelsToRemove_ar = labels_sort[invlabels_toRemove]
    labelsToRemove_ar = labelsToRemove_ar + 1
    labelsToRemove_list = labelsToRemove_ar.tolist()
    sup10percentConn_labels = np.where(labels > 0.1 )[0] + 1
  
    for sup10percent_label_i in xrange(sup10percentConn_labels.size):
        sup10percent_label = sup10percentConn_labels[sup10percent_label_i]
        if labelsToRemove_list.count(sup10percent_label) != 0:
            labelsToRemove_list.remove(sup10percent_label)

    #Min Vertex number checking:
    labelsWithSizeToSmallToRemove_list = []
    for label in labelsWithSizeToSmallToRemove_list:
        if labelsToRemove_list.count(label) == 0:
            labelsToRemove_list.append(label)
    
    filteredWatershedBasins_tex = tt.remove_labels(
        subjectWatershedBasins_tex,labelsToRemove_list)
    aims.write(filteredWatershedBasins_tex, self.filtered_watershed.fullPath())