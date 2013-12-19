# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma import aims
import numpy as np

def validation():
  try:
    import constel
  except:
    raise ValidationError( 'constellation module is not here.' )

try :
  import constel.lib.texturetools as TT
except :
  pass
    

name = 'Watershed of Group'
userLevel = 2

signature = Signature(
  'normed_connectivity_profile', ReadDiskItem( 
                                   'Avg Normed Connectivity Profile', 
                                   'Aims texture formats' 
                                 ),
  'average_mesh', ReadDiskItem( 'BothAverageBrainWhite', 'MESH mesh' ),
  'watershed', WriteDiskItem( 'Avg Watershed Texture', 
                              'Aims texture formats' ),
  'filtered_watershed', WriteDiskItem( 'Avg Filtered Watershed', 
                                       'Aims texture formats' ),
)

def initialization ( self ):
  self.linkParameters( 'watershed', 'normed_connectivity_profile' )
  self.linkParameters( 'filtered_watershed', 'normed_connectivity_profile' )

def execution ( self, context ):
  '''
  A watershed is performed to obtain different patches of interest. 
  These patches correspond to cortex sites with a strong connection 
  to the gyrus.
  '''
  context.system( 'AimsMeshWatershed.py',
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
  basins_tex = aims.read( self.watershed.fullPath() )
  basinTex_ar = basins_tex[0].arraydata()
  basins_labels = np.unique(basinTex_ar).tolist()
  labelsToRemove_list = []
  for basin_label in basins_labels:
    if np.where( basinTex_ar == basin_label )[0].size < minVertex_nb:
      labelsToRemove_list.append( basin_label )
  filteredBasins = TT.removeLabelsFromTexture( basins_tex, 
                                               labelsToRemove_list )
  aims.write( filteredBasins, self.filtered_watershed.fullPath() )