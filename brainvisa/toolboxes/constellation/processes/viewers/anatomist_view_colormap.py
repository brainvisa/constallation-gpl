###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

# Axon python API module
from __future__ import absolute_import
from __future__ import print_function
import numpy as np


# Axon python API module
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError
from brainvisa.processes import Boolean


def validation(self):
    try:
        from brainvisa import anatomist as ana
    except ImportError:
        raise ValidationError(_t_("Anatomist not available"))
    ana.validation()


name = "Anatomist view Constellation colormap"
userLevel = 2
# roles = ("viewer", )

signature = Signature(
    "ROIs_segmentation", ReadDiskItem(
        "ROI Texture", "Aims texture formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"},
        section="Inputs"),
    "white_mesh", ReadDiskItem(
        "White Mesh", "Aims mesh formats",
        requiredAttributes={"side": "both", "vertex_corr": "Yes"},
        section="Inputs"),
    "palette", WriteDiskItem(
        "4D Volume", "BrainVISA volume formats",
        section="Outputs"),
    "temporary_palette", Boolean(section="Options"),)


def initialization(self):
    pass


def execution(self, context):
    """
    """
    from brainvisa import anatomist as ana
    from soma import aims

    context.pythonSystem('constel_colormap.py',
                         self.ROIs_segmentation,
                         self.white_mesh,
                         self.palette)

    vol_palette = aims.read(self.palette.fullPath())
    RGBA_colors = np.asarray(vol_palette)[:, 0, 0, 0, 0].flatten().tolist()

    # instance of Anatomist
    a = ana.Anatomist()

    # view an object (window)
    win = a.createWindow("3D")

    # load objects
    mesh = a.loadObject(self.white_mesh)
    gyri = a.loadObject(self.ROIs_segmentation)

    # set the custom palette
    palette = a.createPalette('colormap')
    palette.setColors(colors=RGBA_colors, color_mode="RGBA")
    gyri.setPalette("colormap", absoluteMode=True)

    # set interpolation
    a.execute('TexturingParams', objects=[gyri], interpolation='rgb')

    # fusion of the mesh with the gyri segmentation
    surftex = a.fusionObjects([mesh, gyri], method="FusionTexSurfMethod")

    # add the object in the windows
    win.addObjects(surftex)
    a.execute('SetMaterial', objects=[surftex])

    return [win, gyri, mesh, surftex]
