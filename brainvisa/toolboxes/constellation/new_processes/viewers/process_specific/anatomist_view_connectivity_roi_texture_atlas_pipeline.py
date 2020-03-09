# Axon python API module
from __future__ import absolute_import
from brainvisa.processes import *
from brainvisa.processing.process_based_viewer import ProcessBasedViewer

name = 'Anatomist view Connectivity ROI Texture, Atlas pipeline variant'
base_class = ProcessBasedViewer
userLevel = 3
def allowed_processes(process):
    return get_process(process) is not None


signature = Signature(
    'connectivity_roi_texture', ReadDiskItem(
        'Connectivity ROI Texture', 'aims texture formats'),
)


def get_process(process):
    allowed = ('constel_indiv_clusters_from_atlas_pipeline',
               'database_qc_table',
               'constel_group_pipeline')
    if process.id() in allowed:
        return process
    parent = process.parent_pipeline()
    if parent is not None and parent.id() in allowed:
        return parent
    return None


def execution(self, context):
    viewer = getProcessInstance('anatomist_view_connectivity_roi_texture')
    if not hasattr(self, 'reference_process'):
        return context.runProcess(viewer, self.connectivity_roi_texture)
    process = get_process(self.reference_process)

    # -------
    # constel_indiv_clusters_from_atlas_pipeline case
    if process.id() == 'constel_indiv_clusters_from_atlas_pipeline':
        mesh = ReadDiskItem(
            "White Mesh", "Aims mesh formats",
            requiredAttributes={"side": "both", "vertex_corr": "Yes",
                                "inflated": "Yes"}
            ).findValue(process.individual_white_mesh)
        if mesh is None:
          mesh = process.individual_white_mesh
        return context.runProcess(
            viewer, connectivity_roi_texture=self.connectivity_roi_texture,
            mesh=mesh)

    # -------
    # database_qc_table case
    if process.id() == 'database_qc_table':
        match = {
            'averaged': 'No',
            'vertex_corr': 'Yes',
            'side': 'both',
            'inflated': 'Yes',
            'subject': self.connectivity_roi_texture.get('sid'),
        }
        mesh = ReadDiskItem('White Mesh',
                            'anatomist mesh formats').findValue(match)
        if mesh is None:
            match['inflated'] = 'No'
            mesh = ReadDiskItem('White Mesh',
                                'anatomist mesh formats').findValue(match)
        return context.runProcess(
            viewer, connectivity_roi_texture=self.connectivity_roi_texture,
            mesh=mesh)

    # -------
    # constel_group_pipeline case
    if process.id() == 'constel_group_pipeline':
        sid = self.connectivity_roi_texture.get('sid')
        mesh = None
        if sid is not None:
            match = {'subject': sid, 'side': 'both', 'inflated': 'Yes'}
            mdi = ReadDiskItem('White Mesh', 'anatomist mesh formats')
            mesh = mdi.findValue(match)
            if mesh is None:
                match['inflated'] = 'No'
            mesh = mdi.findValue(match)
        if mesh is None:
            mesh = process.average_mesh
        return context.runProcess(
            viewer, connectivity_roi_texture=self.connectivity_roi_texture,
            mesh=mesh)

