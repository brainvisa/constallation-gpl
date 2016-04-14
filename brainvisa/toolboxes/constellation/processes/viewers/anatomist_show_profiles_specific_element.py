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
* Connectivity profiles of a specific cortical element
* cortical element = vertex or region
* Connectivity profile on a textured mesh of the cortical surface in an
  iteractive way, by electing either a vertex or a cortical region.
      - option 1: vertex of ROI --> vertices of cortex,
      - option 2: vertex of cortex --> vertices of ROI,
      - option 3: cluster of ROI --> vertices of cortex,
      - option 4: vertex of ROI --> basins
      - option 5: cluster of ROI --> basins

Main dependencies:

Author: Sandrine Lefranc, 2015
"""

#----------------------------Imports-------------------------------------------


# axon python API module
from brainvisa.processes import Signature, ReadDiskItem

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


name = "Anatomist Show Connectivity Profiles of a Specific Cortical Element"
roles = ("viewer", )
userLevel = 0

signature = Signature(
    "connectivity_matrix", ReadDiskItem(
        "connectivity matrix", "aims readable volume formats",
        requiredAttributes={"ends_labelled": "mixed",
                            "reduced": "Yes",
                            "dense": "No",
                            "intersubject": "Yes"}),
    "white_mesh", ReadDiskItem("White Mesh", "anatomist mesh formats",
                               requiredAttributes={"side": "both",
                                                   "vertex_corr": "Yes"}),
    "gyrus_texture",
        ReadDiskItem("ROI texture", "anatomist texture formats",
                     requiredAttributes={"side": "both",
                                         "vertex_corr": "Yes"}),
    "basins_texture",
        ReadDiskItem("Label texture", "anatomist texture formats"), )


#----------------------------Function------------------------------------------


def initialization(self):
    self.linkParameters("white_mesh", "connectivity_matrix")
    self.linkParameters("gyrus_texture", "connectivity_matrix")
    self.linkParameters("basins_texture", "connectivity_matrix")


#----------------------------Main program--------------------------------------
def execution(self, context):
    """
    """
    # instance of anatomist
    a = ana.Anatomist()

    # load an object from a file
    mesh = a.loadObject(self.white_mesh)
    patch = a.loadObject(self.gyrus_texture)
    sparse = a.loadObject(self.connectivity_matrix)
    basins = a.loadObject(self.basins_texture)

    # create a fusionned multi object that contains all given objects
    conn = a.fusionObjects(
        [mesh, patch, sparse, basins], method="ConnectivityMatrixFusionMethod")
    if conn is None:
        raise ValueError(
            "could not fusion objects - matrix, mesh and "
            "labels texture may not correspond.")

    # create a new window and opens it
    win = a.createWindow("3D")

    # executes a command in anatomist application
    a.execute(
        "WindowConfig", windows=[win], light={"background": [0., 0., 0., 0.]})

    # add objects in windows
    win.addObjects(conn)

    # changes the selected button in windows menu.
    win.setControl("ConnectivityMatrixControl")

    return [win, conn, basins]
