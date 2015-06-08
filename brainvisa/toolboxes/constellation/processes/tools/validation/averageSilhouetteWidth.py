###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

from brainvisa.processes import *
try :
  import constel.lib.clustervalidity as cv
except :
  pass

import constel.lib.plot as p
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pylab
import os
import re
name = 'Average Silhouette Width'
userLevel = 2

signature = Signature(
    "output_name_directory", String(),
    'connectivity_matrix_reduced', ListOf(ReadDiskItem('Group Matrix', 'GIS image')),
    'kmax', Integer(),
)

class MatplotlibFig(object):
    def __init__(self, fig):
        self._fig = fig
    def __del__(self):
        mainThreadActions().call(pylab.close, self._fig)

def validate( self ):
  import constel.lib.clustervalidity as cv
  
def initialization(self):
    self.kmax = 12


def create_page(name_matrix, matrix, kmax):
    """
    """
    title = {23: "left postcentral gyrus",
             25: "left precentral gyrus",
             27: "left rostral anterieur cingulate gyrus",
             59: "right postcentral gyrus",
             61: "right precentral gyrus",
             63: "right rostral anterieur cingulate gyrus",
             1315: "left orbitofrontal cortex",
             4951: "right orbitofrontal cortex"}
    patch = re.findall("G[0-9]+", os.path.basename(str(name_matrix)))[0]
    patch_nb = int(re.findall("[0-9]+", patch)[0])
    fig = plt.figure()
    fig.suptitle(os.path.basename(str(name_matrix)), fontsize=14, fontweight="bold", color="blue")
    ax = plt.subplot(121)
    fig.subplots_adjust(top=0.85)
    left = 0.
    bottom = 1.
    b = 0
    asw = []
    for k in range(2, kmax + 1):
        s = cv.silhouette_score(matrix, k)
        asw.append(s)
        ax.text(left, bottom - b, "for K = " + str(k) + ", ASW is " + str(round(s, 4)))
        b += 0.05
    aswOpt = max(asw)
    ax.text(0.5, 0., "The larger Average Silhouette Width is " + str(aswOpt), color="red")
    ax.axis("off")
    plt.subplot(222)
    
    list_k = range(kmax+1)
    list_k = [x for x in list_k if x != 0 and x != 1]
    
    plt.plot(list_k, asw, 'k')
    plt.title(title[patch_nb], fontsize=13)
    plt.ylabel("ASW", fontsize=11)
    plt.xlabel("Clusters", fontsize=11)
    
        
    

def execution (self, context):
    pp = PdfPages(self.output_name_directory)

    for matrix in self.connectivity_matrix_reduced:
        reduced_matrix = aims.read(matrix.fullPath())
        reduced_matrix = np.asarray(reduced_matrix)[:, :, 0, 0]
        create_page(matrix, reduced_matrix, self.kmax)
        pp.savefig()
    pp.close()
