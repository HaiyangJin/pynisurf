# from nibabel.freesurfer import io as io
from pyfsurf.setup import *
# import utilities as ut
# from freesurfer import *
import pyfsurf.freesurfer as fs


fs_setup('7.2')
# subjdir, subj_list = fs.subjdir('/Volumes/Reliability/bids_tmp/derivatives/subjects', 'sub*')
subjdir, subjlist = fs.subjdir('/Volumes/Reliability/Reliability_pilot/subjects')

# c, f = fs.readsurf('lh.white')
# c[1000, ]

fs.fs.vtx2fsavg(1000, 'fsaverage', 'lh.white')
fs.fs.vtx2fsavg(1000, 'sub-pilot01', 'lh.white')

