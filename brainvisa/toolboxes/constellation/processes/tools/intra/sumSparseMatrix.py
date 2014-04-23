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
from soma.path import find_in_path

# Plot aims modules
def validation():
    if not find_in_path('AimsSumSparseMatrix') \
        or not find_in_path('AimsSparseMatrixSmoothing'):
            raise ValidationError('Please make sure that constel module'
                                  'is installed.')

name = 'Smoothing Matrix'
userLevel = 2

# Argument declaration
signature = Signature(
    'matrix_of_fibers_near_cortex', ReadDiskItem(
        'Connectivity Matrix Fibers Near Cortex', 
        'Matrix sparse'),
    'matrix_of_distant_fibers', ReadDiskItem( 
        'Connectivity Matrix Outside Fibers Of Cortex', 
        'Matrix sparse'),
    'gyri_texture', ReadDiskItem('FreesurferResampledBothParcellationType', 
                                 'Aims texture formats'),
    'white_mesh', ReadDiskItem('AimsBothWhite', 'Aims mesh formats'),
    'smoothing', Float(),
    'patch', Integer(),
    'complete_connectivity_matrix', WriteDiskItem('Gyrus Connectivity Matrix', 
                                                  'Matrix sparse'),
)

# Default values
def initialization(self):
    self.smoothing = 3.0
    
    def linkSmooth(self, dummy):
        if self.matrix_of_distant_fibers is not None:
            attrs = dict(self.matrix_of_distant_fibers.hierarchyAttributes())
            attrs['subject'] =  self.matrix_of_distant_fibers.get('subject')
            attrs['study'] = self.matrix_of_distant_fibers.get('study')
            attrs['texture'] = self.matrix_of_distant_fibers.get('texture')
            attrs['patch'] = self.matrix_of_distant_fibers.get('patch')
            attrs['smoothing'] = str(self.smoothing)
            filename = self.signature['complete_connectivity_matrix'].findValue(attrs)
            return filename
  
    self.linkParameters('matrix_of_distant_fibers', 
        'matrix_of_fibers_near_cortex')
    self.linkParameters('complete_connectivity_matrix', 
        ('matrix_of_distant_fibers', 'smoothing'), linkSmooth)
        
    self.setOptional('patch')

def execution (self, context):
    # provides the patch name
    if self.patch is not None:
        patch = self.patch
    else:
        patch = os.path.basename(os.path.dirname( 
            os.path.dirname(self.matrix_of_fibers_near_cortex.fullPath())))
        patch = patch.strip('G')

    # sum of two matrices
    context.system('AimsSumSparseMatrix',
        '-i', self.matrix_of_distant_fibers,
        '-i', self.matrix_of_fibers_near_cortex,
        '-o', self.complete_connectivity_matrix
    )

    # smoothing matrix: -s in millimetres
    context.system('AimsSparseMatrixSmoothing',
        '-i', self.complete_connectivity_matrix,
        '-m', self.white_mesh,
        '-o', self.complete_connectivity_matrix,
        '-s', self.smoothing,
        '-l', self.gyri_texture,
        '-p', patch,
    )