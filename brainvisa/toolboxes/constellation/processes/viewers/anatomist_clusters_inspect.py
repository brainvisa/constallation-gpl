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

signature = Signature(
    'clusters', ReadDiskItem('Connectivity ROI texture',
                             'aims texture formats'),
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


def inlineGUI(self, values, process_view, dummy, externalRunButton=True):
    widget = QtGui.QWidget()
    layout = QtGui.QVBoxLayout()
    widget.setLayout(layout)
    hlay = QtGui.QHBoxLayout()
    layout.addLayout(hlay)
    hlay.addStretch()
    btn = QtGui.QPushButton('Run')
    btn.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    hlay.addWidget(btn)
    #btn.clicked.connect(process_view._runButton)
    btn.connect(btn, QtCore.SIGNAL('clicked()'), process_view._runButton)
    self.gui = widget
    te = process_view.findChild(QtGui.QTextEdit)
    te.hide()

    return widget


def exec_main_thread(self, context, meshes, clusters, measurements,
        seed_gyri, matrix):
    print('exec_main_thread')
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
    print('exec.')
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

