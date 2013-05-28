from brainvisa.processes import *
from soma import aims
from soma.path import find_in_path

def validation():
  if not find_in_path( 'constelConnectionDensityTexture' ):
    raise ValidationError( 'constellation module is not here.' )

name = '14 - Reduced Connectivity Matrix'
userLevel = 2

signature = Signature(
  'connectivity_matrix_full', ReadDiskItem( 'Gyrus Connectivity Matrix', 'Matrix sparse' ),
        'filtered_watershed', ReadDiskItem( 'Filtered Watershed', 'Aims texture formats' ),
         'gyri_segmentation', ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ),
                'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
              'vertex_index', ReadDiskItem( 'Vertex Index', 'Text file' ),
               'patch_label', Integer(),
  
  'connectivity_matrix_reduced', WriteDiskItem( 'Reduced Connectivity Matrix', 'GIS image' ),
)

def initialization ( self ):
  self.setOptional( 'patch_label' )
  self.linkParameters( 'vertex_index','connectivity_matrix_full')
  self.linkParameters( 'filtered_watershed', 'connectivity_matrix_full' )
  self.linkParameters( 'connectivity_matrix_reduced', 'filtered_watershed' )

def execution ( self, context ):
  context.write( 'For a given cortex region, a dimension reduction of the connectivity matrix is computed, of size (patches number, gyrus vertices number)' )
  if self.patch_label is not None:
    patch_label = self.patch_label
  else:
    patch_label = os.path.basename( os.path.dirname( os.path.dirname( self.connectivity_matrix_full.fullPath() ) ) )
    patch_label = patch_label.strip('G')
  context.write('patch_label = ', patch_label, '    Is it correct?')
  context.system( 'constelConnectionDensityTexture',
    '-mesh', self.white_mesh, 
    '-connfmt', 'binar_sparse',
    '-connmatrixfile', self.connectivity_matrix_full,
    '-targetregionstex', self.filtered_watershed,
    '-seedregionstex', self.gyri_segmentation,
    '-seedlabel', patch_label,
    '-type', 'seedVertex_to_targets',
    '-connmatrix', self.connectivity_matrix_reduced,
    '-seedvertexindex', self.vertex_index,
    '-normalize', 1,
    '-verbose', 1
  )
  context.write( 'OK' )



  
