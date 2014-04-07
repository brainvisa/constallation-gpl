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

# Plot aims module
try:
  from soma import aims
  import soma.aims
except:
  warnings.warn('Please make sure that aims module is installed.' )

name = 'Remove Internal Connections'
userLevel = 2

# Argument declaration
signature = Signature(
    'patch_connectivity_profile', ReadDiskItem('Gyrus Connectivity Profile', 
                                               'Aims texture formats'),
    'gyri_texture', ReadDiskItem('FreesurferResampledBothParcellationType', 
                                 'Aims texture formats'),
    'white_mesh', ReadDiskItem('AimsBothWhite', 'Aims mesh formats'),
    'patch', Integer(),
    'normed_connectivity_profile', WriteDiskItem(
         'Normed Connectivity Profile', 
         'Aims texture formats' ),
)

# Default values
def initialization(self):
    self.linkParameters('normed_connectivity_profile', 
                        'patch_connectivity_profile')
                        
    self.setOptional('patch')

def execution(self, context):
    # provides the patch name
    if self.patch is not None:
        patch = self.patch # keep internal connections, put 0
    else:
        patch = os.path.basename(os.path.dirname(os.path.dirname( 
                os.path.dirname(self.patch_connectivity_profile.fullPath()))))
        patch = patch.strip('G')

    # remove internals connections of patch
    mask = aims.read(self.gyri_texture.fullPath())
    pcp = aims.read(self.patch_connectivity_profile.fullPath())
    maskarr =  mask[0].arraydata()
    pcparr = pcp[0].arraydata()
    for i in xrange(pcp[0].nItem()):
        pcparr[maskarr == int(patch)] = 0

    # the profile is normalized
    dividende_coef = pcparr.max()
    if dividende_coef > 0:
        z = 1. / dividende_coef
        pcparr *= z
    aims.write(pcp, self.normed_connectivity_profile.fullPath())