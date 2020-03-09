
from __future__ import absolute_import
from brainvisa.processes import Signature, Choice, ListOf, String,\
    WriteDiskItem, neuroHierarchy, getProcessInstance, OpenChoice
from six.moves import zip

name = 'Constellation Group QC table'
userLevel = 0

signature = Signature(
    'database', Choice(),
    'keys', ListOf(String()),
    'data_filters', ListOf(String()),
    'output_file', WriteDiskItem('Text File', 'HTML PDF'),
)


def initialization(self):
    # list of possible databases, while respecting the ontology
    # ontology: brainvisa-3.2.0, non-builtin first
    databases = [h.name for h in neuroHierarchy.hierarchies()
                 if h.fso.name == "brainvisa-3.2.0" and not h.builtin] \
                 + [h.name for h in neuroHierarchy.hierarchies()
                    if h.fso.name == "brainvisa-3.2.0" and h.builtin]
    self.signature["database"].setChoices(*databases)
    if len(databases) >= 1:
        self.database = databases[0]
    else:
        self.signature["database"] = OpenChoice()

    self.setOptional('data_filters', 'output_file')
    self.keys = ['gyrus', 'studyname', 'method']


def execution(self, context):
    dtypes = ['Mask Texture', 'Connectivity Profile Texture',
              'Connectivity Profile Texture',
              'Connectivity ROI Texture', 'Connectivity Matrix',
              'Connectivity ROI Texture', ]

    tlabels = ['Group Mask Texture',
               'Group Profile',
               'Normalized Group Profile',
               'Group Filtered Watershed',
               'Group Reduced Matrix',
               'Group Clustering, all K']

    custom_filt = [eval(filt) for filt in self.data_filters]
    if len(custom_filt) == 1:
        custom_filt = custom_filt * len(dtypes)
    if len(custom_filt) < len(dtypes):
        custom_filt = custom_filt + [{}] * (len(dtypes) - len(custom_filt))

    filter1 = {}
    filter2 = {'intersubject': 'yes', 'normed': 'no'}
    filter3 = {'intersubject': 'yes', 'normed': 'yes'}
    filter4 = {'roi_autodetect': 'yes', 'roi_filtered': 'yes',
               'intersubject': 'yes'}
    filter5 = {'individual': 'no', 'intersubject': 'yes', 'reduced': 'yes'}
    filter6 = {'intersubject': 'yes', 'step_time': 'yes'}

    filters = [filter1, filter2, filter3, filter4, filter5, filter6]
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
