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
from soma.path import find_in_path

# Plot aims module
def validation():
    if not find_in_path('AimsMeshWatershed.py'):
        raise ValidationError('Please make sure that aims module is installed.')

name = 'Watershed'
userLevel = 2

# Argument declaration
signature = Signature(
    'normed_connectivity_profile', ReadDiskItem('Normed Connectivity Profile', 
                                                'Aims texture formats'),
    'white_mesh', ReadDiskItem('AimsBothWhite', 'Aims mesh formats'),
    'watershed', WriteDiskItem('Watershed Texture', 'Aims texture formats'),
)

# Default values
def initialization(self):
    self.linkParameters('white_mesh', 'normed_connectivity_profile')
    self.linkParameters('watershed', 'normed_connectivity_profile')

def execution(self, context):
    # watershed is computed providing a set of target regions
    commandMeshWatershedProcessing = [sys.executable,
        find_in_path('AimsMeshWatershed.py'),
        '-i', self.normed_connectivity_profile,
        '-m', self.white_mesh,
        '-k', 10,
        '-q', 0.05,
        '-z', 'or',
        '-t', 0.05,
        '-o', self.watershed
    ]
    context.system(*commandMeshWatershedProcessing)