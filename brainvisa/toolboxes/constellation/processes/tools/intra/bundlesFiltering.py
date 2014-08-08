# -*- coding: utf-8 -*-
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

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

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

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.
############################################################################

# BrainVisa module
from brainvisa.processes import *
from soma.path import find_in_path

# System module
import glob

# Plot constel module
def validation():
    if not find_in_path('constelBundlesFiltering'):
        raise ValidationError('Please make sure that constel module is installed.')

name = 'Bundles Filtering'
userLevel = 2

# Argument declaration
signature = Signature(
    'study', String(),
    'texture', String(),
    'patch', String(),
    'database', Choice(),
    'subject', ReadDiskItem('subject', 'directory'),
    'subset_of_tract', ReadDiskItem('Fascicles bundles', 'Aims bundles'),
    'listOf_subsets_of_tract', ListOf( ReadDiskItem('Fascicles bundles', 
                                                    'Aims bundles')),
    'gyri_texture', ReadDiskItem('FreesurferResampledBothParcellationType', 
                                 'Aims texture formats'),
    'white_mesh', ReadDiskItem('AimsBothWhite', 'Aims mesh formats'),
    'dw_to_t1', ReadDiskItem('Transformation matrix', 'Transformation matrix'),
    'min_length_of_fibers_near_cortex', Float(),
    'max_length_of_fibers_near_cortex', Float(),
    'min_distant_fibers_length', Float(),
    'max_distant_fibers_length', Float(),
    'subsets_of_fibers_near_cortex', WriteDiskItem('Fibers Near Cortex', 
                                                   'Aims bundles'),
    'subsets_of_distant_fibers', WriteDiskItem('Very OutSide Fibers Of Cortex', 
                                               'Aims bundles'),
)

# Default values
def initialization( self ):
    databases=[h.name for h in neuroHierarchy.hierarchies() if h.fso.name == 'brainvisa-3.2.0']
    self.signature['database'].setChoices(*databases)
    if len(databases) != 0:
        self.database=databases[0]
    else:
        self.signature['database'] = OpenChoice()
    def linkSubjects(self, dummy):
        if self.database is not None and self.subject is not None:
            subject = os.path.basename(self.subject.fullPath())
            db = os.path.dirname(self.subject.fullPath())
            attrs = dict(self.subject.hierarchyAttributes())
            attrs['_database'] = db
            attrs['subject'] = subject
            attrs['trackfileum'] = '1'
            filename = self.signature['subset_of_tract'].findValue(attrs)
            return filename
    def lef(self, dummy):
        if self.subset_of_tract is not None:
            d = os.path.dirname(self.subset_of_tract.fullPath())
            listBundles = glob.glob(os.path.join(d, '*.bundles'))
            return listBundles
    def linkProfile(self, dummy):
        if self.subject is None:
            return None
        if self.subset_of_tract is not None and self.patch is not None and self.study is not None and self.texture is not None and self.min_length_of_fibers_near_cortex is not None and self.database is not None and self.subject is not None:
            attrs = dict(self.subset_of_tract.hierarchyAttributes())
            attrs.update(self.subject.hierarchyAttributes())
            attrs['study'] = self.study
            attrs['texture'] = self.texture
            attrs['_database'] = self.database
            attrs['_ontology'] = 'brainvisa-3.2.0'
            attrs['subject'] = os.path.basename(self.subject.fullPath())
            attrs['gyrus'] = 'G' + str(self.patch)
            attrs['trackfileum'] = None
            attrs['numberoftrackfiles'] = None
            attrs['minlengthoffibersIn'] = str(int(self.min_length_of_fibers_near_cortex))
            filename = self.signature['subsets_of_fibers_near_cortex'].findValue(attrs)
            return filename
    def linkProfileDistantFibers(self, dummy):
        if self.subsets_of_fibers_near_cortex is not None:
            attrs = dict(self.subsets_of_fibers_near_cortex.hierarchyAttributes())
            attrs['minlengthoffibersOut'] = str(int(self.min_distant_fibers_length))
            filename = self.signature['subsets_of_distant_fibers'].findValue(attrs)
            return filename
    self.linkParameters('subset_of_tract', 'subject', linkSubjects)
    self.linkParameters('listOf_subsets_of_tract', 'subset_of_tract', lef)
    self.linkParameters('subsets_of_fibers_near_cortex', ('database', 'subject', 'study', 'texture', 'patch', 'min_length_of_fibers_near_cortex'), linkProfile)
    self.linkParameters('subsets_of_distant_fibers', ('subsets_of_fibers_near_cortex', 'min_distant_fibers_length'), linkProfileDistantFibers)
    self.linkParameters('white_mesh', 'subject')
    self.linkParameters('dw_to_t1', 'subset_of_tract')
    
    self.signature['listOf_subsets_of_tract'].userLevel = 2
    self.min_length_of_fibers_near_cortex = 30.
    self.max_length_of_fibers_near_cortex = 500.
    self.min_distant_fibers_length = 20.
    self.max_distant_fibers_length = 500.


def execution( self, context ):
    # Both ends of fibers tracts are defined 
    cmd = ['constelBundlesFiltering']
    for subset_of_tract in self.listOf_subsets_of_tract:
        cmd += ['-i', subset_of_tract]
    cmd += [
        '-o', self.subsets_of_fibers_near_cortex,
        '-n', self.subsets_of_distant_fibers,
        '--mesh', self.white_mesh,
        '--tex', self.gyri_texture,
        '--trs', self.dw_to_t1,
        '--mode', 'Name1_Name2orNotInMesh',
        '--names', '^' + self.patch + '_[0-9]+$',
        '--names', '^[0-9]+_' + self.patch + '$',
        '-g', self.patch,
        '-r',
        '-l', self.min_length_of_fibers_near_cortex,
        '-L', self.max_length_of_fibers_near_cortex,
        '--nimlmin', self.min_distant_fibers_length,
        '--nimlmax', self.max_distant_fibers_length,
    ]

    context.system(*cmd)