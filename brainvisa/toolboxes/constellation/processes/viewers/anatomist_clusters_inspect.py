###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

from __future__ import print_function
# Axon python API module
from brainvisa.processes import Signature, ReadDiskItem, mainThreadActions
from soma import aims

# Anatomist
from brainvisa import anatomist
from soma.qt_gui.qt_backend import QtGui, QtCore

# constellation module
from constel.anatomist.clusters_inspect import ClustersInspectorWidget, \
    load_clusters_instpector_files

# temp
import pandas
import numpy as np


name = 'Anatomist clusters inspect tool'
userLevel = 0

signature = Signature(
    'clusters', ReadDiskItem('Connectivity ROI texture',
                             'aims texture formats', 
                             requiredAttributes={'step_time': 'Yes'}),
    'mesh', ReadDiskItem('White Mesh', 'aims mesh formats'),
    #'clusters_measurements', ReadDiskItem('?'),
    'seed_gyri', ReadDiskItem('ROI texture', 'aims texture formats'),
    'reduced_matrix', ReadDiskItem('Connectivity matrix',
                                   'aims matrix formats'),
)


def initialization(self):
    self.linkParameters('mesh', 'clusters')
    self.linkParameters('seed_gyri', 'mesh')
    self.linkParameters('reduced_matrix', 'clusters')


def exec_main_thread(self, context, meshes, clusters, measurements,
        seed_gyri, matrix):
    if hasattr(self, 'gui'):
        gui = self.gui
        parent = gui.parentWidget()
        gui.setParent(None)
        del self.gui
    else:
        te = context.findChild(QtGui.QTextEdit)
        parent = te.parentWidget()
        #parent.removeWidget(te)
        #te.setParent(None)
        te.hide()
    gui = QtGui.QWidget()
    gui.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
    parent.insertWidget(1, gui)
    layout = QtGui.QVBoxLayout()
    gui.setLayout(layout)
    self.gui = gui
    layout = self.gui.layout()
    while layout.count() > 1:
        old_item = layout.itemAt(1)
        print('remove item:', old_item)
        w = old_item.widget()
        layout.removeItem(layout.itemAt(1))
        w.setParent(None) # should delete it also
    cw = ClustersInspectorWidget(
        meshes, clusters, measurements=measurements, seed_gyri=seed_gyri,
        matrix=matrix)
    layout.addWidget(cw)
    cw.show()
    #return cw


def execution(self, context):
    meshes, clusters, measurements, seed_gyri, matrix \
        = load_clusters_instpector_files([self.mesh.fullPath()],
                                         [self.clusters.fullPath()],
                                         None,
                                         [self.seed_gyri.fullPath()],
                                         self.reduced_matrix.fullPath())
    # temp
    measurements = dict(
        (i, pandas.DataFrame(np.random.ranf((i + 2, 4)),
                             columns=('size', 'homogeneity', 'conn_density',
                                      'other')))
        for i in range(max([len(clusters_tex) for clusters_tex in clusters])))

    return mainThreadActions().call(
        self.exec_main_thread, context, meshes, clusters, measurements,
        seed_gyri, matrix)

