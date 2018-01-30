# Axon python API module
from brainvisa.processes import *
from brainvisa.processing.process_based_viewer import ProcessBasedViewer

name = 'Anatomist view Connectivity Texture, Atlas pipeline variant'
base_class = ProcessBasedViewer
allowed_processes = ['constel_indiv_clusters_from_atlas_pipeline']


signature = Signature(
    'connectivity_texture', ReadDiskItem(
        'Connectivity Profile Texture', 'aims texture formats'),
)


def execution(self, context):
    viewer = getProcessInstance('anatomist_view_connectivity_texture')
    if not hasattr(self, 'reference_process'):
        return context.runProcess(viewer, self.connectivity_texture)
    mesh = ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes",
                            "inflated": "Yes"}
        ).findValue(self.reference_process.individual_white_mesh)
    if mesh is None:
      mesh = self.reference_process.individual_white_mesh
    return context.runProcess(viewer,
                              connectivity_texture=self.connectivity_texture,
                              mesh=mesh)

