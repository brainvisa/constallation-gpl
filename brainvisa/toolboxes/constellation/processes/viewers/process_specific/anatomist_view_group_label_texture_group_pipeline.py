# Axon python API module
from __future__ import absolute_import
from brainvisa.processes import *
from brainvisa.processing.process_based_viewer import ProcessBasedViewer

name = 'Anatomist View Group Label Texture, Group pipeline variant'
base_class = ProcessBasedViewer
def allowed_processes(process):
    return get_process(process) is not None


signature = Signature(
    "label_texture", ReadDiskItem('Mask Texture', 'Anatomist texture formats'),
)


def get_process(process):
    allowed = ('constel_group_pipeline', )
    if process.id() in allowed:
        return process
    parent = process.parent_pipeline()
    if parent is not None and parent.id() in allowed:
        return parent
    return None


def execution(self, context):
    viewer = getProcessInstance('anatomist_view_group_label_texture')
    if not hasattr(self, 'reference_process'):
        return context.runProcess(viewer, self.label_texture)
    process = get_process(self.reference_process)

    mesh = process.average_mesh
    return context.runProcess(
        viewer, label_texture=self.label_texture,
        mesh=mesh)
