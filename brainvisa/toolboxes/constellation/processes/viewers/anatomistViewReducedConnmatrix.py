############################################################################
# This software and supporting documentation are distributed by
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
############################################################################
from brainvisa.processes import *
try:
    from brainvisa import anatomist as ana
except:
    pass

def validation():
    try:
        from brainvisa import anatomist as ana
    except:
        raise ValidationError(_t_('Anatomist not available'))


name = 'Anatomist view reduced connectivity matrix'
roles = ('viewer', )
userLevel = 0

signature = Signature(
    'connectivity_matrix',
        ReadDiskItem('Group Reduced connectivity matrix', 
            'aims readable volume formats'),
    'white_mesh', ReadDiskItem('FreesurferMesh', 'anatomist mesh formats'),
    'gyrus_texture', 
        ReadDiskItem('Label texture', 'anatomist texture formats'),
    'basins_texture',
        ReadDiskItem('Label texture', 'anatomist texture formats'), )


def initialization(self):
    self.linkParameters('white_mesh', 'connectivity_matrix')
    self.linkParameters('gyrus_texture', 'connectivity_matrix')
    self.linkParameters('basins_texture', 'connectivity_matrix')


def execution(self, context):
    a = ana.Anatomist()
    mesh = a.loadObject(self.white_mesh)
    patch = a.loadObject(self.gyrus_texture)
    sparse = a.loadObject(self.connectivity_matrix)
    basins = a.loadObject(self.basins_texture)
    conn = a.fusionObjects(
        [mesh, patch, sparse, basins], method='ConnectivityMatrixFusionMethod')
    if conn is None:
        raise ValueError(
            'could not fusion objects - matrix, mesh and ' \
            'labels texture may not correspond.')
    win = a.createWindow('3D')
    a.execute('WindowConfig', windows=[win], light={'background' : [0.,0.,0.,0.]})
    win.addObjects(conn)
    win.setControl('ConnectivityMatrixControl')

    return [win, conn, basins]
