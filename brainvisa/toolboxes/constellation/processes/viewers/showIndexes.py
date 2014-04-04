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
import constel.lib.visutools as clv

signature = Signature(
    'measures_files', ListOf(ReadDiskItem('Directory', 'Directory')),
    'k_max', Integer(),
    'rand_index', Boolean(),
    'cramer_V', Boolean(),
    'V_measure', Boolean(),
    'mutual_information', Boolean(),  
)

def initialization(self):
    self.rand_index = True
    self.cramer_V = True
    self.V_measure = True
    self.mutual_information = True

def execution(self, context):
    if self.rand_index:
        clv.plot_measures(self.measures_files, self.k_max, 'rand_index')
    if self.cramer_V:
        clv.plot_measures(self.measures_files, self.k_max, 'cramer_V')
    if self.V_measure:
        clv.plot_measures(self.measures_files, self.k_max, 'v_measure')
    if self.mutual_information:
        clv.plot_measures(self.measures_files, self.k_max, 'mutual_information')
    #input_dir = os.path.dirname(self.measures_files[0].fullPath())
    #print input_dir
    #clv.thumbnails(input_dir)