import os
import re
import subprocess
import platform

def fs_version(isnum=0):
    
    # check the if FS version is available
    fscmd = 'recon-all -version'
    status = os.system(fscmd)
    
    if bool(status): 
        print('\nFreeSurfer has not been set up properly...')
        return
    else:  # obtain the FS version if it was set up
        fs_v = str(subprocess.check_output(['recon-all', '-version'], stderr=subprocess.STDOUT), 'utf-8')
    
    if not isnum:
        # output strings
        if not bool(status): # FS was set up
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
        

def fsl_setup(fsl_path='/usr/local/fsl'):
    
    # check if FSL was already set up
    if bool(os.getenv('FSLDIR')):
        print('\nFSL was already set up properly.')
        return
    
    path = os.getenv('PATH')
    os.environ['FSLDIR'] = fsl_path
    os.environ['PATH'] = f'{fsl_path}/bin:{path}'
    os.environ['FSLOUTPUTTYPE'] = 'NIFTI_GZ'
    os.system('export FSLDIR PATH')
    status = os.system('sh ${FSLDIR}/etc/fslconf/fsl.sh')
    
    assert not bool(status), print(f'\nfsl.sh cannot be found at {fsl_path}/etc/fslconf/')
    
    print('\nFSL is set up successfully [I hope so].')
    

def fs_setup(fs_path, fsl_path='/usr/local/fsl', force=0):

    if bool(os.getenv('FREESURFER_HOME')) and force:
        print('\nFreeSurfer was already set up.')
        fs_version()
        return
    
    # Default path to FreeSurfer in Mac or Linux
    if not bool(fs_path):
        if platform.system()=='Darwin':
            fs_path = '/Applications/freesurfer'
        elif platform.system()=='Linux':
            fsPath = '/usr/local/freesurfer'
        else:
            raise Exception('Platform not supported.')
    
    # please ignore this part and just set fsPath as the full path to FreeSurfer
    if os.path.sep not in fs_path:
        # use fsPath as the verion number if fsPath is not a path 
        # (e.g., '5.3', '6.0', '7.1') 
        fs_path = f'/Applications/freesurfer/{fs_path}'
        
    ## Set up FreeSurfer
    os.environ['FREESURFER_HOME'] = fs_path
    os.environ['SUBJECTS_DIR'] = os.path.join(fs_path, 'subjects')
    
    status = os.system(f'source {fs_path}/FreeSurferEnv.sh')
    
    if bool(status):
        os.environ['FREESURFER_HOME'] = ''
        raise Exception(f'SetUpFreeSurfer.sh cannot be found at {fs_path}.')
    
    fsl_setup(fsl_path)
    
    ## Set PATH and environment variable
    path = os.getenv('PATH')
    os.environ['PATH'] = f'/usr/local/bin:{path}' # add /usr/local/bin to PATH
    os.environ['PATH'] = f'{fs_path}/tktools:{path}' # add /Applications/freesurfer/tktools: to PATH
    os.environ['PATH'] = f'{fs_path}/fsfast/bin:{path}' # add /Applications/freesurfer/fsfast/bin: to PATH
    os.environ['PATH'] = f'{fs_path}/bin:{path}' # add /Applications/freesurfer/bin: to PATH
    
    os.environ['FSFAST_HOME'] = os.path.join(fs_path, 'fsfast')
    os.environ['FSF_OUTPUT_FORMAT'] = 'nii.gz'
    os.environ['MNI_DIR'] = os.path.join(fs_path, 'mni')
    
    print('\nFreeSurfer is set up successfully [I hope so].')
    
    ## display the FS version
    fs_version()
            

