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

# ----------------------------Imports------------------------------------------


# axon python API module
from __future__ import absolute_import
from brainvisa.processes import Signature, ReadDiskItem, getFormats


def validation():
    try:
        from brainvisa import anatomist as ana
    except ImportError:
        raise ValidationError(_t_("Anatomist not available"))
    ana.validation()

# ----------------------------Header-------------------------------------------


name = "Anatomist Show Connectivity Profiles of a Specific Cortical Element"
roles = ("viewer", )
userLevel = 2

signature = Signature(
    "connectivity_matrix", ReadDiskItem(
        "Connectivity matrix",
        getFormats("aims matrix formats").data + ['Sparse Matrix'],
        requiredAttributes={"ends_labelled": "all",
                            "reduced": "yes",
                            "intersubject": "yes",
                            # "individual": "no",
                            }),
    "white_mesh", ReadDiskItem("White Mesh", "anatomist mesh formats",
                               requiredAttributes={"side": "both",
                                                   "vertex_corr": "Yes"}),
    "gyrus_texture",
        ReadDiskItem("ROI texture", "anatomist texture formats",
                     requiredAttributes={"side": "both",
                                         "vertex_corr": "Yes"}),
    "basins_texture",
        ReadDiskItem("Connectivity ROI texture",
                     "anatomist texture formats"),
)


# ----------------------------Function-----------------------------------------


def initialization(self):
    def link_mesh(self, dummy):
        if self.connectivity_matrix is not None:
            cm = self.connectivity_matrix
            mesh_type = self.signature["white_mesh"]
            atts = {
                "subject": cm.get("subject"),
                "inflated": "No",
            }
            res = mesh_type.findValue(atts)
            if res is None:
                atts = {
                    "group_of_subjects": cm.get("group_of_subjects"),
                    "freesurfer_group_of_subjects":
                        cm.get("group_of_subjects"),
                    "inflated": "No",
                }
                res = mesh_type.findValue(atts)
            if res is None:
                res = cm
            return res

    def link_gyrus(self, dummy):
        if self.connectivity_matrix is not None:
            cm = self.connectivity_matrix
            gyrus_type = self.signature["gyrus_texture"]
            study = cm.get('study')
            if study == 'avg':
                atts = {
                    "group_of_subjects": cm.get("group_of_subjects"),
                    "freesurfer_group_of_subjects":
                        cm.get("group_of_subjects"),
                    "_type": "BothAveragedResampledGyri",
                }
                res = gyrus_type.findValue(atts)
                if res is not None:
                    return res
            atts = {
                "subject": cm.get("subject"),
                "_type": "BothResampledGyri",
            }
            res = gyrus_type.findValue(atts)
            if res is None:
                del atts["_type"]
                res = gyrus_type.findValue(atts)
            if res is None:
                res = cm
            return res

    def link_basins(self, dummy):
        if self.connectivity_matrix is not None:
            cm = self.connectivity_matrix
            basins_type = self.signature["basins_texture"]
            atts = {
                "center": cm.get("center"),
                "subject": cm.get("subject"),
                "_database": cm.get("_database"),
                "roi_filtered": "Yes",
                "gyrus": cm.get("gyrus"),
            }
            res = basins_type.findValue(atts)
            if res is None:
                atts = {
                    "group_of_subject": cm.get("group_of_subject"),
                    "_database": cm.get("_database"),
                    "roi_filtered": "Yes",
                    "gyrus": cm.get("gyrus"),
                }
                res = basins_type.findValue(atts)
            if res is None:
                res = cm
            return res

    self.linkParameters("white_mesh", "connectivity_matrix", link_mesh)
    self.linkParameters("gyrus_texture", "connectivity_matrix", link_gyrus)
    self.linkParameters("basins_texture", "connectivity_matrix", link_basins)


# ----------------------------Main program-------------------------------------
def execution(self, context):
    """
    """
    from bainvisa import anatomist as ana
    # instance of anatomist
    a = ana.Anatomist()

    objects_to_keep = []
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

    objects_to_keep += [win, conn, basins]
    return objects_to_keep
