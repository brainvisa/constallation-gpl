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

# Plot connectomist module
def validation():
    if not find_in_path('comistFiberOversampler'):
        raise ValidationError('Please make sure that connectomist module is installed.')

name = 'Fiber Oversampler'
userLevel = 2

# Argument declaration
signature = Signature(
    'filtered_length_distant_fibers', ReadDiskItem(
        'Very OutSide Fibers Of Cortex', 
        'Aims bundles'),
    'oversampled_distant_fibers', WriteDiskItem('Oversampled Fibers', 
                                                'Aims bundles'),
)

# Default value
def initialization( self ):
    self.linkParameters('oversampled_distant_fibers', 
                        'filtered_length_distant_fibers')

def execution (self, context):
    # fibers tracts are oversampled to attach its end with the cortical 
    # surface
    context.system('comistFiberOversampler',
        '-i', self.filtered_length_distant_fibers,
        '-o', self.oversampled_distant_fibers,
        '-points', 3,
        '-verbose', 1
    )
