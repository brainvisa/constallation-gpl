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


# Axon python API module
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError
from brainvisa.processes import Choice
from brainvisa.processes import OpenChoice
from brainvisa.processes import ListOf
from brainvisa.processes import Boolean


def validation(self):
    try:
        from constel.lib.utils.filetools import select_ROI_number
        from constel.lib.utils.filetools import read_nomenclature_file
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")
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
    "colors_dict", ReadDiskItem("Colors dictionary",
                                "JSON file", section="Options"),
    "nb_colors", Choice(
        "minimal", "exclusive", "5", "6", "7", "8", "9", "10", "11",
        section="Options"
    ),
    "regions_nomenclature", ReadDiskItem("Nomenclature ROIs File",
                                         "Text File",
                                         section="Options"),
    "default_regions", ListOf(OpenChoice(), section="Options"),
    "palette", WriteDiskItem(
        "4D Volume", "BrainVISA volume formats",
        section="Outputs"),
    "view_coloring", Boolean(section="Options"))


def initialization(self):
    from constel.lib.utils.filetools import read_nomenclature_file
    from soma import aims
    # self.setOptional("palette")
    self.setOptional("regions_nomenclature")
    self.setOptional("default_regions")
    self.setOptional("colors_dict")
    self.view_coloring = True

    def link_default_regions(self, dummy):
        """
        """
        if self.regions_nomenclature is not None:
            self.default_regions = None
            s = []
            s += read_nomenclature_file(
                self.regions_nomenclature.fullPath(), mode=2)
            self.signature["default_regions"] = ListOf(Choice(*s),
                                                       section="Options")
            self.setOptional("default_regions")
            self.changeSignature(self.signature)

    # def link_nb_colors_to_colors_dict(self, dummy):
    #     if self.colors_dict is not None:
    #         colors_dict = aims.read(self.colors_dict)
    #         print(colors_dict)
    #         s = ["minimal"]
    #         for n in colors_dict.keys():
    #             if int(n) >= 5:
    #                 s += str(n)
    #         self.signature["nb_colors"] = Choice(*s, section="Options")

    self.linkParameters(None,
                        "regions_nomenclature",
                        link_default_regions)

    # self.linkParameters(None,
    #                     "colors_dict",
    #                     link_nb_colors_to_colors_dict)


def execution(self, context):
    """
    """
    from brainvisa import anatomist as ana
    from soma import aims
    from constel.lib.utils.filetools import select_ROI_number

    # Selects the label numbers corresponding to label names
    labels = []
    for region in self.default_regions:
        label = select_ROI_number(self.regions_nomenclature.fullPath(),
                                  region)
        labels.append(int(label))

    context.pythonSystem('constel_colormap.py',
                         self.ROIs_segmentation,
                         self.white_mesh,
                         self.colors_dict,
                         self.nb_colors,
                         labels,
                         self.palette)

    if self.view_coloring:
        vol_palette = aims.read(self.palette.fullPath())
        RGBA_colors = vol_palette.np['v'].flatten().tolist()
        if vol_palette['v'].shape[-1] == 4:
            mode = 'RGBA'
        else:
            mode = 'RGB'

        # instance of Anatomist
        a = ana.Anatomist()

        # view an object (window)
        win = a.createWindow("3D")

        # load objects
        mesh = a.loadObject(self.white_mesh)
        gyri = a.loadObject(self.ROIs_segmentation)

        # set the custom palette
        palette = a.createPalette('constel_colormap')
        palette.setColors(colors=RGBA_colors, color_mode=mode)
        gyri.setPalette("constel_colormap", minVal=0., maxVal=1.)

        # set interpolation
        a.execute('TexturingParams', objects=[gyri], interpolation='rgb')

        # fusion of the mesh with the gyri segmentation
        surftex = a.fusionObjects([mesh, gyri], method="FusionTexSurfMethod")

        # add the object in the windows
        win.addObjects(surftex)

        return [win, gyri, mesh, surftex]
