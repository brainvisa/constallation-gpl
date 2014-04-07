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

# Constel module
try:
    import constel
except:
    warnings.warn('Please make sure that constel module is installed.' )

name = 'Connectivity Matrix'
userLevel = 2

signature = Signature(
    'oversampled_distant_fibers', ReadDiskItem('Oversampled Fibers', 
                                      'Aims bundles'),
    'filtered_length_fibers_near_cortex', ReadDiskItem('Fibers Near Cortex', 
                                              'Aims bundles'),
    'gyri_texture', ReadDiskItem('FreesurferResampledBothParcellationType', 
                        'Aims texture formats'),
    'white_mesh', ReadDiskItem('AimsBothWhite', 'Aims mesh formats'),
    'dw_to_t1', ReadDiskItem('Transformation matrix', 
                    'Transformation matrix'),
    'patch', Integer(),
    'matrix_of_distant_fibers', WriteDiskItem(
        'Connectivity Matrix Outside Fibers Of Cortex', 
        'Matrix sparse' ),
    'matrix_of_fibers_near_cortex', WriteDiskItem(
        'Connectivity Matrix Fibers Near Cortex', 'Matrix sparse'),
    'profile_of_fibers_near_cortex', WriteDiskItem(
        'Connectivity Profile Fibers Near Cortex', 'Aims texture formats' ),
    'profile_of_distant_fibers', WriteDiskItem(
        'Connectivity Profile Outside Fibers Of Cortex', 
        'Aims texture formats' ),
)

def initialization(self):
    self.linkParameters('filtered_length_fibers_near_cortex', 
                        'oversampled_distant_fibers')
    self.linkParameters('matrix_of_distant_fibers', 
                        'oversampled_distant_fibers')
    self.linkParameters('matrix_of_fibers_near_cortex', 
                        'matrix_of_distant_fibers')
    self.linkParameters('profile_of_distant_fibers', 
                        'oversampled_distant_fibers')
    self.linkParameters('profile_of_fibers_near_cortex', 
                        'profile_of_distant_fibers')
    self.linkParameters('gyri_texture', 'white_mesh')
    
    self.setOptional('patch')

def execution (self, context):
    # provides the patch name
    if self.patch is not None:
        patch = self.patch
    else:
        patch = os.path.basename(os.path.dirname(
            os.path.dirname(self.oversampled_distant_fibers.fullPath())))
        patch = patch.strip('G')
    
    # computes connectivity matrix for distant fibers of cortex
    # one end only of fibers is known
    # this command is mostly concerned with fibers leaving the brain stem
    context.system('constelConnectivityMatrix',
        '-bundles', self.oversampled_distant_fibers,
        '-connmatrix', self.matrix_of_distant_fibers,
        '-matrixcompute', 'meshintersectionpoint', 
        '-dist', 0.0, # no smoothing
        '-wthresh', 0.001,
        '-distmax', 5.0,
        '-seedregionstex', self.gyri_texture,
        '-outconntex', self.profile_of_distant_fibers,
        '-mesh',self. white_mesh,
        '-type', 'seed_mean_connectivity_profile',
        '-trs', self.dw_to_t1,
        '-seedlabel', patch,
        '-normalize', 0,
        '-verbose', 1
    )
  
    # computes connectivity matrix for fibers near cortex
    # both ends of fibers are well known
    context.system('constelConnectivityMatrix',
        '-bundles', self.filtered_length_fibers_near_cortex,    
        '-connmatrix', self.matrix_of_fibers_near_cortex,
        '-dist', 0.0, # no smoothing
        '-seedregionstex', self.gyri_texture,
        '-outconntex', self.profile_of_fibers_near_cortex,
        '-mesh',self. white_mesh,
        '-type', 'seed_mean_connectivity_profile',
        '-trs', self.dw_to_t1,
        '-seedlabel', patch,
        '-normalize', 0,
        '-verbose', 1
    )