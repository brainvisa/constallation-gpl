from brainvisa.processes import *
from soma.path import find_in_path
import gyri_texture_cleaning
from brainvisa.group_utils import Subject
from soma.minf.api import registerClass, readMinf

name = '00 - Average Gyri Segmentation'
userLevel = 2

signature = Signature(
  'group_freesurfer', ReadDiskItem('Freesurfer Group definition', 'XML' ),
  'gyri_segmentations', ListOf( ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ) ),
  'BothAverageMesh', ReadDiskItem('BothAverageBrainWhite', 'MESH mesh'),
  'average_gyri_segmentation', WriteDiskItem( 'BothResampledGyri', 'Aims texture formats' ),
)

def initialization ( self ):
  #def linkGyri( self, dummy ):
    #if self.group_freesurfer is not None:
      #registerClass('minf_2.0', Subject, 'Subject')
      #groupOfSubjects = readMinf(self.group_freesurfer.fullPath())
      #print groupOfSubjects
      #tex = []
      #for subject in groupOfSubjects:
        #print subject
        #if self.database is not None:
          #subject = subject
          #dirname = self.database
          #filename = os.path.join( dirname, subject, 'label/bh.r.aparc.annot.gii' )
          #print filename
          #if filename is not None:
            #tex.append( filename )
        #return tex
  self.linkParameters( 'gyri_segmentations', 'group_freesurfer' )

def execution ( self, context ):
  registerClass('minf_2.0', Subject, 'Subject')
  groupOfSubjects = readMinf(self.group_freesurfer.fullPath())

  subjects = []
  for subject in groupOfSubjects:
    subjects.append( ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ).findValue( subject.attributes() ) )
  context.write(str([i for i in subjects]))
  
  gyri_segmentations = []
  for gyri_segmentation in self.gyri_segmentations:
    gyri_segmentations.append(gyri_segmentation)

  context.write(str([i for i in gyri_segmentations]))

  #context.system('python', '-c', 'from lefranc.average_texture_labels_test import average_texture_labels_test as f; f(\"%s\", %s);'%(self.average_gyri_segmentation.fullPath(), str([i for i in gyri_segmentations])))
  context.system('python', '-m', 'lefranc.average_texture_labels', self.average_gyri_segmentation.fullPath(), *gyri_segmentations)

  # Computing connected component:
  context.system('python', find_in_path( '/volatile/sandrine/svn/brainvisa/perso/roca/trunk/ensemble_du_code_hors_depot/code_test/scripts/gyri_texture_cleaning.py' ),
    '-i', self.average_gyri_segmentation,
    '-m', self.BothAverageMesh,
    '-o', self.average_gyri_segmentation
  )
  