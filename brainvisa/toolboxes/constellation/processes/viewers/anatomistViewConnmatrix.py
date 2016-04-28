###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################
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


name = 'Anatomist view connectivity matrix'
roles = ('viewer', )
userLevel = 0

signature = Signature(
    'connectivity_matrix', ReadDiskItem(
        'Connectivity Matrix',
        getFormats("aims matrix formats").data + ['Sparse Matrix'],
        requiredAttributes={"ends_labelled":"mixed",
                            "reduced":"No",
                            "dense":"No",
                            "intersubject":"No"}),
    'white_mesh', ReadDiskItem('White Mesh', 'anatomist mesh formats',
                               requiredAttributes={"side": "both"}),
    'gyrus_texture', 
        ReadDiskItem('ROI texture', 'anatomist texture formats',
                     requiredAttributes={"side": "both"}), )

def initialization(self):
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
            study = cm.get('study')
            if study == 'avg':
                print 'averaged study.'
                atts = {
                    "group_of_subjects": cm.get("group_of_subjects"),
                    "freesurfer_group_of_subjects":
                        cm.get("group_of_subjects"),
                    "_type": "BothAveragedResampledGyri",
                }
                res = gyrus_type.findValue(atts)
                print 'res:', res
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
    a = ana.Anatomist()
    mesh = a.loadObject(self.white_mesh)
    patch = a.loadObject(self.gyrus_texture)
    sparse = a.loadObject(self.connectivity_matrix)
    conn = a.fusionObjects(
        [mesh, patch, sparse], method='ConnectivityMatrixFusionMethod')
    if conn is None:
        raise ValueError(
            'could not fusion objects-matrix, mesh and labels texture may not correspond.')
    
    wgroup = a.createWindowsBlock(2)
    win = a.createWindow('Sagittal', block=wgroup, no_decoration=False)
    a.execute('WindowConfig', windows=[win], light={'background' : [0.,0.,0.,0.]})
#    win1 = a.createWindow('Sagittal', block=wgroup, no_decoration=True)
#    a.execute('WindowConfig', windows=[win1], light={'background' : [0.,0.,0.,0.]})
    
    win.addObjects(conn)
#    win1.addObjects(conn)
    win.setControl('ConnectivityMatrixControl')
#    win1.setControl('ConnectivityMatrixControl')

    return [win, conn]
