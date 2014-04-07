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
from soma import aims
from soma.path import find_in_path

# Plot constel module
def validation():
  if not find_in_path('constelConnectionDensityTexture'):
    raise ValidationError('Please make sure that constel module is installed.')

name = 'Reduced Connectivity Matrix'
userLevel = 2

# Argument declaration
signature = Signature(
    'complete_connectivity_matrix', ReadDiskItem('Gyrus Connectivity Matrix', 
                                                 'Matrix sparse'),
    'filtered_watershed', ReadDiskItem('Filtered Watershed', 
                                       'Aims texture formats'),
    'gyri_texture', ReadDiskItem('FreesurferResampledBothParcellationType', 
                                 'Aims texture formats'),
    'white_mesh', ReadDiskItem('AimsBothWhite', 'Aims mesh formats'),
    'patch', Integer(),
    'reduced_connectivity_matrix', WriteDiskItem('Reduced Connectivity Matrix', 
                                                 'GIS image'),
)

# Default value
def initialization(self):
    self.setOptional('patch')
    def linkMatrix(self, dummy):
        if self.complete_connectivity_matrix is not None:
            attrs = dict(self.complete_connectivity_matrix.hierarchyAttributes())
            attrs['subject'] =  self.complete_connectivity_matrix.get('subject')
            attrs['study'] = self.complete_connectivity_matrix.get('study')
            attrs['texture'] = self.complete_connectivity_matrix.get('texture')
            attrs['patch'] = self.complete_connectivity_matrix.get('patch')
            attrs['smoothing'] = 'smooth' + str(self.complete_connectivity_matrix.get('smoothing'))
            filename = self.signature['filtered_watershed'].findValue(attrs)
            return filename
    self.linkParameters('filtered_watershed', 
                        'complete_connectivity_matrix', linkMatrix)
    self.linkParameters('reduced_connectivity_matrix', 'filtered_watershed')

def execution(self, context):
    # provides the patch name
    if self.patch is not None:
        patch = self.patch
    else:
        patch = os.path.dirname(os.path.basename(os.path.dirname( 
                os.path.dirname(self.complete_connectivity_matrix.fullPath()))))
        patch = patch.strip('G')

    # compute reduced connectivity matrix 
    # of size (target regions, cortex vertices)
    context.system('constelConnectionDensityTexture',
        '-mesh', self.white_mesh,
        '-connmatrixfile', self.complete_connectivity_matrix,
        '-targetregionstex', self.filtered_watershed,
        '-seedregionstex', self.gyri_texture,
        '-seedlabel', patch,
        '-type', 'seedVertex_to_targets',
        '-connmatrix', self.reduced_connectivity_matrix,
        '-normalize', 1,
        '-verbose', 1
    )