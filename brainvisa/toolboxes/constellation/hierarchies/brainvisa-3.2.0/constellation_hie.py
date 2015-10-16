###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

include("diffusion")


###############################################################################
#                                  Individual part                            #
###############################################################################


insert("{center}/{subject}/diffusion/{acquisition}/{analysis}/{tracking_session}",

"connectivity_parcellation", SetContent(
"{study}", SetContent(
"{texture}", SetContent(


#----------------------------------filteredTracts------------------------------


"{gyrus}", SetContent(     
"filteredTracts", SetContent(

    "<subject>_<texture>_<gyrus>_outsideFibersOfCortex_{smallerlength2}to{greaterlength2}mm_oversampled",
        SetType("Filtered Fascicles Bundles"),
        SetWeakAttr("both_ends_labelled", "No",
                    "oversampled", "Yes"),
            
    "<subject>_<texture>_<gyrus>_fibersNearCortex_{smallerlength1}to{greaterlength1}mm",
        SetType("Filtered Fascicles Bundles"),
        SetWeakAttr("both_ends_labelled", "Yes",
                    "oversampled", "No"),
            
    "<subject>_<texture>_<gyrus>_outsideFibersOfCortex_{smallerlength2}to{greaterlength2}mm",
        SetType("Filtered Fascicles Bundles"),
        SetWeakAttr("both_ends_labelled", "No",
                    "oversampled", "No"),

), # end filteredTracts


#----------------------------------matrix--------------------------------------


"matrix", SetContent(

    "<subject>_<texture>_<gyrus>_connectivityMatrix_fibersNearCortex_{smallerlength1}to{greaterlength1}mm",
        SetType("Connectivity Matrix"),
        SetWeakAttr("ends_labelled", "both",
                    "reduced", "No",
                    "dense", "No",
                    "intersubject", "No"),

    "<subject>_<texture>_<gyrus>_meanConnectivityProfile_fibersNearCortex_{smallerlength1}to{greaterlength1}mm",
        SetType("Filtered Connectivity Profile Texture"),
        SetWeakAttr("both_ends_labelled", "Yes"),
        
    "<subject>_<texture>_<gyrus>_connectivityMatrix_outsideFibersOfCortex_{smallerlength2}to{greaterlength2}mm",
        SetType("Connectivity Matrix"), 
        SetWeakAttr("ends_labelled", "single",
                    "reduced", "No",
                    "dense", "No",
                    "intersubject", "No"),

    "<subject>_<texture>_<gyrus>_meanConnectivityProfile_outsideFibersOfCortex_{smallerlength2}to{greaterlength2}mm",
        SetType("Filtered Connectivity Profile Texture"),
        SetWeakAttr("both_ends_labelled", "No"),
        
    "<subject>_<texture>_<gyrus>_connectivityMatrixSmooth{smoothing}",
        SetType("Connectivity Matrix"),
        SetWeakAttr("ends_labelled", "mixed",
                    "reduced", "No",
                    "dense", "No",
                    "intersubject", "No"),
        
    "<subject>_<texture>_<gyrus>_patchConnectivityMatrix",
        SetType("Connectivity Matrix"),
        SetWeakAttr("ends_labelled", "mixed",
                    "reduced", "No",
                    "dense", "Yes",
                    "intersubject", "No"),

), # end matrix

#----------------------------------clustering----------------------------------

"clustering", SetContent(
"{smoothing}", SetContent(
    
    "<subject>_<texture>_<gyrus>_meanConnectivityProfile",
        SetType("Connectivity Profile Texture"),
        SetWeakAttr("normed", "No",
                    "thresholded", "No",
                    "averaged", "No",
                    "intersubject", "No"),

    "<subject>_<texture>_<gyrus>_thresholdedMeanConnectivityProfile",
        SetType("Connectivity Profile Texture"),
        SetWeakAttr("normed", "No",
                    "thresholded", "Yes",
                    "averaged", "No",
                    "intersubject", "No"),

    "<subject>_<texture>_<gyrus>_normedMeanConnectivityProfile",
        SetType("Connectivity Profile Texture"),
        SetWeakAttr("normed", "Yes",
                    "thresholded", "Yes",
                    "averaged", "No",
                    "intersubject", "No"),

    "<subject>_<texture>_<gyrus>_sumValuesFromRegion",
        SetType("Measures Connectivity ROI Texture"),

    "<subject>_<texture>_<gyrus>_spreadValueOnRegion",
        SetType("Measures Connectivity ROI Texture"),

    "<subject>_<texture>_<gyrus>_watershed",
        SetType("Connectivity ROI Texture"),
        SetWeakAttr("roi_autodetect", "Yes",
                    "roi_filtered", "No",
                    "averaged", "No",
                    "intersubject", "No",
                    "step_time", "No"),

    "<subject>_<texture>_<gyrus>_filteredWatershed",
        SetType("Connectivity ROI Texture"),
        SetWeakAttr("roi_autodetect", "Yes",
                    "roi_filtered", "Yes",
                    "averaged", "No",
                    "intersubject", "No",
                    "step_time", "No"),

    "<subject>_<texture>_<gyrus>_reducedConnectivityMatrix",
        SetType("Connectivity Matrix"),
        SetWeakAttr("ends_labelled", "mixed",
                    "reduced", "Yes",
                    "dense", "No",
                    "intersubject", "No"),

    "<subject>_<texture>_<gyrus>_clusteringTime",
        SetType("Connectivity ROI Texture"),
        SetWeakAttr("roi_autodetect", "No",
                    "roi_filtered", "No",
                    "averaged", "No",
                    "intersubject", "No",
                    "step_time", "Yes"),

), # end smoothing
), # end clustering
), # end gyrus
), # end texture
), # end study
), # end connectivity_parcellation
) # end


###############################################################################
#                                  Group part                                 #
###############################################################################

insert("{center}/group_analysis/{group_of_subjects}",

    "connectivity_clustering", SetContent(
    "{study}", SetContent(
    "{texture}", SetContent(


#----------------------------------Group result--------------------------------

"{gyrus}", SetContent(
"{smoothing}", SetContent(

    "<group_of_subjects>_<study>_<texture>_<gyrus>_mask",
        SetType("Mask Texture"),

    "<group_of_subjects>_<study>_<texture>_<gyrus>_meanConnectivityProfile",
        SetType("Connectivity Profile Texture"),
        SetWeakAttr("normed", "No",
                    "thresholded", "No",
                    "averaged", "Yes",
                    "intersubject", "Yes"),

    "<group_of_subjects>_<study>_<texture>_<gyrus>_thresholdedMeanConnectivityProfile",
        SetType("Connectivity Profile Texture"),
        SetWeakAttr("normed", "No",
                    "thresholded", "Yes",
                    "averaged", "Yes",
                    "intersubject", "Yes"),

    "<group_of_subjects>_<study>_<texture>_<gyrus>_normedMeanConnectivityProfile",
        SetType("Connectivity Profile Texture"),
        SetWeakAttr("normed", "Yes",
                    "thresholded", "Yes",
                    "averaged", "Yes",
                    "intersubject", "Yes"),

    "<group_of_subjects>_<study>_<texture>_<gyrus>_filteredWatershed",
        SetType("Connectivity ROI Texture"),
        SetWeakAttr("roi_autodetect", "Yes",
                    "roi_filtered", "Yes",
                    "averaged", "Yes",
                    "intersubject", "Yes",
                    "step_time", "No"),

    "<group_of_subjects>_<study>_<texture>_<gyrus>_watershed",
        SetType("Connectivity ROI Texture"),
        SetWeakAttr("roi_autodetect", "Yes",
                    "roi_filtered", "No",
                    "averaged", "Yes",
                    "intersubject", "Yes",
                    "step_time", "No"),

    "<group_of_subjects>_<study>_<texture>_<gyrus>_matrix",
        SetType("Connectivity Matrix"),
        SetWeakAttr("ends_labelled", "mixed",
                    "reduced", "No",
                    "dense", "No",
                    "intersubject", "Yes"),
            
#----------------------------------Individual Result---------------------------
          
"{subject}", SetContent(

    "<group_of_subjects>_<study>_<texture>_<gyrus>_<subject>_ConnectivityProfile_nb_normed",
        SetType("Connectivity Profile Texture"),
        SetWeakAttr("normed", "Yes",
                    "thresholded", "Yes",
                    "averaged", "No",
                    "intersubject", "Yes"),

    "<group_of_subjects>_<study>_<texture>_<gyrus>_<subject>_reducedMatrix",
        SetType("Connectivity Matrix"),
        SetWeakAttr("ends_labelled", "mixed",
                    "reduced", "Yes",
                    "dense", "No",
                    "intersubject", "Yes"),
        
    "<group_of_subjects>_<study>_<texture>_<gyrus>_<subject>_clusteringTime",
        SetType("Connectivity ROI Texture"),
        SetWeakAttr("roi_autodetect", "No",
                    "roi_filtered", "No",
                    "averaged", "No",
                    "intersubject", "Yes",
                    "step_time", "Yes"),

), # end subject
), # end smoothing
), # end gyrus
), # end texture
), # end study
), # end connectivity_clustering
) # end
 
