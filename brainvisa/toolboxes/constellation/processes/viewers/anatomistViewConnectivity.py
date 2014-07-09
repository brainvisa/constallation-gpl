############################################################################
# This software and supporting documentation are distributed by
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
############################################################################

# BrainVisa
from brainvisa.processes import *
from soma import aims

# Anatomist
from brainvisa import anatomist

name = 'Anatomist view connectivity'
userLevel = 0
roles = ('viewer', )

signature = Signature(
    'bundles', ReadDiskItem('Fascicles bundles', 'Aims bundles'),
    'RawT1Image', ReadDiskItem('Raw T1 MRI', 'NIFTI-1 image'),
    'dw_to_t1', ReadDiskItem('Transformation matrix', 
                             'Transformation matrix'),
    'white_mesh', ReadDiskItem('AimsBothWhite', 
                               'anatomist mesh formats'),
    'clustering_texture', ReadDiskItem('Group Clustering Texture', 
                                       'anatomist texture formats'),
    'cluster_number', String(),
)

def initialization( self ):
    self.linkParameters('bundles', 'clustering_texture')
    self.linkParameters('dw_to_t1', 'RawT1Image')

def execution_mainthread(self, context):
    # instance of Anatomist
    a = anatomist.Anatomist()
    
    # load objects
    mesh = a.loadObject(self.white_mesh)
    clusters = a.loadObject(self.clustering_texture)
    bundles = a.loadObject(self.bundles)
    t1 = a.loadObject(self.RawT1Image)
    
    # load a transformation
    r = a.createReferential()
    mr = t1.referential
    bundles.assignReferential(r)
    mesh.assignReferential(mr)
    a.loadTransformation(self.dw_to_t1.fullPath(), r, mr)
    
    # change palette
    palette = a.getPalette("freesurfer_gyri")
    clusters.setPalette(palette, minVal=0, maxVal=20, absoluteMode=True)
    
    # view object
    win = a.createWindow('3D')
    
    # fusion T1, mesh, texture and bundles
    connectivity = a.fusionObjects([ mesh, clusters, bundles, t1 ],
        method = 'FusionTexMeshImaAndBundlesToROIsAndBundlesGraphMethod')
        
    #a.execute('FusionTexMeshImaAndBundlesToROIsAndBundlesGraphMethod', 
               #object=connectivity)
    if connectivity is None:
        raise ValueError('could not fusion objects')
    
    # adds objects in windows:
    win.addObjects(connectivity)
    
    # get the Aims graph
    graph = a.toAimsObject(connectivity)
    #mesh = a.toAimsObject(mesh)
    a.execute('SetMaterial', objects=[connectivity], diffuse=[0.5, 0., 1., 0.2])

    
    patches = {self.cluster_number: [0.4, 0.6, 1., 1.]}
    basins = {'11': [0., 0., 1., 0.35], '24': [1., 0., 0., 0.35], 
              '16': [0., 1., 0., 0.35],}
              #'17': [0.5, 1., 1., 0.3], 
              #'13': [1., 0., 0.5, 0.3]}
    basincolor = [0.9, 0.9, 0.9, 1.]
    all_regions = patches.keys() + basins.keys()
    for v in graph.vertices():
        if v['name'] in all_regions:
            if v['name'] in patches:
                a.execute('SetMaterial', objects=[v['ana_object']], diffuse=patches[v['name']])
                for edge in v.edges():
                    if edge.vertices()[0]['name'] in basins or edge.vertices()[1]['name'] in basins:
                        if edge.vertices()[0]['name'] in basins:
                            color = basins[edge.vertices()[0]['name']]
                        else:
                            color = basins[edge.vertices()[1]['name']]
                        edgeobj = edge['ana_object']
                        a.execute('SetMaterial', objects=[edgeobj], diffuse=color)
                        win.addObjects(edgeobj)
            else:
                a.execute('SetMaterial', objects=[v['ana_object']], diffuse=basincolor)
                           
    return[win, connectivity, mesh, t1, bundles, clusters]

def execution(self, context):
    return mainThreadActions().call(self.execution_mainthread, context)