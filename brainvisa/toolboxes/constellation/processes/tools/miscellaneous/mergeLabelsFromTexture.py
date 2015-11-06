#!/usr/bin/env python
from brainvisa.processes import *
from soma.path import find_in_path


def validation():
    if not find_in_path('AimsMergeLabelsFromTexture.py'):
        raise ValidationError('aims module is not here.')
    if not find_in_path('AimsExtractLabelsFromTexture.py'):
        raise ValidationError('aims module is not here.')

name = 'Merge Labels From texture'
userLevel = 2

signature = Signature(
    'gyri_texture', ReadDiskItem('ROI Texture', 'Aims texture formats',
                                 requiredAttributes={"side":"both",
                                                     "vertex_corr":"Yes"}),
    'old_labels', ListOf(Integer()),
    'new_label', Integer(),
    'new_gyri_texture', WriteDiskItem('ROI Texture', 'Aims texture formats',
                                      requiredAttributes={"side":"both",
                                                          "vertex_corr":"Yes"}),
    'keep_only_merged_regions', Boolean(),)


def initialization(self):
    self.keep_only_merged_regions = False


def execution(self, context):
    cmd_args = []
    for n in self.old_labels:
        cmd_args += ['-l', n]
    cmd_args += ['-i', self.gyri_texture, '-n', self.new_label,
                 '-o', self.new_gyri_texture]
    if not self.keep_only_merged_regions:
        context.system('python',
                       find_in_path('AimsMergeLabelsFromTexture.py'),
                       *cmd_args)
    else:
        context.system('python',
                       find_in_path('AimsExtractLabelsFromTexture.py'),
                       *cmd_args)
