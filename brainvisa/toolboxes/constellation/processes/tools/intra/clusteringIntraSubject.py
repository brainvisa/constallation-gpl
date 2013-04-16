# -*- coding: utf-8 -*-
from brainvisa.processes import *
from soma.path import find_in_path

name = '15 - Clustering'
userLevel = 2

signature = Signature(
  'connectivity_matrix_reduced', ReadDiskItem( 'Reduced Connectivity Matrix', 'GIS image' ),
            'gyri_segmentation', ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ),
                   'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
            'areaMin_threshold', Integer(),
                 'vertex_index', ReadDiskItem( 'Vertex Index', 'Text file' ),
                  'patch_label', Integer(),
                  
               'clustering_kopt', WriteDiskItem( 'Clustering kOpt', 'Aims texture formats' ),
               'clustering_time', WriteDiskItem( 'Clustering Time', 'Aims texture formats' ),
          'clustering_k_medoids', WriteDiskItem( 'Patch Clustering Kmedoids Time', 'Aims texture formats' ),
         'clustering_silhouette', WriteDiskItem( 'Patch Clustering Silhouette Width Time', 'Aims texture formats' ),
  'clustering_vertex_silhouette', WriteDiskItem( 'Patch Clustering Vertex Silhouette Width Time', 'Aims texture formats' ),
       'clustering_result_gyrus', WriteDiskItem( 'Gyrus Clustering Result', 'Text file' ),
        'clustering_result_full', WriteDiskItem( 'Full Clustering Result', 'Text file' ),      
)

def initialization ( self ):
  self.areaMin_threshold = 400.0
  self.setOptional( 'patch_label' )
  self.linkParameters( 'clustering_kopt', 'connectivity_matrix_reduced' )
  self.linkParameters( 'clustering_time', 'clustering_kopt' )
  self.linkParameters( 'clustering_k_medoids', 'clustering_time' )
  self.linkParameters( 'clustering_silhouette', 'clustering_k_medoids' )
  self.linkParameters( 'clustering_vertex_silhouette', 'clustering_silhouette' )
  self.linkParameters( 'vertex_index','connectivity_matrix_reduced' )
  self.linkParameters( 'clustering_result_gyrus','connectivity_matrix_reduced' )
  self.linkParameters( 'clustering_result_full','connectivity_matrix_reduced' )
  self.linkParameters( 'gyri_segmentation', 'white_mesh' )

def execution ( self, context ):
  context.write( 'The connectivity profiles of the region are clustered using k-medoids approach.' )
  if self.patch_label is not None:
    patch_label = self.patch_label # keep internal connections, put 0
  else:
    patch_label = os.path.basename( os.path.dirname( os.path.dirname( self.connectivity_matrix_reduced.fullPath() ) ) )
    patch_label = patch_label.strip('G')
  context.system( 'python', find_in_path( 'clusteringIntrasubject.py' ),
    '-m', self.connectivity_matrix_reduced,
    '-p', patch_label,
    '-g', self.gyri_segmentation,
    '-w', self.white_mesh,
    '-a', self.areaMin_threshold,
    '-v', self.vertex_index,
    '-k', self.clustering_kopt,
    '-t', self.clustering_time,
    '-d', self.clustering_k_medoids,
    '-s', self.clustering_silhouette,
    '-l', self.clustering_vertex_silhouette,
    '-r', self.clustering_result_gyrus,
    '-f', self.clustering_result_full
  )
  context.write( 'OK' ) 