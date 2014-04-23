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

# System module
import numpy as np

# Plot constel module
def validation():
    try:
        import constel
    except:
        raise ValidationError('Please make sure that constel module'
                              'is installed.')

try :
    from constel.lib.texturetools import remove_labels
except :
    pass
    

name = 'Watershed of Group'
userLevel = 2

signature = Signature(
    'normed_connectivity_profile', ReadDiskItem('Avg Normed Connectivity Profile', 
                                                'Aims texture formats'),
    'average_mesh', ReadDiskItem('BothAverageBrainWhite', 'MESH mesh'),
    'watershed', WriteDiskItem('Avg Watershed Texture', 'Aims texture formats'),
    'filtered_watershed', WriteDiskItem('Avg Filtered Watershed', 
                                        'Aims texture formats'),
)

def initialization(self):
    # function of link between group and average_mesh
    def linkMesh(self, dummy):
        if self.normed_connectivity_profile is not None:
            group = os.path.basename(os.path.dirname(os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.dirname(self.normed_connectivity_profile.fullPath())
                    ))))))
            atts = {'freesurfer_group_of_subjects': group}
            print atts
            return self.signature['average_mesh'].findValue(atts)
    
    # link of parameters
    self.linkParameters('watershed', 'normed_connectivity_profile')
    self.linkParameters('filtered_watershed', 'normed_connectivity_profile')
    self.linkParameters('average_mesh', 'normed_connectivity_profile', linkMesh)

def execution(self, context):
    '''
    A watershed is performed to obtain different patches of interest. 
    These patches correspond to cortex sites with a strong connection 
    to the gyrus.
    '''
    context.system('AimsMeshWatershed.py',
        '-i', self.normed_connectivity_profile,
        '-m', self.average_mesh,
        '-k', 10,
        '-q', 0.05,
        '-z', 'or',
        '-t', 0.05,
        '-o', self.watershed
    )

    # Low connections to gyrus : filtered watershed with "minVertex_nb"
    minVertex_nb = 20
    basins_tex = aims.read(self.watershed.fullPath())
    basinTex_ar = basins_tex[0].arraydata()
    basins_labels = np.unique(basinTex_ar).tolist()
    labelsToRemove_list = []
    for basin_label in basins_labels:
        if np.where(basinTex_ar == basin_label)[0].size < minVertex_nb:
            labelsToRemove_list.append(basin_label)
    filteredBasins = remove_labels(basins_tex, labelsToRemove_list)
    aims.write(filteredBasins, self.filtered_watershed.fullPath())