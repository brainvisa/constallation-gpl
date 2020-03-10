###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

"""
This script does the following:
* defines a Brainvisa process
    - the parameters of a process (Signature),
    - the parameters initialization
    - the linked parameters
* calculate the matrix of size (clusters, basins)
* calculate the same matrix with the values relative to the total number of
  connections (per rows, in percent)

Main dependencies: axon python API, soma-base, constel

Author: Sandrine Lefranc, 2015
"""

# ----------------------------Imports------------------------------------------


# system module
from __future__ import absolute_import
import numpy

# axon python API modules
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem
from brainvisa.processes import Integer, String, ValidationError

# soma module
from soma import aims


def validation(self):
    """
    This function is executed at BrainVisa startup when the process is loaded.
    It checks some conditions for the process to be available.
    """
    try:
        from constel.lib.utils.matrixtools import write_matrix2csv,\
            calculate_percentage, compute_mclusters_by_nbasins_matrix
    except ImportError:
        raise ValidationError(
            "Please make sure that constel module is installed.")

# ---------------------------Header-------------------------------------------


name = "Write connectivity matrix as CSV File"
userLevel = 2

signature = Signature(
    # inputs
    "reduced_matrix", ReadDiskItem(
        "Connectivity Matrix", "Aims writable volume formats",
        requiredAttributes={"ends_labelled": "mixed",
                            "reduced": "Yes",
                            "dense": "No",
                            "intersubject": "Yes"}),
    "clustering", ReadDiskItem(
        "Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "No",
                            "roi_filtered": "No",
                            "averaged": "No",
                            "intersubject": "Yes",
                            "step_time": "Yes"}),
    "number_of_clusters", Integer(),

    # outputs
    "csv_file", String(),
)

# ----------------------------Function-----------------------------------------


def initialization(self):
    """
    """
    self.number_of_clusters = 5

# ----------------------------Main program-------------------------------------


def execution(self, context):
    """
    """
    from constel.lib.utils.matrixtools import write_matrix2csv,\
        calculate_percentage, compute_mclusters_by_nbasins_matrix
    # read the matrix by converting it into numpy array
    reduced_matrix = aims.read(self.reduced_matrix.fullPath())
    matrix = numpy.array(reduced_matrix)[:, :, 0, 0]

    # read the clusters texture by converting it into numpy array
    clusters_aims = aims.read(self.clustering.fullPath())
    clusters = clusters_aims[self.number_of_clusters - 2].arraydata()

    # give the matrix of size M(clusters, basins)
    clusters_matrix = compute_mclusters_by_nbasins_matrix(
        matrix, clusters, mode="mean")

    # give the same matrix with the values relative to the total number of
    # connections (per rows, in percent)
    percent_matrix = calculate_percentage(clusters_matrix)

    # write the results in a CSV file
    write_matrix2csv(percent_matrix, self.csv_file)
