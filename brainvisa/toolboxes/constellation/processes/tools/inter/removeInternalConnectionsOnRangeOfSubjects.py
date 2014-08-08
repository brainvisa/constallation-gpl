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

# Plot constel module
def validation():
    try:
        import soma.aims
    except:
        raise ValidationError('Please make sure that aims module is installed.')

name = 'Normed Connectivity Profile of Group'
userLevel = 2

# Argument declaration
signature = Signature(
    'mask', ReadDiskItem('Avg Connectivity Mask', 'Aims texture formats'),
    'connectivity_profiles', ReadDiskItem('Avg Connectivity Profile', 
                                          'Aims texture formats'),
    'thresholded_connectivity_profile', WriteDiskItem( 
                                            'Avg Thresholded Connectivity Profile', 
                                            'Aims texture formats' 
                                        ),
    'normed_connectivity_profile', WriteDiskItem( 
                                       'Avg Normed Connectivity Profile', 
                                       'Aims texture formats' 
                                       ),
)

# Default values
def initialization(self):
    self.linkParameters('connectivity_profiles', 'mask')
    self.linkParameters('thresholded_connectivity_profile', 
                        'connectivity_profiles')
    self.linkParameters('normed_connectivity_profile',
                        'thresholded_connectivity_profile')

def execution(self, context):

    mask = aims.read( self.mask.fullPath())
    meanConnectivityProfileTex = aims.read(self.connectivity_profiles.fullPath())
    for i in xrange(meanConnectivityProfileTex[0].nItem()):
        if mask[0][i] == 0:
            meanConnectivityProfileTex[0][i] = 0
    aims.write(meanConnectivityProfileTex, 
                self.thresholded_connectivity_profile.fullPath())
    
    tex = aims.read(self.thresholded_connectivity_profile.fullPath())
    tex_ar = tex[0].arraydata()
    max_connections_nb = tex_ar.max()
    if max_connections_nb > 0:
        z = 1./max_connections_nb
        for i in xrange(tex[0].nItem()):
            value = tex[0][i]
            tex[0][i]= z*value
    aims.write(tex, self.normed_connectivity_profile.fullPath())