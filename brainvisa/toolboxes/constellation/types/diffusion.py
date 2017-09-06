#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
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

include( 'builtin' )
include( 'anatomy' )
include( 'registration' )

Format( 'Aims bundles', [ 'f|*.bundles', 'f|*.bundlesdata' ] )
Format( 'Trackvis tracts', 'f|*.trk' )
Format( 'Bundle Selection Rules', 'f|*.brules' )

createFormatList(
  'Aims readable bundles formats',
  (
    'Aims Bundles',
    'Trackvis tracts',
  )
)

createFormatList(
  'Aims writable bundles formats',
  (
    'Aims Bundles',
  )
)

FileType( 'Bundles', 'Any Type', 'Aims readable bundles formats' )

#----------------- Diffusion ----------------------

FileType( 'Directions MESH', 'Mesh' )

FileType( 'DW Diffusion MR', '4D Volume' )
FileType( 'Raw DW Diffusion MR', 'DW Diffusion MR' )
FileType( 'Corrected DW Diffusion MR', 'DW Diffusion MR' )
FileType( 'Non oriented DW Diffusion MR', 'Corrected DW Diffusion MR' )
FileType( 'AC/PC DW Diffusion MR', 'Corrected DW Diffusion MR' )
FileType( 'Extended AC/PC DW Diffusion MR', 'Corrected DW Diffusion MR' )
FileType( 'T2 Diffusion MR', '3D Volume' )
FileType( 'Raw T2 Diffusion MR', 'T2 Diffusion MR' )
FileType( 'AC/PC T2 Diffusion MR', 'T2 Diffusion MR' )
FileType( 'Extended AC/PC T2 Diffusion MR', 'T2 Diffusion MR' )
FileType( 'T1 MRI AC/PC oriented', 'T1 MRI' )
FileType( 'Tracking regions', 'ROI' )
FileType( 'Tracking regions graph', 'Tracking regions' )
FileType( 'Diffusion Mask', 'Tracking regions' )
FileType( 'T2 Brain Mask', 'Diffusion Mask' )
FileType( 'T2 White matter Mask', 'Diffusion Mask' )

FileType( 'Diffusion Model', 'Any Type', 'Bucket' )
FileType( 'DTI Model', 'Diffusion Model' )

FileType( 'Diffusion Scalar Map', '3D Volume' )
FileType( 'Apparent Diffusion Coefficient', 'Diffusion Scalar Map' ),
FileType( 'Fractional Anisotropy', 'Diffusion Scalar Map' ),
FileType( 'Volume Ratio', 'Diffusion Scalar Map' ),
FileType( 'Diffusion Standard Deviation', 'Diffusion Scalar Map' ),
FileType( 'Parallel Diffusion Coefficient', 'Diffusion Scalar Map' ),
FileType( 'Transverse Diffusion Coefficient', 'Diffusion Scalar Map' ),
FileType( 'Diffusion Weighted T2', 'Diffusion Scalar Map' ),


FileType( 'Diffusion Orientation Map', '3D Volume' ),
FileType( 'Maximum Eigenvector', 'Diffusion Orientation Map' ),
FileType( 'RGB Eigenvector', 'Diffusion Orientation Map' ),

FileType( 'QBall Model', 'Diffusion Model'),
FileType( 'Orientation File', 'Text file'),
FileType( 'Diffusion Anisotropy', 'Diffusion Scalar Map'),


FileType( 'Fascicles bundles', 'Bundles' )
FileType( 'Diffusion Density Map', '4D Volume'),
FileType( 'Bundle Selection Rules', 'Any Type', 'Bundle Selection Rules' )

#----------------- Registration -------------------------

FileType( 'Referential of Raw T2 Diffusion MR', 'Referential' )
FileType( 'AC/PC T2 Diffusion MR referential', 'Referential' )
FileType( 'Extended AC/PC T2 Diffusion MR referential', 'Referential' )


#FileType( 'Transform T2 Diffusion MR to T2 Diffusion MR', 'Transformation matrix' )
FileType( 'Transform T2 Diffusion MR to Raw T1 MRI', 'Transformation matrix' )
FileType( 'Transform T2 Diffusion MR to AC/PC T2 Diffusion MR', 'Transformation matrix' )
FileType( 'Transform T2 Diffusion MR to Extended AC/PC T2 Diffusion MR', 'Transformation matrix' )
FileType( 'Transform AC/PC T2 Diffusion MR to Extended AC/PC T2 Diffusion MR', 'Transformation matrix' )
FileType( 'Transform Raw T1 MRI to T2 Diffusion MR', 'Transformation matrix' )
FileType( 'Transform Raw T1 MRI to Extended AC/PC T2 Diffusion MR', 'Transformation matrix' )
FileType( 'Transform Raw T1 MRI to AC/PC T2 Diffusion MR', 'Transformation matrix' )

