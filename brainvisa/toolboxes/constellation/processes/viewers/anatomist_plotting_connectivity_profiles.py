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
* plotting the connectivity profiles
* the possibility to use the mesh : inflated, not inflated, group or individual

Main dependencies: PyQt
"""

# ----------------------------Imports------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import math
import six

# module PyGt4
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


name = "Anatomist Plotting Connectivity Profiles"
roles = ("viewer",)
userLevel = 2

signature = Signature(
    "connectivity_profiles", ListOf(
        ReadDiskItem("Connectivity Profile Texture",
                     "anatomist texture formats")),
    "white_mesh", ListOf(ReadDiskItem("White Mesh", "Anatomist mesh formats")),
    "min_width", Integer(),
    "min_height", Integer(),
    "prefer_inflated_meshes", Boolean(),
    "max_views", Integer()
)


# ----------------------------Function-----------------------------------------


def initialization(self):
    """Provides default values and link of parameters"""

    def link_mesh(self, dummy):
        if self.connectivity_profiles is not None:
            mesh_type = self.signature["white_mesh"].contentType
            meshes = []
            for profile in self.connectivity_profiles:
                side = profile.get('side')
                if not side:
                    side = 'both'
                atts = {'side': side}
                if self.prefer_inflated_meshes:
                    atts['inflated'] = 'Yes'
                else:
                    atts['inflated'] = 'No'
                mesh = mesh_type.findValue(profile, requiredAttributes=atts)
                if mesh is None:
                    if self.prefer_inflated_meshes:
                        atts['inflated'] = 'No'
                    else:
                        atts['inflated'] = 'Yes'
                    mesh = mesh_type.findValue(profile,
                                               requiredAttributes=atts)
                meshes.append(mesh)
            if len(meshes) >= 2:
                for mesh in meshes[1:]:
                    if mesh != meshes[0]:
                        return meshes
                meshes = [meshes[0]]
            if meshes == [None]:
                return []
            return meshes

    # optional value
    self.setOptional("min_width")
    self.setOptional("min_height")
    self.linkParameters('white_mesh',
                        ['connectivity_profiles', 'prefer_inflated_meshes'],
                        link_mesh)
    self.max_views = 10


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

    # define the number of files
    if self.max_views > 0:
        nb_files = min(len(self.connectivity_profiles), self.max_views)
    else:
        # no limit
        nb_files = len(self.connectivity_profiles)

    # define the minimal values (width and height) of the image
    min_width = self.min_width
    min_height = self.min_height
    if min_width is None or min_height is None:
        min_width = 300
        min_height = 200
        if width / min_width > nb_files:
            min_width = width / nb_files
            min_height = height
            if min_width > 800:
                min_width = 800
            if min_height > 600:
                min_height = 600

    # deduce the maximale number of lines and columns accepted
    nb_rows = width / min_width
    nb_columns = height / min_height

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
        block = a.createWindowsBlock(nbRows=nb_rows, nbCols=nb_columns)
        blocklist.append(block)

    # empty list to add the windows
    w = []

    # empty list to add the objects
    t = []

    count = 1
    c = 0
    vmin = 0
    vmax = 0
    textures = []
    for i in six.moves.xrange(nb_files):
        # load an object from a file (mesh, texture)
        mesh_i = i
        if i >= len(self.white_mesh):
            mesh_i = -1
        mesh = a.loadObject(self.white_mesh[mesh_i])
        roi_clustering = a.loadObject(self.connectivity_profiles[i])
        tex_info = roi_clustering.getInfos()
        tmin, tmax = tex_info['texture']['textureMin'], \
            tex_info['texture']['textureMax']
        vmin, vmax = min(vmin, tmin), max(vmax, tmax)

        # assign a palette to object
        roi_clustering.setPalette(palette="white_blue_red")
        textures.append(roi_clustering)

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
            if i == 0:
                blocklist[0].internalWidget.widget.resize(
                    nb_columns * min_width, nb_rows * min_height)
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

    # set the same palette values on all
    # arbitrarily set max to 30%
    max_tex = vmin + (vmax - vmin) * 0.3
    a.setObjectPalette(textures, absoluteMode=True, minVal=vmin,
                       maxVal=max_tex)

    return [w, t]
