# -*- coding: utf-8 -*-
############################################################################
#  This software and supporting documentation are distributed by
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
#
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the 
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info". 
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.
############################################################################

from brainvisa.processes import *
import matplotlib.pyplot as plt
import numpy as np
import glob

signature = Signature(
    'rand_index_files', ListOf(ReadDiskItem('Directory', 'Directory')),
    'k_max', Integer(),
)

def initialization(self):
    pass

def execution(self, context):
    # finds all the pathnames matching a specified pattern
    for i in range(len(self.rand_index_files)):
        inputs = glob.glob(self.rand_index_files[i].fullPath() + '/*.npy')
    
        couleurs = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
        partition = ['A', 'B', 'C']
    
        rand_index_fig = plt.figure()
        axarr = plt.subplots(2, 2)
        j = 0
        for infile in inputs:
            plt.plot(range(2, self.k_max + 1), np.loadtxt(infile), couleurs[j], label=("partition_" + partition[j]))
            plt.plot(range(2, self.k_max + 1), np.loadtxt(infile), couleurs[j] + 'o')
            plt.ylabel('Rand Index')
            plt.xlabel('Clusters (K)')
            gyrus = os.path.basename(self.rand_index_files[i].fullPath())
            rand_index_fig.suptitle(gyrus)
            plt.legend()
            j += 1
        output_fig = os.path.join(self.rand_index_files[i].fullPath(), "rand_index.svg")
        rand_index_fig.savefig(output_fig)
        
        
    #f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex='col', sharey='row')
    #ax1.plot(listof_fig[0])
    #ax2.plot(listof_fig[1])
    #ax3.plot(listof_fig[2])
    #ax4.plot(listof_fig[3])
    