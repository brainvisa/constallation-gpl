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
*
*

Main dependencies:

Author: Sandrine Lefranc, 2015
"""

#----------------------------Imports-------------------------------------------


# axon python API module
from brainvisa.processes import *
try:
    from brainvisa import anatomist as ana
except:
    pass

def validation():
    try:
        from brainvisa import anatomist as ana
    except:
        raise ValidationError(_t_('Anatomist not available'))

from soma.path import find_in_path
from PyQt4 import QtGui


#----------------------------Header--------------------------------------------


name = 'Anatomist view Texture Time'
roles = ('viewer',)
userLevel = 0

signature = Signature(
    'clustering_texture', ListOf(
        ReadDiskItem('Connectivity ROI Texture', 'anatomist texture formats',
        requiredAttributes={"roi_autodetect":"No",
                            "roi_filtered":"No",
                            "averaged":"No",
                            "intersubject":"Yes",
                            "step_time":"Yes"})),
    'white_mesh', ListOf(ReadDiskItem('White Mesh', 'Aims mesh formats')),
)


#----------------------------Function------------------------------------------


def initialization(self):
    pass


#----------------------------Main program--------------------------------------


def get_screen_config():
    desktop = QtGui.qApp.desktop()
    print "desktop size: %d x %d" % (desktop.width(), desktop.height())
    monitors = []
    nmons = desktop.screenCount()
    print "there are %d monitors" % nmons
    for m in range(nmons):
        #mg = desktop.screen(m)
        mg = desktop.availableGeometry(m)
        print "monitor %d: %d, %d, %d x %d" % (m, mg.x(), mg.y(), mg.width(), mg.height())
        monitors.append((mg.x(), mg.y(), mg.width(), mg.height()))
#    # current monitor
#    curmon = screen.get_monitor_at_window(screen.get_active_window())
    curmon = desktop.screenNumber(QtGui.QCursor.pos())
#    print "monitor %d: %d x %d (current)" % (curmon,width,height)  
    #~print "monitor %d: %d x %d (current)" % (curmon,width,height)
    return (curmon, monitors[curmon])

    #window = gtk.Window()
    ## the screen contains all monitors
    #screen = window.get_screen()
    #print "screen size: %d x %d" % (gtk.gdk.screen_width(),gtk.gdk.screen_height())
    ## collect data about each monitor
    #monitors = []
    #nmons = screen.get_n_monitors()
    #print "there are %d monitors" % nmons
    #for m in range(nmons):
        #mg = screen.get_monitor_geometry(m)
        #print "monitor %d: %d x %d" % (m,mg.width,mg.height)
        #monitors.append(mg)

    ## current monitor
    #curmon = screen.get_monitor_at_window(screen.get_active_window())
    #x, y, width, height = monitors[curmon]
    #print "monitor %d: %d x %d (current)" % (curmon,width,height)

def execution(self, context):
    nb_tex = len(self.clustering_texture)
    a = ana.Anatomist()

    curmon, monitor = mainThreadActions().call(get_screen_config)
    block = a.createWindowsBlock(nbCols=3, nbRows=3)

    w = []
    t = []
    for i in xrange(nb_tex):
        mesh = a.loadObject(self.white_mesh[i])
        texture = a.loadObject(self.clustering_texture[i])
        texture.setPalette(palette='random', absoluteMode=True)
        textured_mesh = a.fusionObjects([mesh, texture], method='FusionTexSurfMethod')
        a.execute('TexturingParams', objects=[textured_mesh], interpolation='rgb')
        win = a.createWindow('Sagittal', block=block, no_decoration=False)
        win.addObjects(textured_mesh)
        w.append(win)
        t.append(textured_mesh)
    return [w, t]
