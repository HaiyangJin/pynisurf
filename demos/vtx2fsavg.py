# from nibabel.freesurfer import io as io
from setup import *
# import utilities as ut
from freesurfer import fs


fs_setup('7.2')
# subjdir, subj_list = fs.subjdir('/Volumes/Student/bids_tmp/derivatives/subjects', 'sub*')

# c, f = fs.readsurf('lh.white')
# c[1000, ]

fs.vtx2fsavg(1000, 'fsaverage', 'lh.white')

