# from nibabel.freesurfer import io as io
from pysurf.setup import *
# import utilities as ut
from freesurfer import fs

# the_label = io.read_label('/Applications/freesurfer_7.1/subjects/fsaverage/label/lh.cortex.label', read_scalars=True)

# print(the_label[1].shape)

fs_setup('7.2')
subjdir, subj_list = fs.subjdir('/Volumes/Student/bids_tmp/derivatives/subjects', 'sub*')
funcdir, sess_list = fs.funcdir('/Volumes/Reliability/Reliability_analysis/functionals')
sess_list = fs.sesslist(sessid='sessid_E1_self')



# fn_list = ['test.f20.f-vs-o.label', 'test2.f13.f-vs-scr.label']
# contra_list = fs.tocontrast(fn_list)
# print(fs.tosig(fn_list))

# ana_list = ['lh.fsaverage.f20.f-vs-o.label', 'lh.self.f13.f-vs-scr.label', 'lh.self.f13.f-vs-scr.label']

# print(fs.totemplate(ana_list))

# ana_list = ['loc_sm5_E1_fsaverage.lh', 'loc_sm5_E1_fsaverage.rh']

# fs.ana2con(ana_list, func_path)