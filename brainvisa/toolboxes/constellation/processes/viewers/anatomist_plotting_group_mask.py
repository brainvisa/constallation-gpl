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
* plotting the group masks
* the possibility to use the mesh : inflated, not inflated, group or individual

Main dependencies: PyQt

Author: Sandrine Lefranc, 2015
"""

#----------------------------Imports-------------------------------------------

# module PyGt4
from soma.qt_gui.qt_backend import QtGui

# axon python API module
from brainvisa.processes import Signature, ListOf, ReadDiskItem, Integer, \
    mainThreadActions, ValidationError

try:
    from brainvisa import anatomist as ana
except:
    pass


def validation():
    try:
        from brainvisa import anatomist as ana
    except:
        raise ValidationError(_t_("Anatomist not available"))


#----------------------------Header--------------------------------------------


name = "Anatomist Plotting Group Mask"
roles = ("viewer",)
userLevel = 0

signature = Signature(
    "group_masks", ListOf(
        ReadDiskItem("Mask Texture", "anatomist texture formats")),
    "white_mesh", ListOf(ReadDiskItem("White Mesh", "Aims mesh formats")),
    "min_width", Integer(),
    "min_height", Integer(),
)


#----------------------------Function------------------------------------------


def initialization(self):
    """Provides default values and link of parameters"""

    # optional value
    self.setOptional("min_width")
    self.setOptional("min_height")


def get_screen_config():
    """Collect the config of the screens :
                - numbers of screen,
                - size,
                - resolution.
    """
    # the screen contains all monitors
    desktop = QtGui.qApp.desktop()
    print "desktop size: %d x %d" % (desktop.width(), desktop.height())

    # collect data about each monitor
    monitors = []
    nmons = desktop.screenCount()
    print "there are %d monitors" % nmons
    for m in range(nmons):
        mg = desktop.availableGeometry(m)
        print "monitor %d: %d, %d, %d x %d" % (
            m, mg.x(), mg.y(), mg.width(), mg.height())
        monitors.append((mg.x(), mg.y(), mg.width(), mg.height()))

    # current monitor (test)
    curmon = desktop.screenNumber(QtGui.QCursor.pos())
    x, y, width, height = monitors[curmon]
    print "monitor %d: %d x %d (current)" % (curmon, width, height)

    return (curmon, width, height)


#----------------------------Main program--------------------------------------


def execution(self, context):
    """
    """
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
    nb_files = len(self.group_masks)

    # define the number of cases in the block
    nb_blocks = nb_rows*nb_columns

    # generate the widgets
    blocklist = []
    for element in range(14):
        blocklist.append(
            a.createWindowsBlock(nbRows=nb_columns, nbCols=nb_rows))

    # empty list to add the windows
    w = []

    # empty list to add the objects
    t = []

    count = 1
    c = 0
    for i in xrange(nb_files):
        # load an object from a file (mesh, texture)
        mesh = a.loadObject(self.white_mesh[i])
        roi_clustering = a.loadObject(self.group_masks[i])

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
                "Sagittal", block=blocklist[0], no_decoration=True)

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
                "Sagittal", block=blocklist[count], no_decoration=True)
            win2.addObjects(textured_mesh)
            w.append(win2)
            t.append(textured_mesh)
            if c == nb_blocks:
                count += 1
                c = 0

    return [w, t]