###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

# Axon python API module
from brainvisa.processes import *
# Anatomist
from brainvisa import anatomist

name = 'Anatomist view Connectivity Texture'
userLevel = 0
roles = ('viewer', )

signature = Signature(
    'connectivity_texture', ReadDiskItem(
        'Connectivity Profile Texture', 'aims texture formats'),
    'mesh', ReadDiskItem("White Mesh", "Aims mesh formats",
                         requiredAttributes={"side": "both",
                                             "vertex_corr": "Yes"}),
)

def initialization(self):
    def link_mesh(self, dummy):
        if self.connectivity_texture is not None:
            res = self.signature['mesh'].findValue(
                self.connectivity_texture,
                requiredAttributes={'inflated': 'Yes'})
            if res is None:
                res = self.signature['mesh'].findValue(
                    self.connectivity_texture,
                    requiredAttributes={'inflated': 'No'})
            return res

    self.linkParameters('mesh', 'connectivity_texture', link_mesh)


def execution(self, context):
    objs = context.runProcess('AnatomistShowTexture',
                              read=self.connectivity_texture,
                              mesh=self.mesh, palette='white_blue_red')
    texture = objs['texture']
    texture.setPalette(maxVal=0.3)
    return objs
