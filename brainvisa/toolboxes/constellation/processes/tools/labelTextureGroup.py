#!/usr/bin/env python
from brainvisa.processes import *
from soma.path import find_in_path

def validation():
  try:
    import constel
  except:
    raise ValidationError( 'module constellation is not here.' )


from brainvisa.group_utils import Subject
from soma.minf.api import registerClass, readMinf

name = 'Average Gyri Texture'
userLevel = 2

signature = Signature(
  'group_freesurfer', ReadDiskItem('Freesurfer Group definition', 'XML' ),
  'mesh', ReadDiskItem('BothAverageBrainWhite', 'MESH mesh'),
  'avg_gyri_texture', WriteDiskItem( 'BothAverageResampledGyri', 'BrainVISA texture formats' ),
)

def initialization ( self ):
  self.linkParameters( 'mesh', 'group_freesurfer' )
  self.linkParameters( 'avg_gyri_texture', 'group_freesurfer' )
  
def execution ( self, context ):
  registerClass('minf_2.0', Subject, 'Subject')
  groupOfSubjects = readMinf(self.group_freesurfer.fullPath())

  textures = []
  for subject in groupOfSubjects:
    textures.append( ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ).findValue( subject.attributes() ) )
  context.write(str([i for i in textures]))
  
  cmd_args = []
  for tex in textures:
    cmd_args += [ '-i', tex ]
  cmd_args += [ '-o', self.avg_gyri_texture ]
  context.system('python', find_in_path( 'constelAvgGyriTexture.py' ), *cmd_args )

  # Computing connected component:
  context.system('python', find_in_path( 'constelGyriTextureCleaningIsolatedVertices.py' ),
    '-i', self.avg_gyri_texture,
    '-m', self.mesh,
    '-o', self.avg_gyri_texture
  )
  