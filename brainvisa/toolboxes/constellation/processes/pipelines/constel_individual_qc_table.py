
from brainvisa.processes import *

name = 'Constellation Individual QC table'
userLevel = 0

signature = Signature(
    'database', Choice(),
    'keys', ListOf(String()),
    'data_filters', ListOf(String()),
    'output_file', WriteDiskItem('Text File', 'HTML PDF'),
)


def initialization(self):
    # list of possible databases, while respecting the ontology
    # ontology: brainvisa-3.2.0
    databases = [h.name for h in neuroHierarchy.hierarchies()
                 if h.fso.name == "brainvisa-3.2.0"]
    self.signature["database"].setChoices(*databases)
    if len(databases) >= 1:
        self.database = databases[0]
    else:
        self.signature["database"] = OpenChoice()

    self.setOptional('data_filters', 'output_file')
    self.keys = ['subject', 'studyname', 'gyrus', 'sid', 'method']


def execution(self, context):
    dtypes = ['Filtered Fascicles Bundles', 'Filtered Fascicles Bundles',
              'Connectivity Matrix', 'Connectivity Matrix',
              'Connectivity Profile Texture', 'Connectivity Profile Texture',
              'Connectivity Matrix', 'Connectivity Matrix',
              'Connectivity Profile Texture', 'Connectivity Matrix',
              'Connectivity ROI Texture']

    tlabels = ['Labeled Filtered Fibers', 'Semi-labeled Filtered Fibers',
               'Labeled Connectivity Matrix',
               'Semi-labeled Connectivity Matrix',
               'Labelled Profile', 'Semi-Labeled Profile',
               'Complete Ind. Matrix', 'Smoothed Ind. Matrix',
               'Normed Ind. Profile', 'Indiv. Reduced Matrix',
               'Indiv. Clustering']

    custom_filt = [eval(filt) for filt in self.data_filters]
    if len(custom_filt) == 1:
        custom_filt = custom_filt * len(dtypes)
    if len(custom_filt) < len(dtypes):
        custom_filt = custom_filt + [{}] * (len(dtypes) - len(custom_filt))

    filter1 = {"ends_labelled": "both", "oversampled": "no"}
    filter2 = {"ends_labelled": "one", "oversampled": "no"}
    filter3 = {"ends_labelled": "both"}
    filter4 = {"ends_labelled": "one"}
    filter5 = {'reduced': 'no', 'intersubject': 'no', 'individual': 'yes',
               'ends_labelled': 'all', 'smoothing': '0.0'}
    filter6 = {'reduced': 'no', 'intersubject': 'no', 'individual': 'yes',
               'smoothing': '3.0'}
    filter7 = {'normed': 'yes', 'intersubject': 'no'}
    filter8 = {'reduced': 'yes', 'intersubject': 'yes', 'individual': 'yes'}
    filter9 = {'intersubject': 'yes', 'roi_autodetect': 'no',
               'roi_filtered': 'no', 'step_time': 'yes', 'measure': 'no'}

    filters = [filter1, filter2, filter3, filter4, filter3, filter4,
               filter5, filter6, filter7, filter8, filter9]
    for filt, custfilt in zip(filters, custom_filt):
        filt.update(custfilt)
    context.write('filters:', filters)
    filters = [repr(filt) for filt in filters]

    self.proc = getProcessInstance('database_qc_table')
    return context.runProcess(self.proc, database=self.database,
                              data_types=dtypes,
                              data_filters=filters,
                              keys=self.keys,
                              type_labels=tlabels,
                              output_file=self.output_file)

