# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 17:02:56 2015

@author: sl236442
"""

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
#import gtk
from numpy import arange

name = 'Anatomist view Fusion Smooth Time'
roles = ('viewer',)
userLevel = 0

signature = Signature(
    'clustering_texture_1', ListOf(
        ReadDiskItem('Connectivity ROI Texture', 'anatomist texture formats',
        requiredAttributes={"roi_autodetect":"No",
                            "roi_filtered":"No",
                            "averaged":"No",
                            "intersubject":"Yes",
                            "step_time":"Yes"})),
    'clustering_texture_2', ListOf(
        ReadDiskItem('Connectivity ROI Texture', 'anatomist texture formats',
        requiredAttributes={"roi_autodetect":"No",
                            "roi_filtered":"No",
                            "averaged":"No",
                            "intersubject":"Yes",
                            "step_time":"Yes"})),
    'white_mesh', ListOf(ReadDiskItem('AimsBothInflatedWhite', 'Aims mesh formats')),
    #'k_time', Integer(),
)


def initialization(self):
    self.k_time = 3 
    

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

    # current monitor
    curmon = desktop.screenNumber(QtGui.QCursor.pos())
    x, y, width, height = monitors[curmon]
    print "monitor %d: %d x %d (current)" % (curmon,width,height)
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
    nb_tex = len(self.clustering_texture_1)
    a = ana.Anatomist()

    curmon, monitor = mainThreadActions().call(get_screen_config)

    block = a.createWindowsBlock(nbCols=5, nbRows=4)

    w = []
    t = []
    for i in xrange(nb_tex):
        mesh = a.loadObject(self.white_mesh[0])
        texture1 = a.loadObject(self.clustering_texture_1[i])
        texture2 = a.loadObject(self.clustering_texture_2[i])
        texture1.setPalette(palette='random', absoluteMode=True)
        texture2.setPalette(palette='random', absoluteMode=True)
        multi_textures = a.fusionObjects([texture1, texture2], method='FusionMultiTextureMethod')
        textured_mesh = a.fusionObjects([mesh, multi_textures], method='FusionTexSurfMethod')
        a.execute('TexturingParams', objects=[texture1, texture2], interpolation='rgb')
        win = a.createWindow('Sagittal', block=block, no_decoration=True)
        win.addObjects(textured_mesh)
        w.append(win)
        t.append(textured_mesh)
    return [w, t]
