#!/usr/bin/env python
###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

"""
This script does the following:
*
*

Main dependencies:

Author: Sandrine Lefranc
"""


#----------------------------Imports-------------------------------------------


# python system module
from brainvisa.processes import ValidationError, Signature, ReadDiskItem, \
    WriteDiskItem
from soma.path import find_in_path


def validation():
    if not find_in_path('constelGyriTextureCleaningIsolatedVertices.py'):
        raise ValidationError('constel module is not here.')


name = 'Cleaning Isolated Vertices'
userLevel = 2


signature = Signature(
    'gyri_texture', ReadDiskItem(
        'ROI Texture', 'Aims texture formats',
        requiredAttributes={"side":"both", "vertex_corr":"Yes"}),
    'mesh', ReadDiskItem(
        'White Mesh', 'Aims mesh formats',
        requiredAttributes={"side":"both", "vertex_corr":"Yes"}),
    'clean_gyri_texture', WriteDiskItem(
        'ROI Texture', 'Aims texture formats',
        requiredAttributes={"side":"both", "vertex_corr":"Yes"}),)


#----------------------------Functions-----------------------------------------


def initialization(self):
    self.linkParameters('mesh', 'gyri_texture')
    self.linkParameters('clean_gyri_texture', 'gyri_texture')


def execution(self, context):
    context.system('python', find_in_path(
                   'constelGyriTextureCleaningIsolatedVertices.py'),
                   '-i', self.gyri_texture,
                   '-m', self.mesh,
                   '-o', self.clean_gyri_texture)
