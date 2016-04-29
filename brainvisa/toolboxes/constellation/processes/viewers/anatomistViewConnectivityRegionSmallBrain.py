#############################################################################
# This software and supporting documentation are distributed by
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
#
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
#############################################################################

# brainvisa
from brainvisa.processes import *
from brainvisa import anatomist as ana

name = 'Anatomist view mozaic visualization of fibers'
userLevel = 0
#roles = ('viewer', )


signature = Signature(
    'bundles', ListOf(ReadDiskItem('Fascicles bundles', 'Aims bundles')),
    'dw_to_t1', ReadDiskItem('Transform T2 Diffusion MR to Raw T1 MRI',
                             'Transformation matrix'),
    'white_mesh', ReadDiskItem('White Mesh', 'anatomist mesh formats',
                               requiredAttributes={"side": "both",
                                                   "vertex_corr": "Yes",
                                                   "inflated": "No"}),
    'clustering_texture', ListOf(
        ReadDiskItem('Connectivity ROI Texture', 'anatomist texture formats',
                     requiredAttributes={"roi_autodetect":"No",
                                         "roi_filtered":"No",
                                         "averaged":"No",
                                         "intersubject":"Yes",
                                         "step_time":"Yes"})),
    'major_texture', ReadDiskItem('Label Texture',
                                  'anatomist texture formats'),
    'max_number_of_fibers', Integer(),
    'clustering_texture_timestep', ListOf(Integer()),
)


def initialization( self ):
    def link_trans(self, dummy):
        if len(self.bundles) != 0:
            return self.bundles[0]

    self.linkParameters('bundles', 'clustering_texture')
    self.linkParameters('dw_to_t1', 'bundles', link_trans)
    self.linkParameters('white_mesh', 'dw_to_t1')
    self.max_number_of_fibers = 10000
    self.clustering_texture_timestep = []


def loadFilteredBundles(self, bundles_name):
    '''Fake bundles reading: just creates an empty graph with the file name
    in it, which will be used (and actually read) by the fusion.
    Also counts fibers.
    '''
    import connectomist.api as conn
    from soma import aims
    from soma.minf import api as minf

    maxFibers = self.max_number_of_fibers
    nfibers = 0
    if maxFibers != 0:
        binfo = minf.readMinf(bundles_name)[0]
        if 'curves_count' in binfo:
            nfibers = binfo['curves_count']
        elif 'fibers_count' in binfo:
            nfibers = binfo['fibers_count']
        else:
            nfibers = 500000 # arbitrary...
    graph = aims.Graph('RoiArg')
    graph['fibers_count'] = nfibers
    a = ana.Anatomist()
    ag = a.toAObject(graph)
    ag.setFileName(bundles_name)
    return ag


def execution_mainthread(self, context):
    """Visualization of small brains on the parcellated cortical surface.
    
    For each cluster or region, a small brain represents the connections
    usinf fiber tracts.
    """
    # instance of anatomist
    a = ana.Anatomist()
    
    # load object
    mesh = a.loadObject(self.white_mesh)
    
    r = a.createReferential()
    mr = mesh.referential
    
    viewing_objects = []
    living_objects = []
    bundleslist = []
    totalfibers = 0
    for (ct, bundles_name) in enumerate(self.bundles):
        context.write('scanning budles:', ct+1, '/', len(self.bundles))
        bundles = self.loadFilteredBundles(bundles_name.fullPath())
        bundles.assignReferential(r)
        bundleslist.append(bundles)
        totalfibers += bundles.graph()['fibers_count']
        a.loadTransformation(self.dw_to_t1.fullPath(), r, mr)
        living_objects.append(bundles)

    context.write('total number of fibers:', totalfibers)
    if totalfibers != 0:
        fibers_proportion_filter \
            = float(self.max_number_of_fibers) / totalfibers
    else:
        fibers_proportion_filter = 1.
    context.write('keeping proportion:', fibers_proportion_filter)
    for (ct, bundles) in enumerate(bundleslist):
        clusters = a.loadObject(self.clustering_texture[ct])
        if len(self.clustering_texture_timestep) > ct:
            clusters.attributed()['time_step'] \
                = self.clustering_texture_timestep[ct]
        living_objects.append(clusters)
        context.write('processing bundles:', ct+1, '/', len(self.bundles))
        bundles.graph()['fibers_proportion_filter'] = fibers_proportion_filter
        connectivity = a.fusionObjects([mesh, clusters, bundles],
            method='FusionBundlesSplitByCorticalROIsMethod')
        if connectivity is None:
            raise ValueError('could not fusion objects - '
                'mesh, texture and bundles')
        viewing_objects.append(connectivity)
        # remove brain mesh in node "other"
        other_nodes = [node for node in connectivity.graph().vertices() \
            if node.has_key('name') and node['name'] == 'others']
        if len(other_nodes) != 0:
            aobj = other_nodes[0]['ana_object']
            aobj.eraseObject(other_nodes[0]['roi_mesh_ana'])
            del other_nodes[0]['roi_mesh_ana']
            del other_nodes[0]['roi_mesh']
            del other_nodes[0]['ana_object']
            connectivity.eraseObject(aobj)

    # load object
    ana_major_texture = a.loadObject(self.major_texture)
    
    # define a palette
    ana_major_texture.setPalette(palette='parcellation720',
                                 minVal=11,
                                 maxVal=730,
                                 absoluteMode=True)
    
    # fusion between mesh and texure
    major_textured_mesh = a.fusionObjects([mesh, ana_major_texture],
                          method='FusionTexSurfMethod')
    
    # change major_textured_mesh settings
    a.execute("TexturingParams",
              objects=[major_textured_mesh],
              interpolation="rgb")
    
    # view object
    wgroup = a.createWindowsBlock(nbCols=2)
    win1 = a.createWindow("3D", block=wgroup)
    win2 = a.createWindow("3D", block=wgroup)
    win1.addObjects(viewing_objects)
    win1.addObjects(major_textured_mesh)
    
    # control on objects
    a.execute("SetControl", windows = [win1], control="SmallBrainsControl")
    action = win1.view().controlSwitch().getAction(
                 "SmallBrainSelectionAction")
    action.secondaryView = win2
    
    living_objects.append(major_textured_mesh)
    living_objects += viewing_objects

    return [win1, win2, living_objects]

def execution(self, context):
    return mainThreadActions().call(self.execution_mainthread, context)
