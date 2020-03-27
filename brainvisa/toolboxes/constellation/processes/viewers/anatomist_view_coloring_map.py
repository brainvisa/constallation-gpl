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
from __future__ import absolute_import
from brainvisa.processes import Signature, ReadDiskItem

# constel import
from constel.lib.utils.texturetools import create_relationship_region2neighbors
from constel.lib.utils.four_color_theorem import build_rules, get_best

# Anatomist
from six.moves import range


def validation(self):
    try:
        from brainvisa import anatomist as ana
    except ImportError:
        raise ValidationError(_t_("Anatomist not available"))
    ana.validation()


name = "Anatomist view 4-coloring Map"
userLevel = 2
# roles = ("viewer", )

signature = Signature(
    "ROIs_segmentation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"}),
    )


def initialization(self):
    pass


def execution(self, context):
    """
    """
    from brainvisa import anatomist as ana
    # create dictionnaire, relation betwenn state and neighbors
    items = create_relationship_region2neighbors(
        self.white_mesh.fullPath(), self.ROIs_segmentation.fullPath())

    # Build the set of rules.
    rules = build_rules(items)

    # list of colors
    colors = {"Red": [203, 0, 0], "Green": [64, 173, 38], "Blue": [0, 0, 142],
              "Yellow": [255, 217, 0], "Orange": [255, 129, 0],
              "Cyan": [0, 148, 189], "Magenta": [207, 3, 124]}

    # the expected optimal situation will be that all adjacent states have
    # different colors
    best = get_best(rules, len(items), len(rules), list(colors.keys()))

    # get all items/regions
    keys = sorted(items.keys())

    # create the RGB colors list
    RGB_colorslist = []
    for index in range(len(items)):
        print(str(keys[index]) + " is " + str(best.States[index]))
        RGB_colorslist.append(colors[str(best.States[index])])

    RGB_colors = [element for sublist in RGB_colorslist for element in sublist]
    print(RGB_colors)

    # instance of Anatomist
    a = ana.Anatomist()

    # view an object (window)
    win = a.createWindow("3D")

    # load objects
    mesh = a.loadObject(self.white_mesh)
    gyri = a.loadObject(self.ROIs_segmentation)

    # custom palette
    customPalette = a.createPalette("coloring_map")
    customPalette.setColors(colors=RGB_colors, color_mode="RGB")
    gyri.setPalette(customPalette)

    # fusion of the mesh with the gyri segmentation
    surftex = a.fusionObjects([mesh, gyri], method="FusionTexSurfMethod")

    # add the object in the windows
    win.addObjects(surftex)
    a.execute('SetMaterial', objects=[surftex])

    return [win, gyri, mesh, surftex]
