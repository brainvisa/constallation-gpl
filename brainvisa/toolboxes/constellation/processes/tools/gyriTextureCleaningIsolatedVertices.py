#!/usr/bin/env python
from brainvisa.processes import *
from soma.path import find_in_path


def validation():
    if not find_in_path('constelGyriTextureCleaningIsolatedVertices.py'):
        raise ValidationError('constel module is not here.')

name = 'Cleaning Isolated Vertices'
userLevel = 2

signature = Signature(
    'gyri_texture', ReadDiskItem('BothResampledGyri', 'Aims texture formats'),
    'mesh', ReadDiskItem('AimsBothWhite', 'Aims mesh formats'),
    'clean_gyri_texture', WriteDiskItem('BothResampledGyri',
                                        'Aims texture formats'),)


def initialization(self):
    self.linkParameters('mesh', 'gyri_texture')
    self.linkParameters('clean_gyri_texture', 'gyri_texture')


def execution(self, context):
    context.system('python', find_in_path(
                   'constelGyriTextureCleaningIsolatedVertices.py'),
                   '-i', self.gyri_texture,
                   '-m', self.mesh,
                   '-o', self.clean_gyri_texture)