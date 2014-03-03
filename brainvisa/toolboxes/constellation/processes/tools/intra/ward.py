from brainvisa.processes import *
from soma.path import find_in_path
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy

def validation():
    if not find_in_path( 'constelConnectionDensityTexture' ):
        raise ValidationError( 'constellation module is not here.' )

name = 'Clustering Ward'
userLevel = 2

signature = Signature( 
    'kmax', Integer(),
    'patch', Integer(),
    'group_matrix', ReadDiskItem('Group Matrix', 'GIS image'),
    'average_mesh', ReadDiskItem('BothAverageBrainWhite', 
                                 'BrainVISA mesh formats'),
    'gyri_texture', ListOf(
        ReadDiskItem('FreesurferResampledBothParcellationType', 
                     'Aims texture formats')),
    'tex_time', ListOf(WriteDiskItem('Group Clustering Time', 
                                            'BrainVISA texture formats')),
    'output_directory', ReadDiskItem('Directory', 'Directory'),
)

def initialization (self):
    pass

def execution(self, context):
    '''Use hieararchical clustering to identify patterns.
    '''
        
    for x in self.gyri_texture:
        args += [ '-g', x ]
    for t in self.tex_time:
        args += [ '-t', t ]
    args += ['-k', self.kmax, '-l', self.patch, '-c', self.group_matrix, 
        '-m', self.avg_mesh, '-o', self.output_directory]
    context.system('python', find_in_path( 'constelClusteringWard.py' ),
        *args)