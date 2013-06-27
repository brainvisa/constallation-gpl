#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
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
from soma import aims
import numpy
import roca.lib.textureTools as TT
import roca.lib.connectivity.matrix.tools as Mat

name = 'Anatomist view connectivity texture on small brains'
userLevel = 2
roles = ( 'viewer', )

signature = Signature(
  'mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
  'connectivity_matrix', ReadDiskItem( 'Reduced connectivity matrix', 'aims readable volume formats' ),
  'basins_texture', ReadDiskItem( 'Filtered Watershed', 'anatomist texture formats' ),
  'clustering_texture', ReadDiskItem( 'Clustering Texture', 'anatomist texture formats' )
)

def initialization( self):
  self.linkParameters( 'connectivity_matrix', 'mesh' )
  self.linkParameters( 'basins_texture', 'connectivity_matrix' )
  self.linkParameters( 'clustering_texture', 'connectivity_matrix' )

def execution_mainthread( self, context ):
  a = ana.Anatomist()
  mesh = a.loadObject( self.mesh )
  #matrix = a.loadObject( self.connectivity_matrix )
  #basins = a.loadObject( self.basins_texture )
  anaclusters = a.loadObject( self.clustering_texture )
  anaclusters.setPalette( palette='Blue-Red-fusion' )
  a.execute( "TexturingParams", objects=[anaclusters], interpolation = 'rgb' )
  matrix = aims.read( self.connectivity_matrix.fullPath() )
  matrix = numpy.asarray( matrix )
  matrix = matrix.reshape( matrix.shape[:2] )
  basins = aims.read( self.basins_texture.fullPath() )
  # abasins = basins[0].arraydata()
  clusters = a.toAimsObject( anaclusters )
  aclusters = clusters[0].arraydata()
  aimsmesh = a.toAimsObject( mesh )
  avertex = numpy.asarray( aimsmesh.vertex() )
  reducedMatrix = Mat.connMatrixParcelsToTargets( matrix, clusters, 0 )
  mat = numpy.asarray( reducedMatrix )
  mat = mat.reshape( mat.shape[:2] )
  
  graph = aims.Graph( 'RoiArg' )
  bbmin, bbmax = mesh.boundingbox()
  graph[ 'boundingbox_min' ] = list( bbmin )
  graph[ 'boundingbox_max' ] = list( bbmax )
  regions = [ x for x in numpy.unique( aclusters ) if x != 0 ]
  for rnum in regions:
    vertex = graph.addVertex( 'roi' )
    aims.GraphManip.storeAims( graph, vertex, 'aims_Tmtktri', aimsmesh )

  anagraph = a.toAObject( graph )
  anagraph.releaseAppRef()
  anagraph.setReferentialInheritance( mesh )
  a.unmapObject( anagraph )
  for i, vertex in enumerate( graph.vertices() ):
    anavertex = vertex[ 'ana_object' ]
    current_tex = TT.oneTargetDensityTargetsRegroupTexture( mat[i], basins )
    anatex = a.toAObject( current_tex )
    anatex.releaseAppRef()
    a.unmapObject( anatex )
    mesh2 = mesh.clone( True ) # shallow copy
    mesh2.setReferential( mesh.referential )
    texsurf = a.fusionObjects( [ mesh2, anatex ], method='FusionTexSurfMethod' )
    a.unmapObject( texsurf )
    oldmesh = [ x for x in anavertex ][0]
    anavertex.setReferentialInheritance( mesh2 )
    anavertex.erase( oldmesh )
    anavertex.insert( texsurf )
    clustindices = numpy.where( aclusters == regions[i] )[0]
    vertices = avertex[ clustindices ]
    cent = numpy.average( vertices, axis=0 )
    vertex[ 'center' ] = cent
    vertex[ 'cluster_index' ] = i
  anagraph.setChanged()
  anagraph.notifyObservers()
  a.mapObject( anagraph )
  anagraph.setMaterial( diffuse=[ 0.8, 0.8, 0.8, 1. ] )
  
  tex = a.fusionObjects( [ mesh, anaclusters  ], method='FusionTexSurfMethod' )

  wgroup = a.createWindowsBlock( nbCols=2 )
  win = a.createWindow( '3D', block=wgroup )
  win2 = a.createWindow( '3D', block=wgroup )
  br = a.createWindow( 'Browser', block=wgroup )
  win.addObjects( tex )
  win.addObjects( anagraph )
  br.addObjects( anagraph )
  #a.execute( 'Select', objects=[ x[ 'ana_object' ] for x in graph.vertices() ] )
  a.execute( 'SetControl', windows=[win], control='BundlesSelectionControl' )
  action = win.view().controlSwitch().getAction( 'BundlesSelectionAction' )
  action.secondaryView = win2

  return [ mesh, anagraph, anaclusters, win, br, tex, win2 ]

def execution( self, context ):
  return mainThreadActions().call( self.execution_mainthread, context )


    
  