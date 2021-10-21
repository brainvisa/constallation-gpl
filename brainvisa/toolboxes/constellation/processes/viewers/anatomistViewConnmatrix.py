###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################
from __future__ import absolute_import
from brainvisa.processes import Signature, ReadDiskItem, ValidationError,\
    getFormats, mainThreadActions


def validation():
    try:
        from brainvisa import anatomist as ana
    except ImportError:
        raise ValidationError(_t_('Anatomist not available'))
    ana.validation()


name = 'Anatomist view connectivity matrix'
roles = ('viewer', )
userLevel = 2

signature = Signature(
    'connectivity_matrix', ReadDiskItem(
        'Connectivity Matrix',
        getFormats("aims matrix formats").data + ['Sparse Matrix'],
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "no",
                            "intersubject": "no",
                            "individual": "yes"}),
    'white_mesh', ReadDiskItem('White Mesh', 'anatomist mesh formats',
                               requiredAttributes={"side": "both"}),
    'gyrus_texture',
        ReadDiskItem('ROI texture', 'anatomist texture formats',
                     requiredAttributes={"side": "both"}),
)


def initialization(self):
    """
    """

    def link_mesh(self, dummy):
        if self.connectivity_matrix is not None:
            cm = self.connectivity_matrix
            mesh_type = self.signature["white_mesh"]
            atts = {
                "subject": cm.get("subject"),
                "inflated": "No",
            }
            res = mesh_type.findValue(atts)
            if res is None:
                atts = {
                    "group_of_subjects": cm.get("group_of_subjects"),
                    "freesurfer_group_of_subjects":
                        cm.get("group_of_subjects"),
                    "inflated": "No",
                }
                res = mesh_type.findValue(atts)
            if res is None:
                res = cm
            return res

    def link_gyrus(self, dummy):
        if self.connectivity_matrix is not None:
            cm = self.connectivity_matrix
            gyrus_type = self.signature["gyrus_texture"]
            method = cm.get('method')
            if method == 'avg':
                atts = {
                    "averaged": "Yes",
                    "group_of_subjects": cm.get("texture"),
                    "freesurfer_group_of_subjects":
                        cm.get("texture"),
                    "_type": "BothAveragedResampledGyri",
                }
                res = gyrus_type.findValue(atts)
                if res is not None:
                    return res
                # indiv. matrics have no group, but are built from a group
                # in avg mode. Find a group object which has this group
                # attribute
                ct = ReadDiskItem("Group definition", "XML")
                x = ct.findValue(cm)
                if x:
                    atts = {
                        "averaged": "Yes",
                        "group_of_subjects": x.get("group_of_subjects"),
                        "freesurfer_group_of_subjects":
                            x.get("group_of_subjects"),
                    }
                    res = gyrus_type.findValue(atts)
                    if res is not None:
                        return res
                # otherwise fallback to a different group, if there is only one
                atts = {"averaged": "Yes"}
                res = gyrus_type.findValue(atts)
                if res is not None:
                    return res
            atts = {
                "subject": cm.get("subject"),
                "_type": "BothResampledGyri",
            }
            res = gyrus_type.findValue(atts)
            if res is None:
                del atts["_type"]
                res = gyrus_type.findValue(atts)
            if res is None:
                res = cm
            return res

    self.linkParameters('white_mesh', 'connectivity_matrix', link_mesh)
    self.linkParameters('gyrus_texture', 'connectivity_matrix', link_gyrus)


def execution(self, context):
    from brainvisa import anatomist as ana
    a = ana.Anatomist()
    mesh = a.loadObject(self.white_mesh)
    patch = a.loadObject(self.gyrus_texture)
    sparse = a.loadObject(self.connectivity_matrix)
    conn = a.fusionObjects(
        [mesh, patch, sparse], method='ConnectivityMatrixFusionMethod')
    if conn is None:
        raise ValueError(
            'could not fusion objects-matrix,\
            mesh and labels texture may not correspond.')

    wgroup = a.createWindowsBlock(2)
    win = a.createWindow('3D', block=wgroup, no_decoration=False)
    a.execute('WindowConfig',
              windows=[win],
              light={'background': [0., 0., 0., 0.]})
    win.camera(view_quaternion=[0.5, 0.5, 0.5, 0.5])

    win.addObjects(conn)
    win.setControl('ConnectivityMatrixControl')

    mainThreadActions().push(wgroup.widgetProxy().widget.resize, 600, 500)

    return [win, conn]
