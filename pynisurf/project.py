import os
import re
import subprocess
import platform

import pynisurf.freesurfer as fs
import pynisurf.bids as bids

def fs_version(isnum=False, toprint=True):
    
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
        

def fsl_setup(fsldir='/usr/local/fsl'):
    
    # check if FSL was already set up
    if bool(os.getenv('FSLDIR')):
        print('\nFSL was already set up properly.')
        return
    
    path = os.getenv('PATH')
    os.environ['FSLDIR'] = fsldir
    os.environ['PATH'] = f'{fsldir}/bin:{path}'
    os.environ['FSLOUTPUTTYPE'] = 'NIFTI_GZ'
    os.system('export FSLDIR PATH')
    status = os.system('sh ${FSLDIR}/etc/fslconf/fsl.sh')
    
    assert not bool(status), print(f'\nfsl.sh cannot be found at {fsldir}/etc/fslconf/')
    
    print('\nFSL is set up successfully [I hope so].')
    

def fs_setup(fsdir, fsldir='/usr/local/fsl', force=0):

    if bool(os.getenv('FREESURFER_HOME')) and force:
        print('\nFreeSurfer was already set up.')
        fs_version()
        return
    
    # Default path to FreeSurfer in Mac or Linux
    if not bool(fsdir):
        if platform.system()=='Darwin':
            fsdir = '/Applications/freesurfer'
        elif platform.system()=='Linux':
            fsPath = '/usr/local/freesurfer'
        else:
            raise Exception('Platform not supported.')
    
    # please ignore this part and just set fsPath as the full path to FreeSurfer
    if os.path.sep not in fsdir:
        # use fsPath as the verion number if fsPath is not a path 
        # (e.g., '5.3', '6.0', '7.3') 
        fsdir = f'/Applications/freesurfer/{fsdir}'
        
    ## Set up FreeSurfer
    os.environ['FREESURFER_HOME'] = fsdir
    os.environ['SUBJECTS_DIR'] = os.path.join(fsdir, 'subjects')
    
    status = os.system(f'source {fsdir}/FreeSurferEnv.sh')
    
    if bool(status):
        os.environ['FREESURFER_HOME'] = ''
        raise Exception(f'SetUpFreeSurfer.sh cannot be found at {fsdir}.')
    
    fsl_setup(fsldir)
    
    ## Set PATH and environment variable
    path = os.getenv('PATH')
    os.environ['PATH'] = f'/usr/local/bin:{path}' # add /usr/local/bin to PATH
    os.environ['PATH'] = f'{fsdir}/tktools:{path}' # add /Applications/freesurfer/tktools: to PATH
    os.environ['PATH'] = f'{fsdir}/fsfast/bin:{path}' # add /Applications/freesurfer/fsfast/bin: to PATH
    os.environ['PATH'] = f'{fsdir}/bin:{path}' # add /Applications/freesurfer/bin: to PATH
    
    os.environ['FSFAST_HOME'] = os.path.join(fsdir, 'fsfast')
    os.environ['FSF_OUTPUT_FORMAT'] = 'nii.gz'
    os.environ['MNI_DIR'] = os.path.join(fsdir, 'mni')
    
    print('\nFreeSurfer is set up successfully [I hope so].')
    
    ## display the FS version
    fs_version()
            
class project:
    '''
    Create a project and store the relevant information.
    '''
   
    def __init__(self, fsdir='', bidsdir='', subjdir='', funcdir='', str_pattern='sub-*'):
        
        fs_setup(fsdir) # setup FreeSurfer
        self.fsversion = fs_version('', False)
        
        # set up BIDS
        self.bidsdir, self.bidslist = bids.bidsdir(bidsdir, str_pattern)
        self.source = os.path.join(self.bidsdir, 'sourcedata')
        
        # set up SUBJECTS_DIR & FUNCTIONALS_DIR
        if not bool(subjdir):
            subjdir = os.path.join(self.bidsdir, 'derivatives', 'subjects')
        self.updatesubjdir(subjdir, str_pattern)
        # self.subjdir, self.subjlist = fs.subjdir(subjdir, str_pattern)
            
        if not bool(funcdir):
            funcdir = os.path.join(self.bidsdir, 'derivatives', 'functionals')
        self.updatefuncdir(funcdir, str_pattern)
        # self.funcdir, self.funclist = fs.funcdir(funcdir, str_pattern)
    
    def updatesubjdir(self, subjdir, str_pattern='sub-*'):
        self.subjdir, self.subjlist = fs.subjdir(subjdir, str_pattern)
    
    def updatefuncdir(self, funcdir, str_pattern='sub-*'):
        self.funcdir, self.funclist = fs.funcdir(funcdir, str_pattern)
    
        
        
  