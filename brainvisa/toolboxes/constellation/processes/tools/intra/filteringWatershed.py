# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma import aims
import numpy as N

def validation():
  try:
    import constel
  except:
    raise ValidationError( 'module roca is not here.' )

try :
  import constel.lib.texturetools as TT
except :
  pass


name = '13 - Filtering Watershed'
userLevel = 2

signature = Signature(
  'connectivity_matrix_full', ReadDiskItem( 'Gyrus Connectivity Matrix', 'Matrix sparse' ),
                 'watershed', ReadDiskItem( 'Watershed', 'Aims texture formats' ),
         'gyri_segmentation', ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ),
                'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
              'vertex_index', ReadDiskItem( 'Vertex Index', 'Text file' ),
               'patch_label', Integer(),
  
  'watershed_fiber_nb_mesh', WriteDiskItem( 'Gyrus Watershed Bassins Fiber Nb Mesh', 'Aims texture formats' ),
       'watershed_fiber_nb', WriteDiskItem( 'Gyrus Watershed Bassins Fiber Nb', 'Aims texture formats' ),
       'filtered_watershed', WriteDiskItem( 'Filtered Watershed', 'Aims texture formats' ),
)

def initialization ( self ):
  self.setOptional( 'patch_label' )
  self.linkParameters( 'vertex_index','connectivity_matrix_full' )
  self.linkParameters( 'watershed', 'connectivity_matrix_full' )
  self.linkParameters( 'watershed_fiber_nb_mesh', 'connectivity_matrix_full' )
  self.linkParameters( 'watershed_fiber_nb', 'connectivity_matrix_full' )
  self.linkParameters( 'filtered_watershed', 'connectivity_matrix_full' )


def execution ( self, context ):
  context.write( 'The connectivity profiles are reduced according to the patches.' )
  if self.patch_label is not None:
    patch_label = self.patch_label
  else:
    patch_label = os.path.basename( os.path.dirname( os.path.dirname( self.connectivity_matrix_full.fullPath() ) ) )
    patch_label = patch_label.strip('G')
  context.write('patch_label = ', patch_label, '    Is it correct?')
  context.system( 'testConnMatrixToTargetsFromMatrix',
    '-mesh', self.white_mesh,
    '-connfmt', 'binar_sparse', 
    '-connmatrixfile', self.connectivity_matrix_full,
    '-targetregionstex', self.watershed, 
    '-seedregionstex', self.gyri_segmentation,
    '-seedlabel', patch_label,
    '-type', 'oneSeedRegion_to_targets',
    '-outconntex', self.watershed_fiber_nb_mesh,
    '-outconntargets', self.watershed_fiber_nb,
    '-seedvertexindex', self.vertex_index, 
    '-normalize', 1 
  )
  fibersNbByWatershedBasinsTarget_tex = aims.read( self.watershed_fiber_nb.fullPath() )
  subjectWatershedBasins_tex = aims.read( self.watershed.fullPath() )
  
  labelsToRemove_ar = fibersNbByWatershedBasinsTarget_tex[0].arraydata()
  watershedTargets_fibersThreshold = 95
  threshPercent = watershedTargets_fibersThreshold/100.
  labels = labelsToRemove_ar.copy()
  labels_sort = labels.argsort()
  labelsToRemove_list = labelsToRemove_ar.tolist()
  labelsToRemove_list = sorted( labelsToRemove_list, reverse =True )
  labelsToRemove_ar = N.asarray( labelsToRemove_list )
  labelsSort_CumSum = labelsToRemove_ar.cumsum()
  invsort_labelsToRemove = N.where( labelsSort_CumSum > threshPercent )[0]
  invlabels_toRemove = labels.size -1 -invsort_labelsToRemove
  labelsToRemove_ar = labels_sort[invlabels_toRemove]
  labelsToRemove_ar = labelsToRemove_ar + 1
  labelsToRemove_list = labelsToRemove_ar.tolist()
  sup10percentConn_labels = N.where( labels > 0.1 )[0] + 1
  
  for sup10percent_label_i in xrange( sup10percentConn_labels.size ):
    sup10percent_label = sup10percentConn_labels[ sup10percent_label_i ]
    if labelsToRemove_list.count( sup10percent_label ) != 0:
      labelsToRemove_list.remove( sup10percent_label )

  #Min Vertex number checking:
  labelsWithSizeToSmallToRemove_list = []
  for label in labelsWithSizeToSmallToRemove_list:
    if labelsToRemove_list.count( label ) == 0:
      labelsToRemove_list.append( label )
  
  filteredWatershedBasins_tex = TT.removeLabelsFromTexture(
    subjectWatershedBasins_tex,labelsToRemove_list )
  aims.write( filteredWatershedBasins_tex, self.filtered_watershed.fullPath() )
  context.write( 'OK' )
