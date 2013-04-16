# -*- coding: utf-8 -*-
from brainvisa.processes import *
import glob

name = '01 - Select Fibers From Mesh'
userLevel = 2

signature = Signature(
              'study_name', String(),
            'texture_name', String(),
         'subset_of_tract', ReadDiskItem( 'Fascicles bundles', 'Aims bundles' ),
                #'protocol', String(),
                 'subject', WriteDiskItem( 'subject', 'directory' ),
  'listOf_subset_of_tract', ListOf( ReadDiskItem( 'Fascicles bundles', 'Aims bundles' ) ),
              'white_mesh', ReadDiskItem( 'AimsBothWhite', 'Aims mesh formats' ),
       'gyri_segmentation', ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ),
  'diff_to_anat_transform', ReadDiskItem( 'Transformation matrix', 'Transformation matrix' ),

               'reorganized_subsets_of_tracts', ListOf( WriteDiskItem( 'Gyri Regrouped Subset of Tracts', 'Aims bundles' ) ),
  'reorganized_subsets_of_tracts_bundlesnames', ListOf( WriteDiskItem( 'Bundles Name List associated to One Subset of Tracts', 'Text file' ) ),
)

def initialization( self ):
  def lef(self, dummy):
    if self.subset_of_tract is not None:
      d = os.path.dirname( self.subset_of_tract.fullPath() )
      listBundles = glob.glob( d+'/*.bundles' )
      return listBundles
  def linkTracts( self, dummy ):
    if self.listOf_subset_of_tract is not None:
      li = []
      i = 0
      for ssTract in self.listOf_subset_of_tract:
        tracts = os.path.basename( self.listOf_subset_of_tract[i].fullPath() )
        #subject = os.path.basename( os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( self.subset_of_tract.fullPath() ) ) ) ) ) )
        #subject = self.subject.get( 'subject' )
        i1 = tracts.rfind( '_' )
        i0 = tracts.rfind( '_', 0, i1-1 ) + 1
        index = tracts[ i0: i1 ]
        n0 = tracts.rfind( '_' ) + 1
        number = tracts[ n0:tracts.rfind( '.' ) ]
        attrs = dict( self.listOf_subset_of_tract[i].hierarchyAttributes() )
        attrs.update( self.subject.hierarchyAttributes() )
        #attrs['protocol'] = self.protocol
        #attrs['subject'] = subject
        attrs['study'] = self.study_name
        attrs['texture'] = self.texture_name
        attrs['trackingfileindex'] = index
        attrs['maxnumberoffile'] = number
        #x = WriteDiskItem( 'Gyri Regrouped Subset of Tracts', 'Aims bundles' ).findValue( attrs )
        x = self.signature[ 'reorganized_subsets_of_tracts' ].contentType.findValue( attrs )
        li.append( x )
        i += 1
      return li
  def linkSubject( self, dummy ):
    if self.subset_of_tract is not None:
      #subject = self.subset_of_tract.get( 'subject', None )
      subject = self.signature[ 'subject' ].findValue( self.subset_of_tract )
      #if subject is not None:
        #return subject
      #subject = os.path.basename( os.path.dirname( self.subset_of_tract.fullPath() ) )
      return subject
  self.linkParameters( 'listOf_subset_of_tract', 'subset_of_tract', lef )
  self.linkParameters( 'reorganized_subsets_of_tracts', ( 'listOf_subset_of_tract', 'study_name', 'texture_name', 'subject' ), linkTracts )
  self.linkParameters( 'reorganized_subsets_of_tracts_bundlesnames', 'reorganized_subsets_of_tracts' )
  self.linkParameters( 'gyri_segmentation', 'white_mesh' )
  self.linkParameters( 'subject', 'subset_of_tract', linkSubject )

  #self.protocol = 'subjects'
  self.signature['listOf_subset_of_tract'].userLevel = 2
  self.signature['reorganized_subsets_of_tracts'].userLevel = 2
  self.signature['reorganized_subsets_of_tracts_bundlesnames'].userLevel = 2
  
def execution( self, context ):
  context.write( 'For each cortex region, select fibers from mesh.' )
  i = 0
  for ssTract in self.listOf_subset_of_tract:
    context.system( 'constelSelectFiberFromMesh',
      '-i', self.listOf_subset_of_tract[i],
      '-o', self.reorganized_subsets_of_tracts[i],
      '-mesh', self.white_mesh,
      '-namesfile', self.reorganized_subsets_of_tracts_bundlesnames[i],
      '-tex', self.gyri_segmentation,
      '-trs', self.diff_to_anat_transform,
      '-verbose', '-mode', 'Name1_Name2orNotInMesh'
    )
    i += 1
  context.write( 'OK')