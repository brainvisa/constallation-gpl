from brainvisa.processes import *

def validation():
  try:
    import constel
  except:
    raise ValidationError( 'constellation module is not here.' )

name = 'Freesurfer BrainVisa + Constellation Inter pipeline'
userLevel = 2


signature = Signature(
  'list_of_subjects_FS', ListOf( ReadDiskItem( 'Subject', 'Directory' ) ),
             'group_FS', ReadDiskItem('Group definition', 'XML' ),
  'list_of_subjects_BV', ListOf( ReadDiskItem( 'Subject', 'Directory' ) ),
             'group_BV', ReadDiskItem('Group definition', 'XML' ),
                'study', String(),
                'gyrus', Integer(),
    'init_texture_name', String(),
   'group_texture_name', String(),
         'gyri_texture', ListOf( ReadDiskItem( 'BothResampledGyri', 'Aims texture formats' ) ),  
)

def initialization( self ):

  eNode = SerialExecutionNode( self.name, parameterized=self )

  ### Average Mesh FreeSurfer
  eNode.addChild( 'GroupFreesurfer',
                  ProcessExecutionNode( 'freesurferCreateGroup',
                  optional = 1 ) )

  eNode.addDoubleLink( 'GroupFreesurfer.list_of_subjects',
                       'list_of_subjects_FS' )
  eNode.addDoubleLink( 'GroupFreesurfer.group_definition',
                       'group_FS' )

  eNode.addChild( 'AverageBrain',
                  ProcessExecutionNode( 'freesurferMeanMesh',
                  optional = 1 ) )

  eNode.addDoubleLink( 'AverageBrain.group',
                       'GroupFreesurfer.group_definition' )

  ### Create of group BrainVisa
  eNode.addChild( 'groupBrainvisa',
                  ProcessExecutionNode( 'createGroup',
                  optional = 1 ) )

  eNode.addDoubleLink( 'groupBrainvisa.list_of_subjects',
                       'list_of_subjects_BV' )
  eNode.addDoubleLink( 'groupBrainvisa.group_definition',
                       'group_BV' )

  ### Brainvisa Constellation Inter Pipeline
  eNode.addChild( 'ConstellationInter',
                  ProcessExecutionNode( 'pipelineInterBrainvisa',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ConstellationInter.study_name',
                       'study' )
  eNode.addDoubleLink( 'ConstellationInter.patch_label',
                       'gyrus' )
  eNode.addDoubleLink( 'ConstellationInter.texture_in',
                       'init_texture_name' )
  eNode.addDoubleLink( 'ConstellationInter.texture_out',
                       'group_texture_name' )
  eNode.addDoubleLink( 'ConstellationInter.group',
                       'group_BV' )
  eNode.addDoubleLink( 'ConstellationInter.average_mesh',
                       'AverageBrain.BothAverageMesh' )                  
  eNode.addDoubleLink( 'ConstellationInter.connMatrixBasinInter.gyri_segmentation',
                       'gyri_texture' )

  self.setExecutionNode( eNode )
  