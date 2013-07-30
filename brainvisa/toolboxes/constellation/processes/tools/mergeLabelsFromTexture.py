#!/usr/bin/env python
from brainvisa.processes import *
from soma.path import find_in_path

def validation():
  if not find_in_path( 'AimsMergeLabelsFromTexture.py' ):
    raise ValidationError( 'aims module is not here.' )
  if not find_in_path( 'AimsExtractLabelsFromTexture.py'):
    raise ValidationError( 'aims module is not here.' )

name = 'Merge Labels From texture'
userLevel = 2

signature = Signature(
  'gyri_texture', ReadDiskItem( 'FreesurferResampledBothParcellationType', 'Aims texture formats' ),
  'old_label', ListOf( Integer() ),
  'new_label', Integer(),
  'gyri_output_texture', WriteDiskItem( 'FreesurferResampledBothParcellationType', 'Aims texture formats' ),
  'keep_only_merged_regions', Boolean(),
)

def initialization ( self ):
  self.keep_only_merged_regions = False

def execution ( self, context ):
  cmd_args = []
  for ol in self.old_label:
    cmd_args += [ '-l', ol ]
  cmd_args += [ '-i', self.gyri_texture, '-n', self.new_label, '-o', self.gyri_output_texture ]
  if  not self.keep_only_merged_regions:
    context.system( 'python', find_in_path( 'AimsMergeLabelsFromTexture.py' ), *cmd_args )
  else:
    context.system( 'python', find_in_path( 'AimsExtractLabelsFromTexture.py' ), *cmd_args )