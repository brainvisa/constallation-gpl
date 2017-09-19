# -*- coding: utf-8 -*-
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

include( 'base' )
include( 'registration' )
include( 'anatomy' )

default_tracking_session='default_tracking_session'

insertFirst( '{center}/{subject}/registration',
    't2diff_TO_t1mri_<subject>-{source.acquisition}-{destination.acquisition}', SetType( 'Transform T2 Diffusion MR to Raw T1 MRI' ),
    't1mri_TO_t2diff_<subject>-{source.acquisition}-{destination.acquisition}', SetType( 'Transform Raw T1 MRI to T2 Diffusion MR' ),
    't1mri_TO_acpc_t2diff_<subject>-{source.acquisition}-{destination.acquisition}', SetType( 'Transform Raw T1 MRI to AC/PC T2 Diffusion MR' ),
    't1mri_TO_eacpc_t2diff_<subject>-{source.acquisition}-{destination.acquisition}', SetType( 'Transform Raw T1 MRI to Extended AC/PC T2 Diffusion MR' ),
  )

insert( '{center}/{subject}',
  #'registration', SetContent(
    #'t2diff_TO_t1mri_{source.subject}_{source.acquisition}_{destination.acquisition}', SetType( 'Transform T2 Diffusion MR to Raw T1 MRI' ),
    #'t1mri_TO_t2diff_{source.subject}_{source.acquisition}_{destination.acquisition}', SetType( 'Transform Raw T1 MRI to T2 Diffusion MR' ),
    #'t1mri_TO_acpc_t2diff_{source.subject}_{source.acquisition}_{destination.acquisition}', SetType( 'Transform Raw T1 MRI to AC/PC' ),
    #'t1mri_TO_eacpc_t2diff_{source.subject}_{source.acquisition}_{destination.acquisition}', SetType( 'Transform Raw T1 MRI to Extended AC/PC T2 Diffusion MR' ),
  #),
  'diffusion', SetContent( 
    '{acquisition}', SetDefaultAttributeValue( 'acquisition', default_acquisition ), SetNonMandatoryKeyAttribute( 'acquisition' ),SetContent(
      'raw_diffusion_<subject>', SetType( 'Raw DW Diffusion MR' ),
      'diffusion_<subject>', SetType( 'Non oriented DW Diffusion MR' ),
                             SetPriorityOffset( +1 ),
      't2diff_<subject>', SetType( 'Raw T2 Diffusion MR' ),
      'acpc_diffusion_<subject>', SetType( 'AC/PC DW Diffusion MR' ),
      'acpc_t2diff_<subject>', SetType( 'AC/PC T2 Diffusion MR' ),
      'eacpc_diffusion_<subject>', SetType( 'Extended AC/PC DW Diffusion MR' ),
      'eacpc_t2diff_<subject>', SetType( 'Extended AC/PC T2 Diffusion MR' ),
      'registration', SetContent(
        't2diff_<subject>', SetType( 'Referential of Raw T2 Diffusion MR' ),
        'acpc_t2diff_<subject>', SetType( 'AC/PC T2 Diffusion MR referential' ),
        'eacpc_t2diff_<subject>', SetType( 'Extended AC/PC T2 Diffusion MR referential' ),
        't2diff_TO_acpc_t2diff_<subject>_<acquisition>', SetType( 'Transform T2 Diffusion MR to AC/PC T2 Diffusion MR' ),
        't2diff_TO_eacpc_t2diff_<subject>_<acquisition>', SetType( 'Transform T2 Diffusion MR to Extended AC/PC T2 Diffusion MR' ),
        'acpc_t2diff_TO_eacpc_t2diff_<subject>_<acquisition>', SetType( 'Transform AC/PC T2 Diffusion MR to Extended AC/PC T2 Diffusion MR' ),
      ),
      '{analysis}', SetDefaultAttributeValue( 'analysis', default_analysis ), SetContent(
        'brain_mask_<subject>', SetType( 'T2 Brain Mask' ),
        'white_mask_<subject>', SetType( 'T2 White matter Mask' ),SetPriorityOffset( +1 ),
        'dti_<subject>', SetType( 'DTI Model' ),
        'dti_error_mask_<subject>', SetType( 'Error Mask' ),
        'adc_<subject>', SetType( 'Apparent Diffusion Coefficient' ),
        'fa_<subject>', SetType( 'Fractional Anisotropy' ),
        'vr_<subject>', SetType( 'Volume Ratio' ),
        'stddev_<subject>', SetType( 'Diffusion Standard Deviation' ),
        'pdc_<subject>', SetType( 'Parallel Diffusion Coefficient' ),
        'tdc_<subject>', SetType( 'Transverse Diffusion Coefficient' ),
        'dwt2_<subject>', SetType( 'Diffusion Weighted T2' ),
        'maxev_<subject>', SetType( 'Maximum Eigenvector' ),
        'rgb_<subject>', SetType( 'RGB Eigenvector' ),
        'qball_<subject>', SetType( 'QBall Model'),
        'alphamap_<subject>', SetType('Diffusion Anisotropy'),
        'orientation_<subject>', SetType('Orientation File'),
        '{tracking_session}', SetDefaultAttributeValue( 'tracking_session', default_tracking_session),
        SetContent(
          'regions_<subject>_<tracking_session>', SetType( 'Tracking regions graph' ), SetPriorityOffset( +2 ),
          'bundles_<subject>_<tracking_session>', SetType( 'Fascicles bundles' ), SetWeakAttr('transformed', 'no'),
          'bundles_<subject>_<tracking_session>_*', SetType( 'Fascicles bundles' ), SetWeakAttr('transformed', 'no'), SetPriorityOffset( -1 ),
          'bundles_transformed_<subject>_<tracking_session>', SetType( 'Fascicles bundles' ), SetWeakAttr('transformed', 'yes'), SetPriorityOffset(-1),
          'density_<subject>_<tracking_session>', SetType( 'Diffusion Density Map' ),
          'statistics_<subject>_<tracking_session>', SetType( 'Bundles scalar features' ),
        ),
      ),
    ),
  ),
)

insert( '{center}/{subject}/t1mri/{acquisition}',
  'acpc_t1mri_<subject>', SetType( 'T1 MRI AC/PC oriented' ),
)

#----------------- Registration -------------------------


#insertFirst( '{center}/registration',
    ## Inter subject: Transform T2 Diffusion MR to T2 Diffusion MR
    #'DiffT2_{source.subject}-{source.acquisition}_TO_DiffT2-{dest.subject}-{dest.acquisition}', SetType( 'Transform T2 Diffusion MR to T2 Diffusion MR' ),
    #'DiffT2_{source.subject}_TO_{dest.subject}-{dest.acquisition}', SetType( 'Transform T2 Diffusion MR to T2 Diffusion MR' ), SetPriorityOffset( -1 ),
    #'DiffT2_{source.subject}-{source.acquisition}_TO_{dest.subject}', SetType( 'Transform T2 Diffusion MR to T2 Diffusion MR' ), SetPriorityOffset( -1 ),
    #'DiffT2_{source.subject}_TO_{dest.subject}', SetType( 'Transform T2 Diffusion MR to T2 Diffusion MR' ), SetPriorityOffset( -2 ),
    ## Inter subject: Transform Raw T1 MRI to T2 Diffusion MR
    #'RawT1-{source.subject}-{source.acquisition}_TO_DiffT2-{dest.subject}-{dest.acquisition}', SetType( 'Transform Raw T1 MRI to T2 Diffusion MR' ),
    #'RawT1-{source.subject}_TO_DiffT2-{dest.subject}-{dest.acquisition}', SetType( 'Transform Raw T1 MRI to T2 Diffusion MR' ), SetPriorityOffset( -1 ),
    #'RawT1-{source.subject}-{source.acquisition}_TO_DiffT2-{dest.subject}', SetType( 'Transform Raw T1 MRI to T2 Diffusion MR' ), SetPriorityOffset( -1 ),
    #'RawT1-{source.subject}_TO_DiffT2-{dest.subject}', SetType( 'Transform Raw T1 MRI to T2 Diffusion MR' ), SetPriorityOffset( -2 ),
    ## Inter subject: Transform T2 Diffusion MR to Raw T1 MRI
    #'DiffT2-{source.subject}-{source.acquisition}_TO_RawT1-{dest.subject}-{dest.acquisition}', SetType( 'Transform T2 Diffusion MR to Raw T1 MRI' ),
    #'DiffT2-{source.subject}_TO_RawT1-{dest.subject}-{dest.acquisition}', SetType( 'Transform T2 Diffusion MR to Raw T1 MRI' ), SetPriorityOffset( -1 ),
    #'DiffT2-{source.subject}-{source.acquisition}_TO_RawT1-{dest.subject}', SetType( 'Transform T2 Diffusion MR to Raw T1 MRI' ), SetPriorityOffset( -1 ),
    #'DiffT2-{source.subject}_TO_RawT1-{dest.subject}', SetType( 'Transform T2 Diffusion MR to Raw T1 MRI' ), SetPriorityOffset( -2 ),
#)


#----------------- Modifications of hierarchy -------------------------

#* Dans {center}/{subject}/diffusion
  #- moved in {acquisition} (must be moved in default_acquisition)
    #'<subject>_raw_dw_diffusion'  --> 'raw_diffusion_<subject>'
    #'<subject>_dw_diffusion'  --> 'diffusion_<subject>'
    #'<subject>_t2_diffusion'  --> 't2diff_<subject>'
    #'<subject>_acpc_dw_diffusion'  --> 'acpc_diffusion_<subject>'
    #'<subject>_acpc_t2_diffusion'  --> 'acpc_t2diff_<subject>'
    #'<subject>_eacpc_dw_diffusion'  --> 'eacpc_diffusion_<subject>'
    #'<subject>_eacpc_t2_diffusion'  --> 'eacpc_t2diff_<subject>'

  #- moved in {acquisition}/{analysis} (must be moved in default_acquisition/default_analysis)
    #'<subject>_mask', --> 'diffusion_mask_<subject>'
    #'<subject>_fixedDT', --> 'dti_<subject>'
    #'<subject>_error_mask', --> 'dti_error_mask_<subject>',
    #'<subject>_adc', --> 'adc_<subject>'
    #'<subject>_fa', --> 'fa_<subject>'
    #'<subject>_vr', --> 'vr_<subject>'
    #'<subject>_stddev', --> 'stddev_<subject>'
    #'<subject>_dwt2', --> 'dwt2_<subject>'
    #'<subject>_maxev', --> 'maxev_<subject>'
    #'<subject>_rgbev', --> 'rgb_<subject>'
    #'<subject>_qball', --> 'qball_<subject>'
    #'<subject>_alphaMap', --> 'alphamap_<subject>'
    #'<subject>_orientation', --> 'orientation_<subject>'

  #- removed (must be moved in default_acquisition/default_analysis/default_tracking)
    #'<subject>_regions', --> 'regions_<subject>_<tracking>'
    #'<subject>_bundles', --> 'bundles_<subject>_<tracking>'
    #'<subject>_density', --> 'density_<subject>_<tracking>'
    #'<subject>_statistics', --> 'statistics_<subject>_<tracking>'

  #- removed (must be moved in acquisition=*, analysis=default_analysis)
    #'<subject>_*_t2_diffusion'
    #'<subject>_*_acpc_dw_diffusion'
    #'<subject>_*_acpc_t2_diffusion'
    #'<subject>_*_eacpc_dw_diffusion'
    #'<subject>_*_eacpc_t2_diffusion'
    #'<subject>_*_eacpc_t1_mri'
    #'<subject>_*_mask'
    #'<subject>_*_fixedDT'
    #'<subject>_*_interpolatedDT'
    #'<subject>_*_multiDT'
    #'<subject>_*_qspace'
    #'<subject>_*_error_mask'
    #'<subject>_*_adc'
    #'<subject>_*_fa'
    #'<subject>_*_vr'
    #'<subject>_*_stddev'
    #'<subject>_*_dwt2'
    #'<subject>_*_maxev'
    #'<subject>_*_rgbev'
    #'<subject>_*_qball'
    #'<subject>_*_alphaMap'
    #'<subject>_*_orientation'

  #- moved in {center}/{subject}/t1mri/{acquisition}
    #'<subject>_eacpc_t1_mri' renamed 't1_acpc_<subject>'

  #- removed (should not exists)
    #'<subject>_interpolatedDT',
    #'<subject>_multiDT',
    #'<subject>_qspace',

#* Dans {center}/{subject}/diffusion/{tracking}
  #- removed  (must be moved in ../default_acquisition/<*>/<tracking>)
    #'<subject>_<tracking>_*_regions',
    #'<subject>_<tracking>_*_bundles',
    #'<subject>_<tracking>_*_bundles',
    #'<subject>_<tracking>_*_density',
    #'<subject>_<tracking>_*_statistics',
  #- moved in ../{acquisition}/{analysis}/{tracking}
    #'<subject>_<tracking>_regions', --> 'regions_<subject>_<tracking>'
    #'<subject>_<tracking>_bundles', --> 'bundles_<subject>_<tracking>'
    #'<subject>_<tracking>_density', --> 'density_<subject>_<tracking>'
    #'<subject>_<tracking>_statistics', --> 'statistics_<subject>_<tracking>'

# Referentials & transformations
# Dans '{center}/{subject}/registration'
  #-  Moved in '{center}/{subject}/diffusion/default_acquisition/registration
    #DiffT2-<subject> -> t2diff_<subject>
    #ACPC-<subject>' -> acpc_t2diff_<subject>
    #ExtACPC-DiffT2-<subject> -> eacpc_t2diff_<subject>
    #DiffT2-<subject>_TO_ACPC -> t2diff_TO_acpc_t2diff_<subject>_default_acquisition
    #DiffT2-<subject>_TO_ExtACPC-DiffT2 -> t2diff_TO_eacpc_t2diff_<subject>_default_acquisition
    #ACPC-<subject>_TO_ExtACPC-DiffT2 -> acpc_t2diff_TO_eacpc_t2diff_<subject>_default_acquisition
  #- Moved in '{center}/{subject}/diffusion/{acquisition}/registration
    #DiffT2-<subject>-<acquisition> -> t2diff_<subject>
    #ACPC-<subject>-<acquisition>' -> acpc_t2diff_<subject>
    #ExtACPC-DiffT2-<subject>-<acquisition> -> eacpc_t2diff_<subject>
    #DiffT2-<subject>-<acquisition>_TO_ACPC -> t2diff_TO_acpc_t2diff_<subject>_<acquisition>
    #DiffT2-<subject>-<acquisition>_TO_ExtACPC-DiffT2 -> t2diff_TO_eacpc_t2diff_<subject>_<acquisition>
    #ACPC-<subject>-<acquisition>_TO_ExtACPC-DiffT2 ->acpc_t2diff_TO_eacpc_t2diff_<subject>_<acquisition>
  #- renamed in {center}/{subject}/registration
    #RawT1-<subject>-<acquisition>_TO_DiffT2 -> t1mri_TO_t2diff_<subject>_<acquisition>_<acquisition>
    #RawT1-<subject>_TO_DiffT2 -> t1mri_TO_t2diff_<subject>_default_acquisition_default_acquisition
    #DiffT2-<subject>-<acquisition>_TO_RawT1 -> t2diff_TO_t1mri_<subject>_<acquisition>_<acquisition>
    #DiffT2-<subject>_TO_RawT1 -> t2diff_TO_t1mri_<subject>_default_acquisition_default_acquisition
    #RawT1-<subject>-<acquisition>_TO_ExtACPC-DiffT2 -> t1mri_TO_eacpc_t2diff_<subject>_<acquisition>_<acquisition>
    #RawT1-<subject>_TO_ExtACPC-DiffT2 ->  t1mri_TO_eacpc_t2diff_<subject>_default_acquisition_default_acquisition
    #RawT1-<subject>-<acquisition>_TO_ACPC -> t1mri_TO_acpc_t2diff_<subject>_<acquisition>_<acquisition>
    #RawT1-<subject>_TO_ACPC ->t1mri_TO_acpc_t2diff_<subject>_default_acquisition_default_acquisition

# Dans {center}/{subject}/diffusion
  #- Moved in {center}/{subject}/registration [brainvisa-3.0]
    #<subject>_t2_diffusion_TO_t1_anatomy_transform -> t2diff_TO_t1mri_<subject>_default_acquisition_default_acquisition
    #<subject>_t1_anatomy_TO_t2_diffusion_transform ->  t1mri_TO_t2diff_<subject>_default_acquisition_default_acquisition
    #<subject>_t1_anatomy_TO_acpc_transform -> t1mri_TO_acpc_t2diff_<subject>_default_acquisition_default_acquisition
    #<subject>_t1_anatomy_TO_eacpc_transform -> t1mri_TO_eacpc_t2diff_<subject>_default_acquisition_default_acquisition
  #- Moved in {center}/{subject}/diffusion/default_acquisition/registration
    #<subject>_t2_diffusion_TO_acpc_transform -> t2diff_TO_acpc_t2diff_<subject>_default_acquisition
    #<subject>_acpc_TO_eacpc_transform -> acpc_t2diff_TO_eacpc_t2diff_<subject>_default_acquisition
    #<subject>_t2_diffusion_TO_eacpc_transform -> t2diff_TO_eacpc_t2diff_<subject>_default_acquisition
