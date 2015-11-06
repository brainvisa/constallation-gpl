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
*

Main dependencies: axon python API, soma-base, constel

Author: Sandrine Lefranc, 2015
"""

#----------------------------Imports-------------------------------------------


# axon python API modules
from brainvisa.processes import Signature, ReadDiskItem, ValidationError, \
    WriteDiskItem, Integer, String

# constel modules
try:
    from constel.lib.connmatrix.connmatrixtools import compute_mclusters_by_nbasins_matrix
    from constel.lib.connmatrix.connmatrixtools import write_matrix2csv
except:
    pass


#----------------------------Header--------------------------------------------


name = "Write CSV File"
userLevel = 2

signature = Signature(
    # inputs
    "reduced_matrix", ReadDiskItem("Connectivity Matrix", "Aims writable volume formats",
        requiredAttributes={"ends_labelled": "mixed",
                            "reduced": "Yes",
                            "dense": "No",
                            "intersubject": "Yes"}),
    "filtered_basins", ReadDiskItem("Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "Yes",
                            "roi_filtered": "Yes",
                            "averaged": "Yes",
                            "intersubject": "Yes",
                            "step_time": "No"}),
    "clustering", ReadDiskItem("Connectivity ROI Texture", "Aims texture formats",
        requiredAttributes={"roi_autodetect": "No",
                            "roi_filtered": "No",
                            "averaged": "No",
                            "intersubject": "Yes",
                            "step_time": "Yes"}),
    "timestep", Integer(),
    
    # outputs
    "csv_file", String(),
)

#----------------------------Function------------------------------------------


def initialization(self):
    """
    """
    self.timestep = 1

#----------------------------Main program--------------------------------------


def execution(self, context):
    """
    """
    reduced_matrix = aims.read(self.reduced_matrix)
    matrix = numpy.array(reduced_matrix)[:, :, 0, 0]
    parcels = aims.read(self.clustering)
    m = compute_mclusters_by_nbasins_matrix(matrix, parcels, self.timestep, mode="meanOfProfiles")
    write_matrix2csv(matrix, self.csv_file)
    
