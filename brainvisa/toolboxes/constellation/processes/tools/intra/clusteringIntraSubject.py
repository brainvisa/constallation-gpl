# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path

def validation():
  if not find_in_path( 'constelIntraSubjectClustering.py' ):
    raise ValidationError( 'constellation module is not here.' )

name = 'Clustering'
userLevel = 2

signature = Signature(
  'connectivity_matrix_reduced', ReadDiskItem( 'Reduced Connectivity Matrix', 'GIS image' ),
                 'gyri_texture', ReadDiskItem( 'FreesurferResampledBothParcellationType', 'Aims texture formats' ),
                   'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
            #'areaMin_threshold', Integer(),
                        'gyrus', Integer(),
                         'kmax', Integer(),
                  
               #'clustering_kopt', WriteDiskItem( 'Clustering kOpt', 'Aims texture formats' ),
               'clustering_time', WriteDiskItem( 'Clustering Time', 'Aims texture formats' ),
          #'clustering_k_medoids', WriteDiskItem( 'Patch Clustering Time', 'Aims texture formats' ),
         #'clustering_silhouette', WriteDiskItem( 'Clustering Silhouette Time', 'Aims texture formats' ),
  #'clustering_vertex_silhouette', WriteDiskItem( 'Clustering Vertex Silhouette Time', 'Aims texture formats' ),
       #'clustering_result_gyrus', WriteDiskItem( 'Gyrus Clustering Result', 'Text file' ),
        #'clustering_result_full', WriteDiskItem( 'Full Clustering Result', 'Text file' ),      
)

def initialization ( self ):
  #self.areaMin_threshold = 400.0
  self.kmax = 10
  self.setOptional( 'gyrus' )
  self.linkParameters( 'clustering_time', 'connectivity_matrix_reduced' )
  #self.linkParameters( 'clustering_time', 'clustering_kopt' )
  #self.linkParameters( 'clustering_k_medoids', 'clustering_time' )
  #self.linkParameters( 'clustering_silhouette', 'clustering_k_medoids' )
  #self.linkParameters( 'clustering_vertex_silhouette', 'clustering_silhouette' )
  #self.linkParameters( 'clustering_result_gyrus','connectivity_matrix_reduced' )
  #self.linkParameters( 'clustering_result_full','connectivity_matrix_reduced' )
  self.linkParameters( 'gyri_texture', 'white_mesh' )

def execution ( self, context ):
  context.write( 'The connectivity profiles of the region are clustered using k-medoids approach.' )
  if self.gyrus is not None:
    gyrus = self.gyrus # keep internal connections, put 0
  else:
    gyrus = os.path.basename( os.path.dirname( os.path.dirname( self.connectivity_matrix_reduced.fullPath() ) ) )
    gyrus = gyrus.strip('G')
  context.system( sys.executable, find_in_path( 'constelIntraSubjectClustering.py' ),
    '-m', self.connectivity_matrix_reduced,
    '-p', gyrus,
    '-g', self.gyri_texture,
    '-w', self.white_mesh,
    '-a', self.kmax,
    #'-k', self.clustering_kopt,
    '-t', self.clustering_time
    #'-d', self.clustering_k_medoids,
    #'-s', self.clustering_silhouette,
    #'-l', self.clustering_vertex_silhouette,
    #'-r', self.clustering_result_gyrus
    #'-f', self.clustering_result_full
  )
  context.write( 'OK' ) 