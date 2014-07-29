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
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.

from brainvisa.processes import *
from brainvisa import anatomist as ana

name = 'Anatomist view connectivity regions on small brain'
userLevel = 0
roles = ('viewer', )

signature = Signature(
    'bundles', ListOf(ReadDiskItem('Fascicles bundles', 'Aims bundles')),
    'RawT1Image', ReadDiskItem('Raw T1 MRI', 'NIFTI-1 image'),
    'dw_to_t1', ReadDiskItem('Transformation matrix', 'Transformation matrix'),
    'white_mesh', ReadDiskItem('AimsBothWhite', 'anatomist mesh formats'),
    'clustering_texture', ListOf(ReadDiskItem('Group Clustering Texture', 
                                              'anatomist texture formats')),
    'texture_hbm', ReadDiskItem('Label Texture', 'anatomist texture formats'),
    'max_number_of_fibers', Integer(),
)

def initialization( self ):
    self.linkParameters('bundles', 'clustering_texture')
    self.linkParameters('dw_to_t1', 'RawT1Image')
    self.max_number_of_fibers = 10000


def loadFilteredBundles(self, bundles_name):
    '''Fake bundles reading: just creates an empty graph with the file name
    in it, which will be used (and actually read) by the fusion.
    Also counts fibers.
    '''
    import connectomist.api as conn
    from soma import aims
    from soma.minf import api as minf

    maxFibers = self.max_number_of_fibers
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
    a = ana.Anatomist()
    mesh = a.loadObject(self.white_mesh)
    t1 = a.loadObject(self.RawT1Image)
    r = a.createReferential()
    mr = t1.referential
    mesh.assignReferential(mr)
    viewing_objects = []
    living_objects = []
    bundleslist = []
    totalfibers = 0
    for ct, bundles_name in enumerate(self.bundles):
        context.write('scanning budles:', ct+1, '/', len(self.bundles))
        bundles = self.loadFilteredBundles(bundles_name.fullPath())
        bundles.assignReferential(r)
        bundleslist.append(bundles)
        totalfibers += bundles.graph()['fibers_count']
        a.loadTransformation(self.dw_to_t1.fullPath(), r, mr)
        living_objects.append(bundles)

    context.write('total number of fibers:', totalfibers)
    fibers_proportion_filter = float(self.max_number_of_fibers) / totalfibers
    context.write('keeping proportion:', fibers_proportion_filter)
    for ct, bundles in enumerate(bundleslist):
        clusters = a.loadObject(self.clustering_texture[ct])
        living_objects.append(clusters)
        context.write('processing bundles:', ct+1, '/', len(self.bundles))
        bundles.graph()['fibers_proportion_filter'] = fibers_proportion_filter
        connectivity = a.fusionObjects([mesh, clusters, bundles, t1],
            method='FusionTexMeshImaAndBundlesToROIsAndBundlesGraphMethod')
        if connectivity is None:
            raise ValueError('could not fusion objects - T1, mesh, texture and bundles')
        viewing_objects.append(connectivity)

    anacl = a.loadObject(self.texture_hbm)
    anacl.setPalette(palette='parcellation720', minVal=11, maxVal=730,
        absoluteMode=True)
    tex = a.fusionObjects([mesh, anacl], method='FusionTexSurfMethod')
    a.execute('TexturingParams', objects=[tex], interpolation='rgb')
    wgroup = a.createWindowsBlock(nbCols=2)
    win = a.createWindow('3D', block=wgroup)
    win2 = a.createWindow('3D', block=wgroup)
    win.addObjects(viewing_objects)
    win.addObjects(tex)
    a.execute('SetControl', windows = [win], control='SmallBrainsControl')
    action = win.view().controlSwitch().getAction('SmallBrainSelectionAction')
    context.write('action:', action)
    action.secondaryView = win2
    living_objects += [t1, tex]
    living_objects += viewing_objects

    return [win, win2, living_objects]

def execution(self, context):
    return mainThreadActions().call(self.execution_mainthread, context)