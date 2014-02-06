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

name = 'Anatomist view connectivity regions on small brain'
userLevel = 0
roles = ( 'viewer', )

signature = Signature(
  'bundles', ReadDiskItem( 'Fascicles bundles', 'Aims bundles' ),
  'RawT1Image', ReadDiskItem('Raw T1 MRI', 'NIFTI-1 image'),
  'dw_to_t1', ReadDiskItem( 'Transformation matrix', 'Transformation matrix' ),
  'white_mesh', ReadDiskItem( 'BothAverageBrainWhite', 'anatomist mesh formats' ),
  'clustering_texture', ReadDiskItem( 'Group Clustering Texture', 'anatomist texture formats' ),
)

def initialization( self ):
  self.linkParameters( 'bundles', 'clustering_texture' )
  self.linkParameters( 'dw_to_t1', 'RawT1Image' )


def execution_mainthread( self, context ):
  a = ana.Anatomist()
  mesh = a.loadObject( self.white_mesh )
  clusters = a.loadObject( self.clustering_texture )
  bundles = a.loadObject( self.bundles )
  t1 = a.loadObject( self.RawT1Image )
  r = a.createReferential()
  cr = a.centralRef
  bundles.assignReferential(r)
  a.loadTransformation(self.dw_to_t1.fullPath(), r, cr)
  
  connectivity = a.fusionObjects( [ mesh, clusters, bundles, t1 ],
      method = 'FusionTexMeshImaAndBundlesToROIsAndBundlesGraphMethod' )
  if connectivity is None:
    raise ValueError( 'could not fusion objects - T1, mesh, texture and bundles' )

  wgroup = a.createWindowsBlock(nbCols=2)
  win = a.createWindow('3D', block=wgroup)
  win2 = a.createWindow('3D', block=wgroup)
  br = a.createWindow('Browser', block=wgroup)
  win.addObjects( connectivity )
  br.addObjects( connectivity )
  a.execute( 'SetControl', windows = [win], control = 'BundlesSelectionControl' )
  action = win.view().controlSwitch().getAction( 'BundlesSelectionAction' )
  action.secondaryView = win2

  return[win, win2, br, connectivity]

def execution(self, context):
  return mainThreadActions().call(self.execution_mainthread, context)
