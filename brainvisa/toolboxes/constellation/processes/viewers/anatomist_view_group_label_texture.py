###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

# Axon python API module
from __future__ import absolute_import
from brainvisa.processes import Signature, ReadDiskItem, Boolean,\
    ValidationError


def validation(self):
    try:
        from brainvisa import anatomist as ana
    except ImportError:
        raise ValidationError(_t_("Anatomist not available"))
    ana.validation()


name = 'Anatomist view Group Label Texture'
userLevel = 2
roles = ('viewer', )

signature = Signature(
    'label_texture', ReadDiskItem('Mask Texture', 'Anatomist texture formats'),
    'mesh', ReadDiskItem("White Mesh", "Anatomist mesh formats"),
    "prefer_inflated_meshes", Boolean(),
)


def initialization(self):
    def link_mesh(self, dummy):
        if self.label_texture is not None:
            mesh_type = self.signature['mesh']
            if self.prefer_inflated_meshes:
                infl1 = 'Yes'
                infl2 = 'No'
            else:
                infl1 = 'No'
                infl2 = 'Yes'
            atts1 = {
                'group_of_subjects':
                    self.label_texture.get('group_of_subjects'),
                'freesurfer_group_of_subjects': self.label_texture.get(
                    'freesurfer_group_of_subjects'),
                'inflated': infl1,
                "side": "both",
                "vertex_corr": "Yes"
            }
            res = mesh_type.findValue(atts1)
            if res is None:
                atts2 = {
                 'group_of_subjects': self.label_texture.get(
                    'freesurfer_group_of_subjects'),
                 'freesurfer_group_of_subjects': self.label_texture.get(
                    'group_of_subjects'),
                 'inflated': infl1,
                 "side": "both",
                 "vertex_corr": "Yes"
                 }
            res = mesh_type.findValue(atts2)
            if res is None:
                atts1['inflated'] = infl2
                res = mesh_type.findValue(atts1)
            if res is None:
                atts2['inflated'] = infl2
                res = mesh_type.findValue(atts2)
            if res is None:
                res = mesh_type.findValue(self.label_texture)
            return res

    self.prefer_inflated_meshes = False
    self.linkParameters('mesh', ['label_texture', 'prefer_inflated_meshes'],
                        link_mesh)


def execution(self, context):
    objs = context.runProcess('AnatomistShowTexture',
                              read=self.label_texture,
                              mesh=self.mesh, palette='random',
                              rgb_interpolation=True)
    return objs
