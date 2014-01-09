from brainvisa.processes import *
from soma import aims
from soma.path import find_in_path

def validation():
  if not find_in_path( 'constelConnectionDensityTexture' ):
    raise ValidationError( 'constellation module is not here.' )

name = 'Reduced Connectivity Matrix'
userLevel = 2

signature = Signature(
  'complete_connectivity_matrix', ReadDiskItem( 'Gyrus Connectivity Matrix', 
                                            'Matrix sparse' ),
  'filtered_watershed', ReadDiskItem( 'Filtered Watershed', 
                                      'Aims texture formats' ),
  'gyri_texture', ReadDiskItem( 'FreesurferResampledBothParcellationType', 
                                'Aims texture formats' ),
  'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
  'gyrus', Integer(),
  'reduced_connectivity_matrix', WriteDiskItem( 'Reduced Connectivity Matrix', 
                                                'GIS image' ),
)

def initialization ( self ):
  self.setOptional( 'gyrus' )
  def linkMatrix(self, dummy):
    if self.complete_connectivity_matrix is not None:
      attrs = dict( self.complete_connectivity_matrix.hierarchyAttributes() )
      attrs['subject'] =  self.complete_connectivity_matrix.get('subject')
      attrs['study'] = self.complete_connectivity_matrix.get('study')
      attrs['texture'] = self.complete_connectivity_matrix.get('texture')
      attrs['gyrus'] = self.complete_connectivity_matrix.get('gyrus')
      attrs['smoothing'] = 'smooth' + str( self.complete_connectivity_matrix.get('smoothing') )
      filename = self.signature['filtered_watershed'].findValue( attrs )
      return filename
  self.linkParameters( 'filtered_watershed', 
                       'complete_connectivity_matrix', linkMatrix )
  self.linkParameters( 'reduced_connectivity_matrix', 'filtered_watershed' )

def execution ( self, context ):
  if self.gyrus is not None:
    gyrus = self.gyrus
  else:
    gyrus = os.path.dirname( os.path.basename( os.path.dirname( 
            os.path.dirname( self.complete_connectivity_matrix.fullPath()))))
    gyrus = gyrus.strip('G')
  context.write('gyrus ', gyrus )
  context.system( 'constelConnectionDensityTexture',
    '-mesh', self.white_mesh,
    '-connmatrixfile', self.complete_connectivity_matrix,
    '-targetregionstex', self.filtered_watershed,
    '-seedregionstex', self.gyri_texture,
    '-seedlabel', gyrus,
    '-type', 'seedVertex_to_targets',
    '-connmatrix', self.reduced_connectivity_matrix,
    '-normalize', 1,
    '-verbose', 1
  )