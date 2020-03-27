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
from brainvisa.processes import Signature, ReadDiskItem, Boolean


def validation(self):
    try:
        from brainvisa import anatomist as ana
    except ImportError:
        raise ValudationError(_t_("Anatomist not available"))
    ana.validation()


name = 'Anatomist view Connectivity ROI Texture'
userLevel = 2
roles = ('viewer', )

signature = Signature(
    'connectivity_roi_texture', ReadDiskItem(
        'Connectivity ROI Texture', 'aims texture formats'),
    'mesh', ReadDiskItem("White Mesh", "Aims mesh formats",
                         requiredAttributes={"side": "both",
                                             "vertex_corr": "Yes"}),
    "prefer_inflated_meshes", Boolean(),
)


def initialization(self):
    def link_mesh(self, dummy):
        if self.connectivity_roi_texture is not None:
            ct = self.connectivity_roi_texture
            if self.prefer_inflated_meshes:
                infl1 = 'Yes'
                infl2 = 'No'
            else:
                infl1 = 'No'
                infl2 = 'Yes'
            mesh_type = self.signature['mesh']
            if ct.get('group_of_subjects') is not None:
                atts1 = {
                    'group_of_subjects':
                        ct.get('group_of_subjects'),
                    'freesurfer_group_of_subjects':
                        ct.get('group_of_subjects'),
                    'inflated': infl1,
                    "side": "both",
                    "vertex_corr": "Yes"
                }
                res = mesh_type.findValue(atts1)
                if res is not None:
                    return res
                atts1['inflated'] = infl2
                res = mesh_type.findValue(atts1)
                if res is not None:
                    return res
            res = mesh_type.findValue(ct,
                                      requiredAttributes={'inflated': infl1})
            if res is not None:
                return res
            res = mesh_type.findValue(ct,
                                      requiredAttributes={'inflated': infl2})
            if res is not None:
                return res
            atts1 = {
                'group_of_subjects':
                    ct.get('group_of_subjects'),
                'freesurfer_group_of_subjects':
                    ct.get('freesurfer_group_of_subjects'),
                'inflated': infl1,
                "side": "both",
                "vertex_corr": "Yes"
            }
            res = mesh_type.findValue(atts1)
            if res is None:
                atts2 = {
                 'group_of_subjects': ct.get('freesurfer_group_of_subjects'),
                 'freesurfer_group_of_subjects': ct.get('group_of_subjects'),
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
            return res

    self.linkParameters('mesh', 'connectivity_roi_texture', link_mesh)


def execution(self, context):
    objs = context.runProcess('AnatomistShowTexture',
                              read=self.connectivity_roi_texture,
                              mesh=self.mesh, palette='random',
                              rgb_interpolation=True)
    texture = objs['texture']
    texture.setPalette(minVal=0., maxVal=1.)
    return objs
