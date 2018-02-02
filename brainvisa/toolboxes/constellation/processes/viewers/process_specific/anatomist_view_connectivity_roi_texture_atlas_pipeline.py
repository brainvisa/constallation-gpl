# Axon python API module
from brainvisa.processes import *
from brainvisa.processing.process_based_viewer import ProcessBasedViewer

name = 'Anatomist view Connectivity ROI Texture, Atlas pipeline variant'
base_class = ProcessBasedViewer
def allowed_processes(process):
    return get_process(process) is not None


signature = Signature(
    'connectivity_roi_texture', ReadDiskItem(
        'Connectivity ROI Texture', 'aims texture formats'),
)


def get_process(process):
    if process.id() in ('constel_indiv_clusters_from_atlas_pipeline',
                        'database_qc_table'):
        return process
    return process.parent_pipeline()


def execution(self, context):
    viewer = getProcessInstance('anatomist_view_connectivity_roi_texture')
    if not hasattr(self, 'reference_process'):
        return context.runProcess(viewer, self.connectivity_texture)
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
