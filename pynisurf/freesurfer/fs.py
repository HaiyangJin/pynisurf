"""
Tools typically only involve structual data.
"""

import os
import re
import numpy as np
import subprocess
import platform

import nibabel

# setup freesurfer
def version(isnum=False, toprint=True):
    """Display the version of FreeSurfer in use.

    Parameters
    ----------
    isnum : bool, optional
        whether only obtain the number of the FreeSurfer version (instead of strings), by default False
    toprint : bool, optional
        whether to print the FreeSurfer version, by default True

    Returns
    -------
    str OR float
        the version of FreeSurfer in use.
    """    
    
    # check the if FS version is available
    fscmd = 'recon-all -version > /dev/null 2>&1'
    status = os.system(fscmd)
    
    if bool(status): 
        print('\nFreeSurfer is not set up properly...')
        return
    else:  # obtain the FS version if it was set up
        fs_v = str(subprocess.check_output(['recon-all', '-version'], stderr=subprocess.STDOUT), 'utf-8')
    
    if not isnum:
        # output strings
        if (not bool(status)) & toprint: # FS was set up
            # display the version
            print(f'\nThe version of FreeSurfer in use is:\n{fs_v}')
    else:
        # output numeric 
        tmp_str = fs_v.split('-')
        if len(tmp_str) < 4:
            fs_v = 5.3
        elif len(tmp_str) == 6:
            fs_v = float(tmp_str[3][0:3])
        elif len(tmp_str) == 7:
            fs_v = float(tmp_str[5][1:3])
        else:
            fs_v = 0.0
            
    return fs_v
        

def fslsetup(fsl_dir='/usr/local/fsl'):
    """Set up FSL.

    Parameters
    ----------
    fsl_dir : str, optional
        directory to FSL, by default '/usr/local/fsl'
    """    
    
    # check if FSL was already set up
    if bool(os.getenv('FSLDIR')):
        print('\nFSL was already set up properly.')
        return
    
    path = os.getenv('PATH')
    os.environ['FSLDIR'] = fsl_dir
    os.environ['PATH'] = f'{fsl_dir}/bin:{path}'
    os.environ['FSLOUTPUTTYPE'] = 'NIFTI_GZ'
    os.system('export FSLDIR PATH')
    status = os.system('sh ${FSLDIR}/etc/fslconf/fsl.sh')
    
    assert not bool(status), print(f'\nfsl.sh cannot be found at {fsl_dir}/etc/fslconf/')
    
    print('\nFSL is set up successfully [I hope so].')
    

def setup(fs_dir, fsl_dir='/usr/local/fsl', force=False):
    """Set up FreeSurfer ($FREESURFER_HOME) and FSL.

    Parameters
    ----------
    fs_dir : str
        path to FreeSurfer ($FREESURFER_HOME).
    fsl_dir : str, optional
        path to FSL, by default '/usr/local/fsl'
    force : int, optional
        whether force to set $FREESURFER_HOME, by default False, then $FREESURFER_HOME will not be overwritten if it was already set up.

    Raises
    ------
    Exception
        Only Mac and Linux are supported.
    Exception
        $FREESURFER_HOME should contain SetUpFreeSurfer.sh
    """    

    if bool(os.getenv('FREESURFER_HOME')) and force:
        print('\nFreeSurfer was already set up.')
        version()
        return
    
    # Default path to FreeSurfer in Mac or Linux
    if not bool(fs_dir):
        if platform.system()=='Darwin':
            fs_dir = '/Applications/freesurfer'
        elif platform.system()=='Linux':
            fsPath = '/usr/local/freesurfer'
        else:
            raise Exception('Platform not supported.')
    
    # please ignore this part and just set fsPath as the full path to FreeSurfer
    if os.path.sep not in fs_dir:
        # use fsPath as the verion number if fsPath is not a path 
        # (e.g., '5.3', '6.0', '7.3') 
        fs_dir = f'/Applications/freesurfer/{fs_dir}'
        
    ## Set up FreeSurfer
    os.environ['FREESURFER_HOME'] = fs_dir
    os.environ['SUBJECTS_DIR'] = os.path.join(fs_dir, 'subjects')
    
    status = os.system(f'source {fs_dir}/FreeSurferEnv.sh')
    
    if bool(status):
        os.environ['FREESURFER_HOME'] = ''
        raise Exception(f'SetUpFreeSurfer.sh cannot be found at {fs_dir}.')
    
    fslsetup(fsl_dir)
    
    ## Set PATH and environment variable
    path = os.getenv('PATH')
    os.environ['PATH'] = f'/usr/local/bin:{path}' # add /usr/local/bin to PATH
    os.environ['PATH'] = f'{fs_dir}/tktools:{path}' # add /Applications/freesurfer/tktools: to PATH
    os.environ['PATH'] = f'{fs_dir}/fsfast/bin:{path}' # add /Applications/freesurfer/fsfast/bin: to PATH
    os.environ['PATH'] = f'{fs_dir}/bin:{path}' # add /Applications/freesurfer/bin: to PATH
    
    os.environ['FSFAST_HOME'] = os.path.join(fs_dir, 'fsfast')
    os.environ['FSF_OUTPUT_FORMAT'] = 'nii.gz'
    os.environ['MNI_DIR'] = os.path.join(fs_dir, 'mni')
    
    print('\nFreeSurfer is set up successfully [I hope so].')
    
    ## display the FS version
    version()


# subject code
def subjdir(subjdir, str_pattern='sub-*', set_dir=True):
    """This function set up $SUBJECTS_DIR and output the subject code list.

    Parameters
    ----------
    subjdir : str
        path to $SUBJECTS_DIR folder in FreeSurfer.
    str_pattern : str, optional
        string pattern used to identify subject folders, by default 'sub-*'
    set_dir : bool, optional
        whether to set the global env 'SUBJECTS_DIR', by default True

    Returns
    -------
    str
        path to $SUBJECTS_DIR.
    str list
        a list of subject codes.
    """    

    if not(bool(subjdir)):
        subjdir=os.getenv('SUBJECTS_DIR')
    
    # my sceret default path to 'fsaverage'
    if subjdir == 'myfs':
        subjdir = os.path.join(os.getenv('HOME'), 'GoogleDrive', '102_fMRI', 'fMRITemplate')
        
    if set_dir:
        os.environ['SUBJECTS_DIR'] = subjdir
        print(f'\n$SUBJECTS_DIR is set as {subjdir} now...')
        
    # subject code information
    subjlist = [f for f in os.listdir(subjdir) if re.match(str_pattern, f) and '.' not in f]
    
    return subjdir, subjlist


# read files in FreeSurfer (with nibabel)
def readsurf(surf_fname, subj_code='fsaverage'):
    """Read surface files in FreeSurfer.

    Parameters
    ----------
    surf_fname : str
        surface file name, e.g., 'lh.pial', or 'rh.white'.
    subj_code : str, optional
        subject code/folder in $SUBJECTS_DIR, by default 'fsaverage'

    Returns
    -------
    numpy.ndarray
        vertex/node coordinates on the surface.
    numpy.ndarray
        faces/triangles of the surface.
    """    
    
    surf_file = os.path.join(os.getenv('SUBJECTS_DIR'), subj_code, 'surf', surf_fname)
    coord, faces = nibabel.freesurfer.io.read_geometry(surf_file)
    
    return coord, faces


# coordinate system
def TNorig(subj_code, TN='t'):
    """Obtain the transformation matrix from voxel to RAS (tkr or native) space.
    
    This function get the Torig (TkSurfer or surface Vox2RAS) or Norig (Native or Scanner Vox2RAS) matrix from FreeSurfer. The Torig matrix is obtained from "mri_info --vox2ras-tkr orig.mgz" (this is the same for all orig volumes). And the Norig matrix is obtained from "mri_info --vox2ras orig.mgz" (this should be different for each subject.) 
    
    Torig (TkSurfer or surface Vox2RAS) is matrix for converting from orig.mgz (scanner CRS) to surface in real world (surface RAS). In tkSurfer (or tkMedit): Vertex RAS (or Volume RAS) = Torig * Volume index;  
    
    Norig (Native or Scanner Vox2RAS) is matrix for converting from orig.mgz (scanner CRS) to volume in real word [Scanner XYZ (or RAS)]. CRS: column; row; slice.
    
    More see: https://surfer.nmr.mgh.harvard.edu/fswiki/CoordinateSystems

    Parameters
    ----------
    subj_code : str
        subject code/folder in $SUBJECTS_DIR.
    TN : str, optional
        't' (for Torig) or 'n' (for Norig), by default 't'

    Returns
    -------
    numpy.ndarray
        origMat matrix is the vox2vox matrix from VoxCRS (orig.mgz) to Vertex RAS in real world (in tksurfer tools window) [when TN is 't'], or from VoxCRS to VoxXYZ (VoxRAS) in real world.
    """
    
    origFile = os.path.join(os.getenv('SUBJECTS_DIR'), subj_code, 'mri', 'orig.mgz')
    if TN=='t':
        TNstr = '-tkr'
    else:
        TNstr = ''
        
    TNout = subprocess.check_output(['mri_info', '--vox2ras'+TNstr, origFile])
    
    TNfloat = [float(x) for x in str.split(TNout.decode("utf-8"))]
    TNnp = np.array(TNfloat).reshape(4,4)
    
    return TNnp


def self2fsavg(inpoints, subj_code, surf_fname=None):
    """Convert coordinates from native space to fsaverage space.

    Parameters
    ----------
    inpoints : numpy.ndarray
        coordinates in native space.
    subj_code : str
        subject code/folder in $SUBJECTS_DIR.
    surf_fname : str
        which surface to be used to estimate the vertex on fsaverage (e.g., 'lh.white'). Default is `None`; then not estimate the vertex. When hemisphere infor is included, please make sure it is not the wrong hemisphere. Note if no hemisphere information is inclluded in surf, e.g., 'white', both hemispheres will be loaded to estimate the vertex.

    Returns
    -------
    numpy.ndarray
        the output coordinates in fsaverage space.
    int
        the estimated vertex index on fsaverage.
    float
        the Euclidean distance between the input coordinates and the estimated vertex on fsaverage.
    """    
    
    inpoints = np.asarray(inpoints).reshape(-1,3)
    
    taldir = os.path.join(os.getenv('SUBJECTS_DIR'), subj_code, 'mri', 'transforms', 'talairach.xfm')
    xfmstrs = open(taldir, 'r', encoding="utf-8").read()
        
    xfmfloat = [float(x) for x in str.split(xfmstrs[:-2])[-12:]]
    xfm = np.array(xfmfloat).reshape(3,4)
    
    Torig = TNorig(subj_code, 't')
    Norig = TNorig(subj_code, 'n')
    
    # converting RAS 
    inRAS = np.transpose(np.hstack((inpoints, np.ones((inpoints.shape[0], 1)))))
    outRAS = xfm @ Norig @ np.linalg.inv(Torig) @ inRAS
    
    outpoints = np.transpose(outRAS)
    
    # estimate the vertex/node on fsaverage if `surf_fname` is not empty
    vtxidx, esterr = np.NaN, np.NaN
    if bool(surf_fname):
        if 'lh.' not in surf_fname & 'rh.' not in surf_fname:
            lhc = readsurf('lh.'+surf_fname, subj_code)[0]
            rhc = readsurf('rh.'+surf_fname, subj_code)[0]
            c = np.vstack((lhc, rhc))
        else:
            c = readsurf(surf_fname, subj_code)[0]
    # calculate the Euclidean distance between the input points and the surface vertices
    distances = np.linalg.norm(c-outpoints)
    # which vertex is the closest to the input points
    vtxidx = np.argmin(distances)
    esterr = np.min(distances)

    return (outpoints, vtxidx, esterr)
    

def vtx2fsavg(vtx_idx, subj_code, surf_fname=None):
    """Convert vertex indices from native space to fsaverage space.

    Parameters
    ----------
    vtx_idx : int list
        vertex indices in native space.
    subj_code : str
        subject code/folder in $SUBJECTS_DIR.
    surf_fname : str, optional
        the surface used to obtain the coordinates. 
        
    Returns
    -------
    numpy.ndarray
        the output coordinates in fsaverage space.
    """    
    c = readsurf(surf_fname, subj_code)[0]
    inpoints = c[vtx_idx, ]
    
    # display the input information
    print(f'\nThe input vertex indices are:')
    print(vtx_idx)
    print('The coordinates on the surface are:')
    print(inpoints)
    
    outpoints = self2fsavg(inpoints, subj_code, surf_fname)
    
    return(outpoints)

    