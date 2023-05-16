"""
Tools typically only involve structual data.
"""

import os
import re
import numpy as np
import subprocess

import nibabel

# subject code and session lists
def subjdir(subjdir, str_pattern='', setdir=True):
    """This function set up 'SUBJECTS_DIR' and output the subject code list.

    Args:
        subjdir (str, optional): path to $SUBJECTS_DIR folder in FreeSurfer. 
            Defaults to os.getenv('SUBJECTS_DIR').
        str_pattern (str, optional): string pattern used to identify subject
            folders. Defaults to ''.
        setdir (bool, optional): whether set the global env 'SUBJECTS_DIR'. 
            Defaults to True.

    Returns:
        subjdir (str): path to the structural folder.
        subj_list (str list): a list of subject codes.
    """
    if not(bool(subjdir)):
        subjdir=os.getenv('SUBJECTS_DIR')
    
    # my sceret default path to 'fsaverage'
    if subjdir == 'myfs':
        subjdir = os.path.join(os.getenv('HOME'), 'GoogleDrive', '102_fMRI', 'fMRITemplate')
        
    if setdir:
        os.environ['SUBJECTS_DIR'] = subjdir
        print(f'\n$SUBJECTS_DIR is set as {subjdir} now...')
        
    # subject code information
    subjlist = [f for f in os.listdir(subjdir) if re.match(str_pattern, f) and '.' not in f]
    
    return subjdir, subjlist



# read files in FreeSurfer (with nibabel)
def readsurf(surfFn, subjCode='fsaverage'):
    
    surfFile = os.path.join(os.getenv('SUBJECTS_DIR'), subjCode, 'surf', surfFn)
    coord, faces = nibabel.freesurfer.io.read_geometry(surfFile)
    
    return coord, faces


# coordinate system
def TNorig(subjCode, TN='t'):
    origFile = os.path.join(os.getenv('SUBJECTS_DIR'), subjCode, 'mri', 'orig.mgz')
    if TN=='t':
        TNstr = '-tkr'
    else:
        TNstr = ''
        
    TNout = subprocess.check_output(['mri_info', '--vox2ras'+TNstr, origFile])
    
    TNfloat = [float(x) for x in str.split(TNout.decode("utf-8"))]
    TNnp = np.array(TNfloat).reshape(4,4)
    
    return TNnp


def self2fsavg(inpoints, subjCode, surfFn):
    
    inpoints = np.asarray(inpoints).reshape(-1,3)
    
    taldir = os.path.join(os.getenv('SUBJECTS_DIR'), subjCode, 'mri', 'transforms', 'talairach.xfm')
    xfmstrs = open(taldir, 'r', encoding="utf-8").read()
        
    xfmfloat = [float(x) for x in str.split(xfmstrs[:-2])[-12:]]
    xfm = np.array(xfmfloat).reshape(3,4)
    
    Torig = TNorig(subjCode, 't')
    Norig = TNorig(subjCode, 'n')
    
    # converting RAS 
    inRAS = np.transpose(np.hstack((inpoints, np.ones((inpoints.shape[0], 1)))))
    outRAS = xfm @ Norig @ np.linalg.inv(Torig) @ inRAS
    
    outpoints = np.transpose(outRAS)
    
    return (outpoints)
    

def vtx2fsavg(vtxIdx, subjCode, surfFn=''):
    c, f = readsurf(surfFn, subjCode)
    inpoints = c[vtxIdx, ]
    
    # display the input information
    print(f'\nThe input vertex indices are:')
    print(vtxIdx)
    print('The coordinates on the surface are:')
    print(inpoints)
    
    outpoints = self2fsavg(inpoints, subjCode, surfFn)
    
    return(outpoints)

    