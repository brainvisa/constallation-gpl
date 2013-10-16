from brainvisa.processes import *
try:
    from brainvisa import anatomist as ana
except:
    pass

def validation():
    try:
        from brainvisa import anatomist as ana
    except:
        raise ValidationError( _t_( 'Anatomist not available' ) )


name = 'Anatomist view connectivity matrix'
roles = ( 'viewer', )
userLevel = 0

signature = Signature(
    'connectivity_matrix',
        ReadDiskItem( 'Gyrus connectivity matrix', 'Matrix sparse' ),
    'white_mesh', ReadDiskItem( 'FreesurferMesh', 'anatomist mesh formats' ),
    'gyrus_texture',
        ReadDiskItem( 'Label texture', 'anatomist texture formats' ),
)


def initialization( self ):
    self.linkParameters( 'white_mesh', 'connectivity_matrix' )
    self.linkParameters( 'gyrus_texture', 'connectivity_matrix' )


def execution( self, context ):
    a = ana.Anatomist()
    mesh = a.loadObject( self.white_mesh )
    patch = a.loadObject( self.gyrus_texture )
    sparse = a.loadObject( self.connectivity_matrix )
    conn = a.fusionObjects( [ mesh, patch, sparse ],
        method='ConnectivityMatrixFusionMethod' )
    if conn is None:
        raise ValueError( 'could not fusion objects - matrix, mesh and ' \
            'labels texture may not correspond.' )
    win = a.createWindow( '3D' )
    win.addObjects( conn )
    win.setControl( 'ConnectivityMatrixControl' )

    return [ win, conn ]

