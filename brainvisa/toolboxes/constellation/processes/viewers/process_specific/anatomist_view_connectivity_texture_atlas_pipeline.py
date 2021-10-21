# Axon python API module
from __future__ import absolute_import
from brainvisa.processes import Signature, ReadDiskItem, getProcessInstance
from brainvisa.processing.process_based_viewer import ProcessBasedViewer

name = 'Anatomist view Connectivity Texture, Atlas pipeline variant'
base_class = ProcessBasedViewer


def allowed_processes(process):
    return get_process(process) is not None


def get_process(process):
    allowed = ('constel_indiv_clusters_from_atlas_pipeline',
               'constel_group_pipeline', )
    if process.id() in allowed:
        return process
    parent = process.parent_pipeline()
    if parent is not None and parent.id() in allowed:
        return parent
    return None


signature = Signature(
    'connectivity_texture', ReadDiskItem(
        'Connectivity Profile Texture', 'aims texture formats'),
)


def execution(self, context):
    """
    """

    viewer = getProcessInstance('anatomist_view_connectivity_texture')
    if not hasattr(self, 'reference_process'):
        return context.runProcess(viewer, self.connectivity_texture)
    process = get_process(self.reference_process)
    if process.id() == 'constel_indiv_clusters_from_atlas_pipeline':
        mesh = ReadDiskItem(
            "White Mesh", "Aims mesh formats",
            requiredAttributes={"side": "both", "vertex_corr": "Yes",
                                "inflated": "Yes"}
            ).findValue(self.reference_process.individual_white_mesh)
        if mesh is None:
            mesh = self.reference_process.individual_white_mesh
    else:
        mesh = process.average_mesh
    return context.runProcess(viewer,
                              connectivity_texture=self.connectivity_texture,
                              mesh=mesh)
