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
* defines a Brainvisa process
    - the signature of the inputs/ouputs,
    - the interlinkages between inputs/outputs.
* executes the command "":

Main dependencies: axon python API, soma-base, constel

Author: Sandrine Lefranc, 2015
"""

# ----------------------------Imports------------------------------------------


# system module
from __future__ import absolute_import
import numpy
import pylab

# scipy library
from scipy.spatial.distance import pdist
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import dendrogram

# axon python API module
from brainvisa.processes import Choice
from brainvisa.processes import Boolean
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem

# soma module
from soma import aims


# ----------------------------Header-------------------------------------------


name = "Dendrogram"
userLevel = 2

signature = Signature(
    # --inputs--
    "connectivity_matrix", ReadDiskItem(
        "Connectivity Matrix", "GIS image",
        requiredAttributes={"ends_labelled": "mixed",
                            "reduced": "No",
                            "dense": "No",
                            "intersubject": "Yes"}),
    "transpose", Boolean(),
    "linkage_method_X", Choice("single", "complete", "average", "weighted",
                               "centroid", "median", "ward"),
    "linkage_method_Y", Choice("single", "complete", "average", "weighted",
                               "centroid", "median", "ward"),
    "outdir", ReadDiskItem("Directory", "Directory"))


# ----------------------------Functions----------------------------------------


def initialization(self):
    """
    """
    self.distance = "Euclidean"
    self.method_1 = "centroid"
    self.method_2 = "average"
    self.linkParameters("outdir", "connectivity_matrix")


# ----------------------------Main program-------------------------------------


def execution(self, context):
    """
    """
    # Load connectivity matrix
    redmat = aims.read(self.connectivity_matrix.fullPath())
    if self.transpose:
        matrix = numpy.asarray(redmat)[:, :, 0, 0].T
    else:
        matrix = numpy.asarray(redmat)[:, :, 0, 0]

    # Calculate distance matrix
    dmat = squareform(pdist(matrix))

    # Compute and plot first dendrogram
    fig = pylab.figure()
    axdendro1 = fig.add_axes([0.09, 0.1, 0.2, 0.6])
    Y = linkage(dmat, method=str(self.linkage_method_X))
    Z1 = dendrogram(Y, orientation="right")
    axdendro1.set_xticks([])
    axdendro1.set_yticks([])

    # Compute and plot second dendrogram.
    axdendro2 = fig.add_axes([0.3, 0.71, 0.6, 0.2])
    Y = linkage(dmat, method=str(self.linkage_method_Y))
    Z2 = dendrogram(Y)
    axdendro2.set_xticks([])
    axdendro2.set_yticks([])

    # Plot distance matrix.
    axmatrix = fig.add_axes([0.3, 0.1, 0.6, 0.6])
    index1 = Z1["leaves"]
    index2 = Z2["leaves"]
    dmat = dmat[index1, :]
    dmat = dmat[:, index2]
    im = axmatrix.matshow(dmat, aspect="auto", origin="lower")
    axmatrix.set_xticks([])
    axmatrix.set_yticks([])

    # Plot colorbar.
    axcolor = fig.add_axes([0.91, 0.1, 0.02, 0.6])
    pylab.colorbar(im, cax=axcolor)

    # Save figure
    fig.savefig(self.outdir.fullPath() + "/dendrogram.png")
