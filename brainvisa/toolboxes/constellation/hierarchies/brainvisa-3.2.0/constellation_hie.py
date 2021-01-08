###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

"""
Four different types:
  * Filtered Fascicles Bundles
  * Connectivity Matrix
  * Connectivity Profile Texture
  * Connectivity ROI Texture
"""

include("diffusion")


insertFirst("{center}/{subject}/nomenclature",

     "nomenclature_{atlasname}", SetType("Nomenclature ROIs File"),
)

###############################################################################
#                                  Individual part                            #
###############################################################################

insert("{center}/{subject}/diffusion/{acquisition}/{analysis}/{tracking_session}",

"connectivity_parcellation", SetContent(
"{method}", SetContent(
"{studyname}", SetContent(


# ---------------------------------filteredTracts------------------------------


"{gyrus}", SetContent(
"filteredTracts", SetContent(

    "<subject>_<studyname>_<gyrus>_oversampled_semilabelled_fibers_{smallerlength}to{greaterlength}mm",
        SetType("Filtered Fascicles Bundles"),
        SetWeakAttr("ends_labelled", "one",
                    "oversampled", "yes"),

    "<subject>_<studyname>_<gyrus>_labelled_fibers_{smallerlength}to{greaterlength}mm",
        SetType("Filtered Fascicles Bundles"),
        SetWeakAttr("ends_labelled", "both",
                    "oversampled", "no"),

    "<subject>_<studyname>_<gyrus>_semilabelled_fibers_{smallerlength}to{greaterlength}mm",
        SetType("Filtered Fascicles Bundles"),
        SetWeakAttr("ends_labelled", "one",
                    "oversampled", "no"),

),  # end filteredTracts


# ---------------------------------matrix--------------------------------------


"matrix", SetContent(

    "<subject>_<studyname>_<gyrus>_labelled_fibers_matrix_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity Matrix"),
        SetWeakAttr("ends_labelled", "both",
                    "reduced", "no",
                    "intersubject", "no",
                    "individual", "yes"),

    "<subject>_<studyname>_<gyrus>_labelled_fibers_mean_profile_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity Profile Texture"),
        SetWeakAttr("ends_labelled", "both",
                    "normed", "no",
                    "intersubject", "no"),

    "<subject>_<studyname>_<gyrus>_semilabelled_fibers_matrix_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity Matrix"),
        SetWeakAttr("ends_labelled", "one",
                    "reduced", "no",
                    "intersubject", "no",
                    "individual", "yes"),

    "<subject>_<studyname>_<gyrus>_semilabelled_fibers_mean_profile_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity Profile Texture"),
        SetWeakAttr("ends_labelled", "one",
                    "normed", "no",
                    "intersubject", "no"),

    "<subject>_<studyname>_<gyrus>_complete_matrix_smooth{smoothing}_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity Matrix"),
        SetWeakAttr("ends_labelled", "all",
                    "reduced", "no",
                    "intersubject", "no",
                    "individual", "yes"),

),  # end matrix

# ---------------------------------clustering----------------------------------

"clustering", SetContent(
"smooth{smoothing}", SetContent(

    "<subject>_<studyname>_<gyrus>_mean_profile_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity Profile Texture"),
        SetWeakAttr("ends_labelled", "all",
                    "normed", "no",
                    "intersubject", "no"),

    "<subject>_<studyname>_<gyrus>_normed_mean_profile_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity Profile Texture"),
        SetWeakAttr("ends_labelled", "all",
                    "normed", "yes",
                    "intersubject", "no"),

    "<subject>_<studyname>_<gyrus>_sum_values_from_region_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity ROI Texture"),
        SetWeakAttr("roi_autodetect", "no",
                    "roi_filtered", "no",
                    "intersubject", "no",
                    "step_time", "no",
                    "measure", "sum"),

    "<subject>_<studyname>_<gyrus>_spread_value_on_region_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity ROI Texture"),
        SetWeakAttr("roi_autodetect", "no",
                    "roi_filtered", "no",
                    "intersubject", "no",
                    "step_time", "no",
                    "measure", "spread"),

    "<subject>_<studyname>_<gyrus>_watershed_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity ROI Texture"),
        SetWeakAttr("roi_autodetect", "yes",
                    "roi_filtered", "no",
                    "intersubject", "no",
                    "step_time", "no",
                    "measure", "no"),

    "<subject>_<studyname>_<gyrus>_filtered_watershed_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity ROI Texture"),
        SetWeakAttr("roi_autodetect", "yes",
                    "roi_filtered", "yes",
                    "intersubject", "no",
                    "step_time", "no",
                    "measure", "no"),

    "<subject>_<studyname>_<gyrus>_reduced_matrix_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity Matrix"),
        SetWeakAttr("ends_labelled", "all",
                    "reduced", "yes",
                    "intersubject", "no",
                    "individual", "yes"),

    "<subject>_<studyname>_<gyrus>_clustering_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity ROI Texture"),
        SetWeakAttr("roi_autodetect", "no",
                    "roi_filtered", "no",
                    "intersubject", "no",
                    "step_time", "yes",
                    "measure", "no"),

),  # end smoothing
),  # end clustering
),  # end gyrus
),  # end studyname
),  # end method
),  # end connectivity_parcellation
)  # end


###############################################################################
#                                  Group part                                 #
###############################################################################

insert("{center}/group_analysis/{group_of_subjects}",

    "connectivity_clustering", SetContent(
    "{method}", SetContent(
    "{studyname}", SetContent(


# ---------------------------------Group result--------------------------------

"{gyrus}", SetContent(
"smooth{smoothing}", SetContent(

    "<group_of_subjects>_<method>_<studyname>_<gyrus>_mask_{smallerlength}to{greaterlength}mm",
        SetType("Mask Texture"),

    "<group_of_subjects>_<method>_<studyname>_<gyrus>_mean_profile_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity Profile Texture"),
        SetWeakAttr("ends_labelled", "all",
                    "normed", "no",
                    "intersubject", "yes"),

    "<group_of_subjects>_<method>_<studyname>_<gyrus>_normed_mean_profile_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity Profile Texture"),
        SetWeakAttr("ends_labelled", "all",
                    "normed", "yes",
                    "intersubject", "yes"),

    "<group_of_subjects>_<method>_<studyname>_<gyrus>_filtered_watershed_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity ROI Texture"),
        SetWeakAttr("roi_autodetect", "yes",
                    "roi_filtered", "yes",
                    "intersubject", "yes",
                    "step_time", "no",
                    "measure", "no"),

    "<group_of_subjects>_<method>_<studyname>_<gyrus>_watershed_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity ROI Texture"),
        SetWeakAttr("roi_autodetect", "yes",
                    "roi_filtered", "no",
                    "averaged", "yes",
                    "intersubject", "yes",
                    "step_time", "no",
                    "measure", "no"),

    "<group_of_subjects>_<method>_<studyname>_<gyrus>_group_reduced_matrix_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity Matrix"),
        SetWeakAttr("ends_labelled", "all",
                    "reduced", "yes",
                    "intersubject", "yes",
                    "individual", "no"),

# ---------------------------------Individual Result---------------------------

    # "<group_of_subjects>_<method>_<studyname>_{sid}_reduced_connectome",
    #    SetType("Connectivity Matrix"),
    #    SetWeakAttr("ends_labelled", "all",
    #                "reduced", "yes",
    #                "intersubject", "yes",
    #                "individual", "yes",
    #                "connectome", "yes"),

    "<group_of_subjects>_<method>_<studyname>_<gyrus>_{sid}_reduced_matrix_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity Matrix"),
        SetWeakAttr("ends_labelled", "all",
                    "reduced", "yes",
                    "intersubject", "yes",
                    "individual", "yes"),

    "<group_of_subjects>_<method>_<studyname>_<gyrus>_{sid}_clustering_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity ROI Texture"),
        SetWeakAttr("roi_autodetect", "no",
                    "roi_filtered", "no",
                    "intersubject", "yes",
                    "step_time", "yes",
                    "measure", "no"),

    "<group_of_subjects>_<method>_<studyname>_<gyrus>_{sid}_silhouette_{smallerlength}to{greaterlength}mm",
        SetType("Clustering Silhouette"),
        SetWeakAttr("roi_autodetect", "no",
                    "roi_filtered", "no",
                    "intersubject", "yes",
                    "step_time", "yes",
                    "measure", "no"),

"optimal", SetContent(

    "<group_of_subjects>_<method>_<studyname>_<gyrus>_{sid}_{optimal}_clustering_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity ROI Texture"),
        SetWeakAttr("roi_autodetect", "no",
                    "roi_filtered", "no",
                    "intersubject", "yes",
                    "step_time", "yes",
                    "measure", "no",
                    "optimal", "silhouette"),
),  # end optimal
),  # end smoothing
),  # end gyrus

"desikan", SetContent(
"smooth{smoothing}", SetContent(

    "<group_of_subjects>_<method>_<studyname>_bh_{sid}_{optimal}_clustering_{smallerlength}to{greaterlength}mm",
        SetType("Connectivity ROI Texture"),
        SetWeakAttr("roi_autodetect", "no",
                    "roi_filtered", "no",
                    "intersubject", "yes",
                    "step_time", "no",
                    "measure", "no",
                    "optimal", "silhouette",
                    "concatenated", "yes"),

),  # end smoothing
),  # end desikan
),  # end texture
),  # end method
),  # end connectivity_clustering
)   # end
