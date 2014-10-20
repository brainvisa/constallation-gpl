# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 09:35:29 2014

@author: sl236442
"""

# Axon python API module
from brainvisa.processes import *
from soma.path import find_in_path


# Plot connectomist module
def validation():
    """This function is executed at BrainVisa startup when the process is loaded.

    It checks some conditions for the process to be available.
    """
    if not find_in_path("comistFiberOversampler"):
        raise ValidationError(
            "Please make sure that connectomist module is installed.")

name = "Extract clusters"
userLevel = 2


# Argument declaration
signature = Signature(
    "white_mesh", ReadDiskItem("Mesh", "Aims mesh formats"),
    "clustering_texture", ReadDiskItem(
        "Group Clustering Time", "Aims texture formats"),
    "number_of_clusters", Integer(),
    "transfo_joy", ReadDiskItem(
        "Transform Raw T1 MRI to Talairach-AC/PC-Anatomist",
        "Transformation matrix"),
    "transfo_morpho", ReadDiskItem(
        "Transform Raw T1 MRI to Talairach-AC/PC-Anatomist",
        "Transformation matrix"),
    "output_database", Choice()
)



def initialization(self):
    """Provides default values and link of parameters
    """
    databases = [h.name for h in neuroHierarchy.hierarchies()
                 if h.fso.name == "brainvisa-3.2.0"]
    self.signature["output_database"].setChoices(*databases)
    if len(databases) != 0:
        self.output_database = databases[0]
    else:
        self.signature["output_database"] = OpenChoice()


def execution(self, context):
    clustering_texture = aims.read(self.clustering_texture.fullPath())
    try:
        assert self.number_of_clusters <= (clustering_texture.size() - 1)
    except AssertionError:
        context.write("ERROR: the number of clusters should be 1 to ",
                      clustering_texture.size() - 1)

    clusters_texture = aims.TimeTexture_S16()
    clusters_texture[0].assign(
        clustering_texture[self.number_of_clusters-1].arraydata())
    mesh = aims.read(self.white_mesh.fullPath())
    subject = os.path.basename(
        os.path.dirname(self.clustering_texture.fullPath()))
    gyrus = os.path.basename(
        os.path.dirname(os.path.dirname(
                        os.path.dirname(self.clustering_texture.fullPath()))))

    for label in range(1, self.number_of_clusters + 1):
        cluster_submesh = aims.SurfaceManip.meshExtract(
            mesh, clusters_texture, label)[0]
        path = (self.output_database + '/t1-1mm-1/' + subject +
                '/default_acquisition/default_analysis/segmentation/mesh/')
        if not os.path.exists(path):
            os.makedirs(path)
        
        name = subject + '_' + gyrus +'_cluster' + str(label) + '.gii'
        ofile = path + name
        context.write("--> SUBMESH " + str(label) + ": ", ofile)
        aims.write(cluster_submesh,  ofile)
    
        transfo_joy = aims.read(self.transfo_joy.fullPath())
        transfo_morpho = aims.read(self.transfo_morpho.fullPath())
        transfo_target = transfo_joy * transfo_morpho
        
        aims.SurfaceManip.meshTransform(cluster_submesh, transfo_target)
        path_t = (self.output_database + '/t1-1mm-1/' + subject +
                '/default_acquisition/default_analysis/segmentation/mesh/')
        name_t = (subject + '_' + gyrus +'_cluster' + str(label) +
                  '_transfo_to_target_subject.gii')
        ofile_t = path_t + name_t
        context.write("--> SUBMESH " + str(label) + ": ", ofile_t)
        aims.write(cluster_submesh,  ofile_t)
        
        