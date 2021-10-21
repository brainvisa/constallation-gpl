# Axon python API module
from __future__ import absolute_import
from __future__ import print_function
from brainvisa.processes import Signature, ReadDiskItem, getProcessInstance,\
    getFormats
from brainvisa.processing.process_based_viewer import ProcessBasedViewer

name = 'Anatomist view connectivity matrix, Atlas pipeline variant'
base_class = ProcessBasedViewer


def allowed_processes(process):
    return get_process(process) is not None


signature = Signature(
    'connectivity_matrix', ReadDiskItem(
        'Connectivity Matrix',
        getFormats("aims matrix formats").data + ['Sparse Matrix'],
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "no",
                            "intersubject": "no",
                            "individual": "yes"}),
)


def get_process(process):

    allowed = ('constel_indiv_clusters_from_atlas_pipeline',
               'database_qc_table',
               'constel_individual_pipeline_fsl_connectome',
               'constel_group_pipeline')
    if process.id() in allowed:
        return process
    parent = process.parent_pipeline()
    if parent is not None and parent.id() in allowed:
        return parent
    return None


def execution(self, context):
    """
    """

    viewer = getProcessInstance('AnatomistViewConnMatrix')
    if not hasattr(self, 'reference_process'):
        return context.runProcess(viewer, self.connectivity_matrix)
    process = get_process(self.reference_process)
    context.write('process:', process.id())

    # constel_indiv_clusters_from_atlas_pipeline case
    if process.id() in ('constel_indiv_clusters_from_atlas_pipeline',
                        'constel_individual_pipeline_fsl_connectome'):
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
                '_database': mesh.get("_database"),
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

    # constel_group_pipeline case
    if process.id() in ('constel_group_pipeline', ):
        white_mesh = process.average_mesh
        if process.method == 'avg':
            gyrus_texture = process.regions_parcellation[0]
        else:
            node = process.executionNode().child('ReducedGroupMatrix')
            print('node:', node)
            sproc = node._process
            i = sproc.complete_individual_matrices.index(
                self.connectivity_matrix)
            if i >= 0:
                gyrus_texture = process.regions_parcellation[i]
        print('gyrus texture:', gyrus_texture)
        return context.runProcess(
            viewer, connectivity_matrix=self.connectivity_matrix,
            white_mesh=white_mesh,
            gyrus_texture=gyrus_texture)
