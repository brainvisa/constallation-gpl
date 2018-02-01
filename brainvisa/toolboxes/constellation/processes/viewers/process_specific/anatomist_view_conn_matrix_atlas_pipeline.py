# Axon python API module
from brainvisa.processes import *
from brainvisa.processing.process_based_viewer import ProcessBasedViewer

name = 'Anatomist view connectivity matrix, Atlas pipeline variant'
base_class = ProcessBasedViewer
def allowed_processes(process):
    return get_process(process) is not None


signature = Signature(
    'connectivity_matrix', ReadDiskItem(
        'Connectivity Matrix',
        getFormats("aims matrix formats").data + ['Sparse Matrix'],
        requiredAttributes={"ends_labelled":"all",
                            "reduced":"no",
                            "intersubject":"no",
                            "individual": "yes"}),
)


def get_process(process):
    if process.id() in ('constel_indiv_clusters_from_atlas_pipeline',
                        'database_qc_table'):
        return process
    return process.parent_pipeline()


def execution(self, context):
    viewer = getProcessInstance('AnatomistViewConnMatrix')
    if not hasattr(self, 'reference_process'):
        return context.runProcess(viewer, self.connectivity_matrix)
    process = get_process(self.reference_process)
    context.write('process:', process.id())

    # -------
    # constel_indiv_clusters_from_atlas_pipeline case
    if process.id() == 'constel_indiv_clusters_from_atlas_pipeline':
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
            gyrus_texture=gyrus_texture)

    # -------
    # database_qc_table case
    if process.id() == 'database_qc_table':
        match = {
            'averaged': 'No',
            'vertex_corr': 'Yes',
            'side': 'both',
            'inflated': 'Yes',
            'subject': self.connectivity_matrix.get('subject'),
        }
        mesh = ReadDiskItem('White Mesh',
                            'anatomist mesh formats').findValue(match)
        if mesh is None:
            match['inflated'] = 'No'
            mesh = ReadDiskItem('White Mesh',
                                'anatomist mesh formats').findValue(match)
        if self.connectivity_matrix.get('method') == 'avg':
            # avg mode
            match = {
                'averaged': 'Yes',
                'vertex_corr': 'Yes',
                'side': 'both',
            }
            group = self.connectivity_matrix.get('group_of_subjects')
            if group is not None:
                match['freesurfer_group_of_subjects'] = group
            gyri = ReadDiskItem('ROI Texture',
                                'anatomist texture formats').findValue(match)
            if gyri is None and group is not None:
                del match['freesurfer_group_of_subjects']
                gyri = ReadDiskItem(
                    'ROI Texture',
                    'anatomist texture formats').findValue(match)
            return context.runProcess(
                viewer, connectivity_matrix=self.connectivity_matrix,
                white_mesh=mesh,
                gyrus_texture=gyri)

        # concat mode
        gyri = ReadDiskItem('ROI Texture',
                            'anatomist texture formats').findValue(mesh)
        group = self.connectivity_matrix.get('group_of_subjects')
        return context.runProcess(
                viewer, connectivity_matrix=self.connectivity_matrix,
                white_mesh=mesh,
                gyrus_texture=gyri)
