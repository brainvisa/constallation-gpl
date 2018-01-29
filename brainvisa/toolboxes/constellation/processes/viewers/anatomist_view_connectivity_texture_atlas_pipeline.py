# Axon python API module
from brainvisa.processes import *
# Anatomist
from brainvisa import anatomist

name = 'Anatomist view Connectivity Texture, Atlas pipeline variant'
userLevel = 3
roles = ('viewer', )
allowed_processes = ['constel_indiv_clusters_from_atlas_pipeline']

signature = Signature(
    'connectivity_texture', ReadDiskItem(
        'Connectivity Profile Texture', 'aims texture formats'),
)


def initialization(self):
    self.reference_process = None


def execution(self, context):
    viewer = getProcessInstance('anatomist_view_connectivity_texture')#'AnatomistShowTexture')
    if not hasattr(self, 'reference_process'):
        return context.runProcess('anatomist_view_connectivity_texture', self.connectivity_texture)
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

