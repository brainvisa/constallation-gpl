###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

"""
This script does the following:
* get screen config
* plotting the connectivity-based parcellation (clustering, basins)
* the possibility to use the mesh : inflated, not inflated, group or individual

Main dependencies: PyQt

Author: Sandrine Lefranc, 2015
"""

# ----------------------------Imports------------------------------------------
from __future__ import print_function

from __future__ import absolute_import
import math
import six
# module PyQt
from soma.qt_gui.qt_backend import QtGui

# axon python API module
from brainvisa.processes import Signature, ListOf, ReadDiskItem, Integer, \
    mainThreadActions, ValidationError, Boolean
from six.moves import range


def validation():
    try:
        from brainvisa import anatomist as ana
    except ImportError:
        raise ValidationError(_t_("Anatomist not available"))
    ana.validation()

# ----------------------------Header-------------------------------------------


name = "Anatomist Plotting Connectivity-based Parcellation"
roles = ("viewer",)
userLevel = 0

signature = Signature(
    "connectivity_based_parcellation", ListOf(
        ReadDiskItem("Connectivity ROI Texture", "anatomist texture formats")),
    "white_mesh", ListOf(ReadDiskItem("White Mesh", "Aims mesh formats",
                                      requiredAttributes={"side": "both"})),
    "min_width", Integer(),
    "min_height", Integer(),
    "prefer_inflated_meshes", Boolean(),
)


# ----------------------------Function-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters"""

    def link_meshes(self, dummy):
        meshes = []
        if self.prefer_inflated_meshes:
            infl1 = 'Yes'
            infl2 = 'No'
        else:
            infl1 = 'No'
            infl2 = 'Yes'
        mesh_type = self.signature["white_mesh"].contentType
        for parc in self.connectivity_based_parcellation:
            atts = dict(parc.hierarchyAttributes())
            print('subject:', parc.get("subject"))
            if parc.get("subject") is not None \
                    and parc.get("acquisition") is not None:
                if parc.get("group_of_subjects"):
                    del atts["group_of_subjects"]
            else:
                group = parc.get("group_of_subjects")
                if group is not None:
                    atts["freesurfer_group_of_subjects"] = group
                    print('group', group)
                    print('atts:', atts)
            mesh = mesh_type.findValue(
                atts,
                requiredAttributes={"inflated": infl1})
            if mesh is None:
                mesh = mesh_type.findValue(
                    atts,
                    requiredAttributes={"inflated": infl2})
            meshes.append(mesh)
        return meshes

    # optional value
    self.setOptional("min_width")
    self.setOptional("min_height")
    self.linkParameters("white_mesh",
                        ["connectivity_based_parcellation",
                         "prefer_inflated_meshes"],
                        link_meshes)


def get_screen_config():
    """Collect the config of the screens :
                - numbers of screen,
                - size,
                - resolution.
    """
    # the screen contains all monitors
    desktop = QtGui.qApp.desktop()
    print("desktop size: %d x %d" % (desktop.width(), desktop.height()))

    # collect data about each monitor
    monitors = []
    nmons = desktop.screenCount()
    print("there are %d monitors" % nmons)
    for m in range(nmons):
        mg = desktop.availableGeometry(m)
        print("monitor %d: %d, %d, %d x %d"
              % (m, mg.x(), mg.y(), mg.width(), mg.height()))
        monitors.append((mg.x(), mg.y(), mg.width(), mg.height()))

    # current monitor (test)
    curmon = desktop.screenNumber(QtGui.QCursor.pos())
    x, y, width, height = monitors[curmon]
    print("monitor %d: %d x %d (current)" % (curmon, width, height))

    return (curmon, width, height)


# ----------------------------Main program-------------------------------------


def execution(self, context):
    """
    """
    from brainvisa import anatomist as ana
    # instance of anatomist
    a = ana.Anatomist()

    # define screen config
    curmon, width, height = mainThreadActions().call(get_screen_config)

    # define the minimal values (width and height) of the image
    min_width = self.min_width
    min_height = self.min_height
    if min_width is None or min_height is None:
        min_width = 300
        min_height = 200

    # deduce the maximale number of lines and columns accepted
    nb_rows = width / min_width
    nb_columns = height / min_height

    # define the number of files
    nb_files = len(self.connectivity_based_parcellation)

    # define the number of cases in the block
    nb_blocks = nb_rows*nb_columns
    if nb_blocks > nb_files:
        # if fewer objects than the max possible number on screen: resize
        nb_columns = int(nb_columns / math.sqrt(float(nb_blocks) / nb_files))
        if nb_columns == 0:
            nb_columns = 1
        nb_rows = int(math.ceil(float(nb_files) / nb_columns))

    # generate the widgets
    blocklist = []
    for element in range(14):
        blocklist.append(
            a.createWindowsBlock(nbRows=nb_rows, nbCols=nb_columns))

    # empty list to add the windows
    w = []

    # empty list to add the objects
    t = []

    count = 1
    c = 0
    for i in six.moves.xrange(nb_files):
        # load an object from a file (mesh, texture)
        mesh = a.loadObject(self.white_mesh[min(i, nb_files - 1)])
        roi_clustering = a.loadObject(self.connectivity_based_parcellation[i])

        # assign a palette to object
        roi_clustering.setPalette(palette="random", absoluteMode=True)

        # create a fusionned multi object that contains all given objects
        textured_mesh = a.fusionObjects(
            [mesh, roi_clustering], method="FusionTexSurfMethod")

        # executes a command in anatomist application
        a.execute(
            "TexturingParams", objects=[textured_mesh], interpolation='rgb')

        # create the first window
        if i < (nb_blocks):
            # create a new window and opens it
            win = a.createWindow(
                "3D", block=blocklist[0], no_decoration=True)
            win.camera(view_quaternion=[0.5, 0.5, 0.5, 0.5])

            # add objects in windows
            win.addObjects(textured_mesh)

            # create a list with all windows
            w.append(win)

            # create a list with all objects
            t.append(textured_mesh)

        # create the others
        if i >= (nb_blocks) and (
                count * (nb_blocks) <= i < (count+1) * (nb_blocks)):
            c += 1
            win2 = a.createWindow(
                "3D", block=blocklist[count], no_decoration=True)
            win2.camera(view_quaternion=[0.5, 0.5, 0.5, 0.5])
            win2.addObjects(textured_mesh)
            w.append(win2)
            t.append(textured_mesh)
            if c == nb_blocks:
                count += 1
                c = 0

    return [w, t]
