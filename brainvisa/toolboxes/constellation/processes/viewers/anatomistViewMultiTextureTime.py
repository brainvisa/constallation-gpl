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
import gtk

name = 'Anatomist view Texture Time'
roles = ('viewer',)
userLevel = 0

signature = Signature(
    'clustering_texture', ListOf(ReadDiskItem('Group Clustering Texture', 'anatomist texture formats')),
    'white_mesh', ListOf(ReadDiskItem('AimsBothWhite', 'Aims mesh formats')),
)


def initialization(self):
    pass
    

def execution(self, context):
    nb_tex = len(self.clustering_texture)
    a = ana.Anatomist()
    
    window = gtk.Window()
    # the screen contains all monitors
    screen = window.get_screen()
    print "screen size: %d x %d" % (gtk.gdk.screen_width(),gtk.gdk.screen_height())
    # collect data about each monitor
    monitors = []
    nmons = screen.get_n_monitors()
    print "there are %d monitors" % nmons
    for m in range(nmons):
        mg = screen.get_monitor_geometry(m)
        print "monitor %d: %d x %d" % (m,mg.width,mg.height)
        monitors.append(mg)

    # current monitor
    curmon = screen.get_monitor_at_window(screen.get_active_window())
    x, y, width, height = monitors[curmon]
    print "monitor %d: %d x %d (current)" % (curmon,width,height)  
    block = a.createWindowsBlock(nbCols=5, nbRows=4)
    
    w = []
    t = []
    for i in xrange(nb_tex):
        mesh = a.loadObject(self.white_mesh[i])
        texture = a.loadObject(self.clustering_texture[i])
        texture.setPalette(palette='random', absoluteMode=True)
        textured_mesh = a.fusionObjects([mesh, texture], method='FusionTexSurfMethod')
        a.execute('TexturingParams', objects=[textured_mesh], interpolation='rgb')
        win = a.createWindow('3D', block=block, no_decoration=True)
        win.addObjects(textured_mesh)
        w.append(win)
        t.append(textured_mesh)
    return [w, t]
