############################################################################
#  This software and supporting documentation are distributed by
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
############################################################################

# BrainVisa module
from brainvisa.processes import *
from soma.path import find_in_path

import constel.lib.plot as p
import pylab

name = 'Validity Indexes'
userLevel = 2

signature = Signature(
    'matrix', ReadDiskItem('Group Matrix', 'GIS image'),
    'kmax', Integer(),
    'nbIter', Integer(),
    'indexFile', WriteDiskItem('Text File', ['Text File', 'CSV file']),)


class MatplotlibFig(object):
    def __init__(self, fig):
        self._fig = fig

    def __del__(self):
        mainThreadActions().call(pylab.close, self._fig)


def initialization(self):
    self.kmax = 12
    self.nbIter = 100
    self.indexFile = '/tmp/validityindexes.txt'


def execution(self, context):
    context.system('python', find_in_path('constelGettingValidityIndexes.py'),
                   '-m', self.matrix,
                   '-n', str(self.nbIter),
                   '-k', str(self.kmax),
                   '-f', self.indexFile)
    context.write('OK')

    fileR = open(str(self.indexFile), 'w')
    fileR.close()

#    fig = mainThreadActions().call(p.validity_indexes_plot)
#    return MatplotlibFig(fig)