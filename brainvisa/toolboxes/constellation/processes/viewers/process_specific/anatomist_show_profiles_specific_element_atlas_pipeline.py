# Axon python API module
from __future__ import absolute_import
from brainvisa.processes import Signature, ReadDiskItem, getFormats,\
    getProcessInstance
from brainvisa.processing.process_based_viewer import ProcessBasedViewer

name = 'Anatomist Show Connectivity Profiles of a Specific Cortical Element,\
        Atlas pipeline variant'
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
    allowed = ('constel_indiv_clusters_from_atlas_pipeline',
               'constel_group_pipeline',
               'database_qc_table')
    if process.id() in allowed:
        return process
    parent = process.parent_pipeline()
    if parent is not None and parent.id() in allowed:
        return parent
    return None


def execution(self, context):
    viewer = getProcessInstance('anatomist_show_profiles_specific_element')
    if not hasattr(self, 'reference_process'):
        return context.runProcess(viewer, self.connectivity_matrix)
    process = get_process(self.reference_process)

    # -------
    # constel_indiv_clusters_from_atlas_pipeline case
    pid = process.id()
    if pid in ('constel_indiv_clusters_from_atlas_pipeline',
               'constel_group_pipeline'):
        gp = (process.id() == 'constel_group_pipeline')
        if gp or self.connectivity_matrix == process.atlas_matrix:
            white_mesh = ReadDiskItem(
                "White Mesh", "Aims mesh formats",
                requiredAttributes={"side": "both", "vertex_corr": "Yes",
                                    "inflated": "Yes"}
                ).findValue(process.regions_parcellation)
            if white_mesh is None:
                white_mesh = ReadDiskItem(
                    "White Mesh", "Aims mesh formats",
                    requiredAttributes={"side": "both", "vertex_corr": "Yes",
                                        "inflated": "No"}
                    ).findValue(process.regions_parcellation)
                if white_mesh is None:
                    if process.id() == 'constel_group_pipeline':
                        white_mesh = process.average_mesh
                    else:
                        white_mesh = process.individual_white_mesh
            if gp:
                gyrus_texture = None
                if process.method == 'avg' \
                    or self.connectivity_matrix \
                        == process.executionNode().GroupClustering \
                        .reduced_group_matrix:
                    if len(process.regions_parcellation) != 0:
                        gyrus_texture = process.regions_parcellation[0]
                else:
                    matrices \
                        = process.executionNode().ReducedGroupMatrix \
                        .intersubject_reduced_matrices
                    i = matrices.index(self.connectivity_matrix)
                    if i >= 0 and len(process.regions_parcellation) > i:
                        gyrus_texture = process.regions_parcellation[i]
            elif process.method == 'avg':
                gyrus_texture = process.regions_parcellation
            else:
                # take group gyri
                match = {
                    'averaged': 'Yes',
                    'vertex_corr': 'Yes',
                    'side': 'both',
                    '_database': white_mesh.get("_database"),
                }
                group = self.connectivity_matrix.get('group_of_subjects')
                if group is not None:
                    match['freesurfer_group_of_subjects'] = group
                gyrus_texture = ReadDiskItem(
                    'ROI Texture',
                    'anatomist texture formats').findValue(match)
                if gyrus_texture is None and group is not None:
                    del match['freesurfer_group_of_subjects']
                    gyrus_texture = ReadDiskItem(
                        'ROI Texture',
                        'anatomist texture formats').findValue(match)
            if process.id() == 'constel_group_pipeline':
                basins_texture \
                    = process.executionNode().GroupRegionsFiltering \
                    .filtered_reduced_group_profile
            else:
                basins_texture = process.filtered_reduced_group_profile
            return context.runProcess(
                viewer, connectivity_matrix=self.connectivity_matrix,
                white_mesh=white_mesh,
                gyrus_texture=gyrus_texture,
                basins_texture=basins_texture)
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

    # -------
    # database_qc_table case
    if pid == 'database_qc_table':
        match = {
            'averaged': 'No',
            'vertex_corr': 'Yes',
            'side': 'both',
            'inflated': 'Yes',
            'subject': self.connectivity_matrix.get('sid'),
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
            if 'freesurfer_group_of_subjects' in match:
                del match['freesurfer_group_of_subjects']
            match['group_of_subjects'] = group
            match['studyname'] = self.connectivity_matrix.get('studyname')
            match['gyrus'] = self.connectivity_matrix.get('gyrus')
            match['smoothing'] = self.connectivity_matrix.get('smoothing')
            match['measure'] = 'no'
            match['roi_autodetect'] = 'yes'
            match['roi_filtered'] = 'yes'
            match['intersubjedt'] = 'yes'
            match['method'] = 'avg'
            basins = ReadDiskItem('Connectivity ROI Texture',
                                  'anatomist texture formats').findValue(match)
            return context.runProcess(
                viewer, connectivity_matrix=self.connectivity_matrix,
                white_mesh=mesh,
                gyrus_texture=gyri,
                basins_texture=basins)

        # concat mode
        gyri = ReadDiskItem('ROI Texture',
                            'anatomist texture formats').findValue(mesh)
        group = self.connectivity_matrix.get('group_of_subjects')
        match = {
            'roi_filtered': 'yes',
            'step_time': 'no',
            'group_of_subjects': group,
            'studyname': self.connectivity_matrix.get('studyname'),
            'intersubject': 'yes',
            'measure': 'no',
            'roi_autodetect': 'yes',
            'method': 'avg',
            'gyrus': self.connectivity_matrix.get('gyrus'),
        }
        basins = ReadDiskItem('Connectivity ROI Texture',
                              'anatomist texture formats').findValue(match)
        return context.runProcess(
                viewer, connectivity_matrix=self.connectivity_matrix,
                white_mesh=mesh,
                gyrus_texture=gyri,
                basins_texture=basins)
