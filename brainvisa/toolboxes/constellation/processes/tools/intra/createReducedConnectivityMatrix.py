from brainvisa.processes import *
from soma import aims
from soma.path import find_in_path

def validation():
  if not find_in_path( 'constelConnectionDensityTexture' ):
    raise ValidationError( 'constellation module is not here.' )

name = 'Reduced Connectivity Matrix'
userLevel = 2

signature = Signature(
  'connectivity_matrix_full', ReadDiskItem( 'Gyrus Connectivity Matrix', 'Matrix sparse' ),
        'filtered_watershed', ReadDiskItem( 'Filtered Watershed', 'Aims texture formats' ),
              'gyri_texture', ReadDiskItem( 'FreesurferResampledBothParcellationType', 'Aims texture formats' ),
                'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
                     'gyrus', Integer(),
  
  'connectivity_matrix_reduced', WriteDiskItem( 'Reduced Connectivity Matrix', 'GIS image' ),
)

def initialization ( self ):
  self.setOptional( 'gyrus' )
  def linkMatrix(self, dummy):
    if self.connectivity_matrix_full is not None:
      attrs = dict( self.connectivity_matrix_full.hierarchyAttributes() )
      attrs['subject'] =  self.connectivity_matrix_full.get('subject')
      attrs['study'] = self.connectivity_matrix_full.get('study')
      attrs['texture'] = self.connectivity_matrix_full.get('texture')
      attrs['gyrus'] = self.connectivity_matrix_full.get('gyrus')
      attrs['smooth'] = 'smooth' + str( self.connectivity_matrix_full.get('smooth') )
      print 'atts', attrs
      filename = self.signature['filtered_watershed'].findValue( attrs )
      print filename
      return filename
  self.linkParameters( 'filtered_watershed', 'connectivity_matrix_full', linkMatrix )
  self.linkParameters( 'connectivity_matrix_reduced', 'filtered_watershed' )

def execution ( self, context ):
  context.write( 'For a given cortex region, a dimension reduction of the connectivity matrix is computed, of size (patches number, gyrus vertices number)' )
  if self.gyrus is not None:
    gyrus = self.gyrus
  else:
    gyrus = os.path.dirname( os.path.basename( os.path.dirname( os.path.dirname( self.connectivity_matrix_full.fullPath() ) ) ) )
    gyrus = gyrus.strip('G')
  context.write('gyrus = ', gyrus, '    Is it correct?')
  context.system( 'constelConnectionDensityTexture',
    '-mesh', self.white_mesh,
    '-connmatrixfile', self.connectivity_matrix_full,
    '-targetregionstex', self.filtered_watershed,
    '-seedregionstex', self.gyri_texture,
    '-seedlabel', gyrus,
    '-type', 'seedVertex_to_targets',
    '-connmatrix', self.connectivity_matrix_reduced,
    '-normalize', 1,
    '-verbose', 1
  )
  context.write( 'OK' )



  
