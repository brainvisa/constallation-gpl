# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma import aims
import numpy as N

def validation():
  try:
    import constel
  except:
    raise ValidationError( 'constellation module is not here.' )
try :
  import constel.lib.texturetools as TT
except :
  pass

name = 'Filtering Watershed'
userLevel = 2

signature = Signature(
  'complete_connectivity_matrix', ReadDiskItem( 'Gyrus Connectivity Matrix', 
                                                'Matrix sparse' ),
  'watershed', ReadDiskItem( 'Watershed Texture', 'Aims texture formats' ),
  'gyri_texture', ReadDiskItem( 'FreesurferResampledBothParcellationType', 
                                'Aims texture formats' ),
  'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
  'gyrus', Integer(),
  'sum_vertices_patch', WriteDiskItem( 'Sum Values From Region', 
                                       'Aims texture formats' ),
  'duplication_value_patch', WriteDiskItem( 'Spread Value On Region', 
                                            'Aims texture formats' ),
  'filtered_watershed', WriteDiskItem( 'Filtered Watershed', 
                                       'Aims texture formats' ),
)

def initialization ( self ):
  self.setOptional( 'gyrus' )
  def linkWat(self, dummy):
    if self.complete_connectivity_matrix is not None:
      attrs = dict( self.complete_connectivity_matrix.hierarchyAttributes() )
      attrs['subject'] =  self.complete_connectivity_matrix.get('subject')
      attrs['study'] = self.complete_connectivity_matrix.get('study')
      attrs['texture'] = self.complete_connectivity_matrix.get('texture')
      attrs['gyrus'] = self.complete_connectivity_matrix.get('gyrus')
      attrs['smoothing'] = 'smoothing' + str( attrs['smoothing'] )
      print 'atts', attrs
      filename = self.signature['watershed'].findValue( attrs )
      print filename
      return filename
  self.linkParameters( 'watershed', 'complete_connectivity_matrix' , linkWat )
  self.linkParameters( 'sum_vertices_patch', 'complete_connectivity_matrix' )
  self.linkParameters( 'duplication_value_patch', 
                       'complete_connectivity_matrix' )
  self.linkParameters( 'filtered_watershed', 'complete_connectivity_matrix' )


def execution ( self, context ):
  if self.gyrus is not None:
    gyrus = self.gyrus
  else:
    gyrus = os.path.dirname( os.path.basename( os.path.dirname( 
            os.path.dirname( self.complete_connectivity_matrix.fullPath() ))))
    gyrus = gyrus.strip('G')
  context.write('gyrus ', gyrus )
  context.system( 'constelConnectionDensityTexture',
    '-mesh', self.white_mesh,
    '-connmatrixfile', self.complete_connectivity_matrix,
    '-targetregionstex', self.watershed, 
    '-seedregionstex', self.gyri_texture,
    '-seedlabel', gyrus,
    '-type', 'oneSeedRegion_to_targets',
    '-outconntex', self.sum_vertices_patch,
    '-outconntargets', self.duplication_value_patch,
    '-normalize', 1 
  )
  fibersNbByWatershedBasinsTarget_tex = aims.read( 
                                        self.duplication_value_patch.fullPath() )
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