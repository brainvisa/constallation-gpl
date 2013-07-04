from brainvisa.processes import *
from freesurfer.brainvisaFreesurfer import testFreesurferCommand

def validation():
  try:
    import constel
  except:
    raise ValidationError( 'constellation module is not here.' )
  testFreesurferCommand()

name = 'Freesurfer/BrainVisa + Constellation Intra pipeline'
userLevel = 2

signature = Signature(
       'RawT1Image', ReadDiskItem('Raw T1 MRI', getAllFormats() ),
            'study', String(),
          'texture', String(),
            'gyrus', Integer(),
         'database', Choice(),
          'subject', ReadDiskItem( 'subject', 'directory' ),
  'subset_of_tract', ReadDiskItem( 'Fascicles bundles', 'Aims bundles' ),
         'dw_to_t1', ReadDiskItem( 'Transformation matrix', 'Transformation matrix' ),
        'smoothing', Float(),
)

def initialization( self ):

  databases=[h.name for h in neuroHierarchy.hierarchies() if h.fso.name == 'brainvisa-3.2.0']
  self.signature['database'].setChoices(*databases)
  if len( databases ) != 0:
    self.database=databases[0]
  else:
    self.signature[ 'database' ] = OpenChoice()
    
  eNode = SerialExecutionNode( self.name, parameterized=self )
  
  ### Brainvisa Freesurfer full pipeline
  eNode.addChild( 'FreeSurferPipeline',
                  ProcessExecutionNode( 'freesurferPipelineComplete',
                  optional = 1 ) )  
                  
  eNode.addDoubleLink( 'FreeSurferPipeline.RawT1Image', 
                       'RawT1Image' )

  ### Brainvisa: Cleaning Isolated Vertices
  eNode.addChild( 'GyriTextureCleaning',
                  ProcessExecutionNode( 'gyriTextureCleaningIsolatedVertices',
                  optional = 1 ) )

  eNode.addDoubleLink( 'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatTex.Gyri',
                       'GyriTextureCleaning.gyri_texture' )

  ### Brainvisa Constellation Intra Pipeline
  eNode.addChild( 'ConstellationIntra',
                  ProcessExecutionNode( 'pipelineIntraBrainvisa',
                  optional = 1 ) )

  eNode.addDoubleLink( 'ConstellationIntra.study',
                       'study' )
  eNode.addDoubleLink( 'ConstellationIntra.texture',
                       'texture' )
  eNode.addDoubleLink( 'ConstellationIntra.gyrus',
                       'gyrus' )
  eNode.addDoubleLink( 'ConstellationIntra.database',
                       'database' )                     
  eNode.addDoubleLink( 'ConstellationIntra.subject',
                       'subject' )
  eNode.addDoubleLink( 'ConstellationIntra.subset_of_tract',
                       'subset_of_tract' )
  eNode.addDoubleLink( 'ConstellationIntra.gyri_texture',
                       'GyriTextureCleaning.gyri_texture_clean' )
  eNode.addDoubleLink( 'ConstellationIntra.white_mesh',
                       'FreeSurferPipeline.FreeSurferPipeline.freesurferConcatenate.BothWhite' )
  eNode.addDoubleLink( 'ConstellationIntra.dw_to_t1',
                       'dw_to_t1' )
  eNode.addDoubleLink( 'ConstellationIntra.smoothing',
                       'smoothing' )

  self.setExecutionNode( eNode )