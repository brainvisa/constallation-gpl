# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path


def validation():
    if not find_in_path('AimsSparseMatrixToDense.py'):
        raise ValidationError('aims module is not here.')

name = 'Convert Sparse Matrix to Dense'
userLevel = 2

signature = Signature(
    'sparse_connectivity_matrix', ReadDiskItem(
        'Gyrus Connectivity Matrix', 'Matrix sparse'),
    'dense_connectivity_matrix', WriteDiskItem(
        'Patch Connectivity Matrix', 'GIS image'))


def initialization(self):
    self.linkParameters(
        'dense_connectivity_matrix', 'sparse_connectivity_matrix')


def execution(self, context):
    context.system('AimsSparseMatrixToDense.py',
                   '-i', self.sparse_connectivity_matrix,
                   '-o', self.dense_connectivity_matrix)