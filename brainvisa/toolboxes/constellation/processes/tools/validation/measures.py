###############################################################################
# This software and supporting documentation are distributed by CEA/NeuroSpin,
# Batiment 145, 91191 Gif-sur-Yvette cedex, France. This software is governed
# by the CeCILL license version 2 under French law and abiding by the rules of
# distribution of free software. You can  use, modify and/or redistribute the
# software under the terms of the CeCILL license version 2 as circulated by
# CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
###############################################################################

# BrainVisa
from brainvisa.processes import *
from soma import aims

# System module
import numpy as np

# Constellation
try:
    from constel.lib.clustering.clusterstools import entropy
    import constel.lib.measuringtools as measure
    from constel.lib.misctools import sameNbElements
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
except:
    pass


name = "Scores"
userLevel = 2

signature = Signature(
    "clustering_1", ReadDiskItem(
        "Group Clustering Time", "BrainVISA texture formats"),
    "clustering_2", ReadDiskItem(
        "Group Clustering Time", "BrainVISA texture formats"),
    "time_step_max", Integer(),
    "output_dir", WriteDiskItem("Directory", "Directory")
)


def mkdir_path(path):
    if not os.access(path, os.F_OK):
        os.makedirs(path)


def validate(self):
    from constel.lib.clustering.clusterstools import entropy


def initialization(self):
    pass
    # TO DO: link parameters between clustering_1 and 2. Group?


def create_page(output, measures, m):
    """
    """
    title = {23: "left postcentral gyrus",
             25: "left precentral gyrus",
             27: "left rostral anterieur cingulate gyrus",
             59: "right postcentral gyrus",
             61: "right precentral gyrus",
             63: "right rostral anterieur cingulate gyrus",
             1315: "left orbitofrontal cortex",
             4951: "right orbitofrontal cortex"}
    patch = re.findall("G[0-9]+", os.path.basename(str(output)))[0]
    patch_nb = int(re.findall("[0-9]+", patch)[0])
    fig = plt.figure()
    fig.suptitle(os.path.basename(output), fontsize=14, fontweight="bold", color="blue")
    ax = plt.subplot(121)
    fig.subplots_adjust(top=0.85)
    left = 0.
    bottom = 1.
    b = 0
    for index, element in enumerate(measures):
        ax.text(left, bottom - b, "for K = " + str(index + 2) + ": " + str(round(element, 4)))
        b += 0.05
    ax.axis("off")
    plt.subplot(222)
    
    list_k = range(2, len(measures) + 2)
    list_k = [x for x in list_k if x != 0 and x != 1]
    
    plt.plot(list_k, measures, 'k')
    plt.title(title[patch_nb], fontsize=13)
    plt.ylabel(m, fontsize=11)
    plt.xlabel("Clusters", fontsize=11)

def execution(self, context):
    # extract name of path
    group1 = os.path.basename(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(self.clustering_1.fullPath()))))))))
    group2 = os.path.basename(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(self.clustering_2.fullPath()))))))))
    gyrus = os.path.basename(
        os.path.dirname(
            os.path.dirname(os.path.dirname(self.clustering_1.fullPath()))))

    # directory for all validation results organized by gyrus
    output_dir = os.path.join(self.output_dir.fullPath(), "validation", gyrus)
    mkdir_path(output_dir)

    # directory for all measures
    output = os.path.join(
        output_dir, group1 + "_" + group2 + "_" + gyrus + "_")

    # read clustering texture (aims)
    c1 = aims.read(self.clustering_1.fullPath())
    c2 = aims.read(self.clustering_2.fullPath())

    # calculate measure between two clustering (1 and 2)
    randindex_values = []
    cramer_values = []
    mutualinformation_values = []
    homogeneity = []
    completeness = []
    v_measure = []
    all_measures = []
    for i in range(2, self.time_step_max + 1):
        # list of labels (1 and 2)
        labels1 = c1[i].arraydata()
        labels2 = c2[i].arraydata()

        # keep the same number of elements
        l1, l2 = sameNbElements(labels1, labels2)

        # measure value for K
        ri = measure.rand_index(l1, l2)
        cv = measure.cramer_v(l1, l2)
        mi = measure.mutual_information(l1, l2)

        # calculate entropy for each clustering
        entropy1 = entropy(l1)
        entropy2 = entropy(l2)

        # calculate homogeneity and completeness
        homog = mi / (entropy1)
        compl = mi / (entropy2)

        # calculate V measure: equivalent to the mutual information
        if homog + compl == 0.0:
            v = 0.0
        else:
            v = (2.0 * homog * compl / (homog + compl))

        # list of measure values for K = 2:kmax
        randindex_values.append(ri)
        cramer_values.append(cv)
        mutualinformation_values.append(mi)
        homogeneity.append(homog)
        completeness.append(compl)
        v_measure.append(v)

    # save in a npy file
    np.savetxt(output + "rand_index.npy", randindex_values)
    np.savetxt(output + "cramer_V.npy", cramer_values)
    np.savetxt(output + "mutual_information.npy", mutualinformation_values)
    np.savetxt(output + "homogeneity.npy", homogeneity)
    np.savetxt(output + "completeness.npy", completeness)
    np.savetxt(output + "v_measure.npy", v_measure)
    
    all_measures.append(randindex_values)
    all_measures.append(cramer_values)
    all_measures.append(mutualinformation_values)
    all_measures.append(homogeneity)
    all_measures.append(completeness)
    all_measures.append(v_measure)

    m = ["rand_index", "cramer_V", "mutual_information",
         "homogeneity", "completeness", "v_measure"]
    
    pp = PdfPages(output + ".pdf")

    for index, measures in enumerate(all_measures):
        create_page(output, measures, m[index])
        pp.savefig()
    
    pp.close()
