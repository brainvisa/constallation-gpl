#!/usr/bin/env python
from brainvisa.processes import *
from soma.path import find_in_path

def validation():
  try:
    import roca
    import constel
  except:
    raise ValidationError( 'module roca or constellation is not here.' )


from brainvisa.group_utils import Subject
from soma.minf.api import registerClass, readMinf

name = '00 - Average Gyri Texture'
userLevel = 2

signature = Signature(
  'group_freesurfer', ReadDiskItem('Freesurfer Group definition', 'XML' ),
  'gyri_textures', ListOf( ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ) ),
  'mesh', ReadDiskItem('BothAverageBrainWhite', 'MESH mesh'),
  'avg_gyri_texture', WriteDiskItem( 'BothAverageResampledGyri', 'BrainVISA texture formats' ),
)

def initialization ( self ):
  self.linkParameters( 'gyri_textures', 'group_freesurfer' )
  self.linkParameters( 'mesh', 'group_freesurfer' )
  self.linkParameters( 'avg_gyri_texture', 'group_freesurfer' )
  
def execution ( self, context ):
  
  registerClass('minf_2.0', Subject, 'Subject')
  groupOfSubjects = readMinf(self.group_freesurfer.fullPath())

  subjects = []
  for subject in groupOfSubjects:
    subjects.append( ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ).findValue( subject.attributes() ) )
  context.write(str([i for i in subjects]))
  
  gyri_textures = []
  for gyri_segmentation in self.gyri_textures:
    gyri_textures.append(gyri_segmentation)

  context.write(str([i for i in gyri_textures]))

  context.system('python', '-m', 'constel.cmd.average_texture_labels', self.avg_gyri_texture.fullPath(), *gyri_textures)

  # Computing connected component:
  context.system('python', find_in_path( 'constelGyriTextureCleaningIsolatedVertices.py' ),
    '-i', self.avg_gyri_texture,
    '-m', self.mesh,
    '-o', self.avg_gyri_texture
  )
  