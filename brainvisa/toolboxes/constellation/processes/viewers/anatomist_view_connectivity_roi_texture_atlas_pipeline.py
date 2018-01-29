# Axon python API module
from brainvisa.processes import *
# Anatomist
from brainvisa import anatomist

name = 'Anatomist view Connectivity ROI Texture, Atlas pipeline variant'
userLevel = 3
roles = ('viewer', )
allowed_processes = ['constel_indiv_clusters_from_atlas_pipeline']

signature = Signature(
    'connectivity_roi_texture', ReadDiskItem(
        'Connectivity ROI Texture', 'aims texture formats'),
)


def initialization(self):
    self.reference_process = None


def execution(self, context):
    viewer = getProcessInstance('anatomist_view_connectivity_roi_texture')
    if not hasattr(self, 'reference_process'):
        return context.runProcess(viewer, self.connectivity_texture)
    mesh = ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes",
                            "inflated": "Yes"}
        ).findValue(self.reference_process.individual_white_mesh)
    if mesh is None:
      mesh = self.reference_process.individual_white_mesh
    return context.runProcess(
        viewer, connectivity_roi_texture=self.connectivity_roi_texture,
        mesh=mesh)

