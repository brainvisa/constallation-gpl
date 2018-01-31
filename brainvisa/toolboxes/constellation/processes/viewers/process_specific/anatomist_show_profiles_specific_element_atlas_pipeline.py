# Axon python API module
from brainvisa.processes import *
from brainvisa.processing.process_based_viewer import ProcessBasedViewer

name = 'Anatomist Show Connectivity Profiles of a Specific Cortical Element, Atlas pipeline variant'
base_class = ProcessBasedViewer
def allowed_processes(process):
    return get_process(process) is not None


signature = Signature(
    "connectivity_matrix", ReadDiskItem(
        "Connectivity matrix",
        getFormats("aims matrix formats").data + ['Sparse Matrix'],
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "yes",
                            "intersubject": "yes"}),
)


def get_process(process):
    if process.id() == 'constel_indiv_clusters_from_atlas_pipeline':
        return process
    return process.parent_pipeline()


def execution(self, context):
    viewer = getProcessInstance('anatomist_show_profiles_specific_element')
    if not hasattr(self, 'reference_process'):
        return context.runProcess(viewer, self.connectivity_matrix)
    process = get_process(self.reference_process)
    if self.connectivity_matrix == process.atlas_matrix:
        return context.runProcess(
            viewer, connectivity_matrix=self.connectivity_matrix,
            basins_texture=process.filtered_reduced_group_profile)
    else:
        white_mesh = ReadDiskItem(
            "White Mesh", "Aims mesh formats",
            requiredAttributes={"side": "both", "vertex_corr": "Yes",
                                "inflated": "Yes"}
            ).findValue(process.individual_white_mesh)
        if white_mesh is None:
            white_mesh = process.individual_white_mesh
        gyrus_texture = process.regions_parcellation
        return context.runProcess(
            viewer, connectivity_matrix=self.connectivity_matrix,
            white_mesh=white_mesh,
            gyrus_texture=gyrus_texture,
            basins_texture=process.filtered_reduced_group_profile)

