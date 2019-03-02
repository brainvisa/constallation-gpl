#############################################################################
# This software and supporting documentation are distributed by
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
#############################################################################

# brainvisa
from brainvisa.processes import *
from brainvisa import anatomist as anatomist

# system import
import numpy

# soma
from soma import aims

# constel module
try:
    import constel
    import constel.lib.utils.matrixtools as clcmt
    from constel.lib.utils.texturetools import geodesic_gravity_center
except:
    pass


def validation():
    """This function is executed at setup when the process is loaded. 

    It checks some conditions for the process to be available.
    """
    try:
        import constel.lib.utils.matrixtools as clcmt
    except:
        raise ValidationError("Please make sure that constel module"
                              "is installed")


name = "Anatomist view mozaic visualization of textured mesh"
userLevel = 2
#roles = ("viewer", )


signature = Signature(
    'connectivity_matrix', ListOf(
        ReadDiskItem('Connectivity Matrix', 'aims readable volume formats',
        requiredAttributes={"ends_labelled":"all",
                            "reduced":"no",
                            "intersubject":"yes",
                            "individual": "yes"})),
    'mesh', ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both",
                            "vertex_corr": "Yes",
                            "averaged": "Yes"}),
    'basins_texture', ListOf(
        ReadDiskItem('Connectivity ROI Texture', 'anatomist texture formats',
        requiredAttributes={"roi_autodetect":"yes",
                            "roi_filtered":"yes",
                            "intersubject":"yes",
                            "step_time":"no",
                            "measure": "no"})),
    'clustering_texture', ListOf(
        ReadDiskItem('Connectivity ROI Texture', 'anatomist texture formats',
        requiredAttributes={"roi_autodetect":"no",
                            "roi_filtered":"no",
                            "intersubject":"yes",
                            "step_time":"yes",
                            "measure": "no"})),
    'time_step', ListOf(Integer()),
    'major_texture', ReadDiskItem(
        'Label Texture', 'anatomist texture formats'),
    'small_brains_distance', Float(),
    'small_brains_scaling', Float(),
    'mode', Choice('normal', 'brain_center', 'hemispheres_centers'),
)


def initialization(self):
    self.linkParameters("mesh", "connectivity_matrix")
    self.linkParameters("basins_texture", "connectivity_matrix")
    self.linkParameters("clustering_texture", "connectivity_matrix")
    self.small_brains_distance = 10.
    self.small_brains_scaling = 0.1
    self.mode = "normal"


def execution_mainthread(self, context):
    """Visualization of small brains on the parcellated cortical surface.

    For each cluster or region, a small brain represents the connections
    on a textured mesh of the cortex.
    """
    # instance of anatomist
    a = anatomist.Anatomist()

    # load object
    ana_mesh = a.loadObject(self.mesh)

    # will bring together
    graph_list = []

    #########################################################################
    #                             Small brains                              #
    #########################################################################

    for (index, matrix_name) in enumerate(self.connectivity_matrix):
        # load object
        ana_clusters = a.loadObject(self.clustering_texture[index])

        # create aims objects from anatomist objects
        aims_mesh = a.toAimsObject(ana_mesh)
        aims_clusters = a.toAimsObject(ana_clusters)

        # read object
        basins = aims.read(self.basins_texture[index].fullPath())
        node_name = os.path.basename(matrix_name.fullName())
        matrix = aims.read(matrix_name.fullPath())
        # M(basins_number, vertices_patch)
        matrix = numpy.asarray(matrix)[:, :, 0, 0]

        # get the texture with the required time_step
        fixed_clusters = aims_clusters[self.time_step[index]].arraydata()

        # compute the reduce matrix for each cluster
        # M(parcels_number, basins_number)
        reduced_matrix = clcmt.compute_mclusters_by_nbasins_matrix(
            matrix, aims_clusters, self.time_step[index])
        reduced_matrix = numpy.asarray(reduced_matrix)

        # create a bouding box from mesh
        # get bouding box min values and max values
        bbmin, bbmax = ana_mesh.boundingbox()

        # create graph structure
        graph = aims.Graph("RoiArg")
        graph["boundingbox_min"] = list(bbmin)
        graph["boundingbox_max"] = list(bbmax)
        graph["small_brains_distance"] = self.small_brains_distance
        graph["small_brains_scaling"] = self.small_brains_scaling
        # TODO: complete this mode
#        if self.mode == "hemispheres_centers":
#            graph["lateralized_view"] = self.lateralized_view

        # get the number of clusters in the loaded texture
        regions = [x for x in numpy.unique(fixed_clusters) if x != 0]

        # create one vertex/node of graph with its name for each cluster
        for rnum in regions:
            # insert a new vertex
            vertex = graph.addVertex("roi")
            # store mesh in the "aims_Tmtktri" property of vertex of graph
            aims.GraphManip.storeAims(
                graph, vertex, "aims_Tmtktri", aims_mesh)
            vertex["name"] = str("%s - clust. %d node" % (node_name, rnum))

        # create anatomist object graph
        ana_graph = a.toAObject(graph)

        # make ref-counting work on python side
        ana_graph.releaseAppRef()

        # set the referential of the mesh as inheritance
        ana_graph.setReferentialInheritance(ana_mesh)

        # makes an object unvisible (i.e. not seen in control window)
        a.unmapObject(ana_graph)

        # action on each node of graph
        global_max = 0.
        textures = []
        for (i, vertex) in enumerate(graph.vertices()):
            # create a texture summarising the connections between
            # one cluster and basins
            # TODO: rename "oneTargetDensityTargetsRegroupTexture"
            basins_texture = constel.oneTargetDensityTargetsRegroupTexture(
                reduced_matrix[i], basins, self.time_step[index])

            # create anatomist object
            ana_basins_texture = a.toAObject(basins_texture)
            a.execute('TexturingParams',
                      objects=[ana_basins_texture],
                      interpolation='rgb')

            # regroup all basins_textures of the patch
            textures.append(ana_basins_texture)

            # make ref-counting work on python side
            ana_basins_texture.releaseAppRef()

            # makes an object unvisible (i.e. not seen in control window)
            a.unmapObject(ana_basins_texture)

            # shallow copy
            mesh_copy = ana_mesh.clone(True)
            mesh_copy.setReferential(ana_mesh.referential)

            # fusion between mesh and texure
            textured_mesh = a.fusionObjects(
                [mesh_copy, ana_basins_texture], method="FusionTexSurfMethod")

            # create a name for the textured mesh from name of node
            textured_mesh.setName("%s - clust. %d" % (node_name, rnum))

            # makes an object unvisible (i.e. not seen in control window)
            a.unmapObject(textured_mesh)

            ana_vertex = vertex["ana_object"]
            oldmesh = [x for x in ana_vertex][0]

            # set the referential of the mesh as inheritance
            ana_vertex.setReferentialInheritance(mesh_copy)
            ana_vertex.eraseObject(oldmesh)
            ana_vertex.insert(textured_mesh)

            # compute the gravity center of the cluster or given region
            gravity_center_index = geodesic_gravity_center(
                aims_mesh,
                aims_clusters,
                regions[i],
                time_step=self.time_step[index])

            # give the center and its index in the node of graph
            vertex["center"] = aims_mesh.vertex()[gravity_center_index]
            vertex["cluster_index"] = i
            if self.mode == "normal":
                vertex["normal"] = aims_mesh.normal()[gravity_center_index]

        # define a palette on the small brains
        # max value is calculated by reference to the max value
        # of the all textures of basins of given graph
        texture_max = numpy.max(basins_texture[0].arraydata())
        global_max = max((texture_max, global_max))
        a.setObjectPalette(objects=textures,
                           palette="Blue-Red-fusion",
                           minVal=-0.05,
                           maxVal=float(global_max),
                           absoluteMode=True)

        # update Anatomist object and its views
        ana_graph.setChanged()
        ana_graph.notifyObservers()

        # makes an object visible (i.e. seen in control window)
        a.mapObject(ana_graph)

        # set selected color
        ana_graph.setMaterial(diffuse=[0.8, 0.8, 0.8, 1.])
        graph_list.append(ana_graph)

    #########################################################################
    #                             Major brain                                 #
    #########################################################################

    # load object
    ana_major_texture = a.loadObject(self.major_texture)

    # define a palette
    ana_major_texture.setPalette(palette="parcellation720")

    # fusion between mesh and texure
    major_textured_mesh = a.fusionObjects(
        [ana_mesh, ana_major_texture], method="FusionTexSurfMethod")

    # change major_textured_mesh settings
    a.execute(
        "TexturingParams", objects=[ana_major_texture], interpolation="rgb")

    # view object
    wgroup = a.createWindowsBlock(nbCols=2)
    win1 = a.createWindow("3D", block=wgroup)
    #win2 = a.createWindow("3D", block=wgroup)
    win1.addObjects(major_textured_mesh)
    win1.addObjects(graph_list)

    # control on objects
    a.execute("SetControl", windows=[win1], control="SmallBrainsControl")
    action = win1.view().controlSwitch().getAction(
        "SmallBrainSelectionAction")
    #action.secondaryView = win2

    wgroup.widgetProxy().widget.resize(1200, 800)

    return [ana_mesh, graph_list, ana_clusters,
            major_textured_mesh, win1]#, win2]


def execution(self, context):
    return mainThreadActions().call(self.execution_mainthread, context)
