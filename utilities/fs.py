import os
import re
from itertools import compress

def subjdir(stru_path=os.getenv('SUBJECTS_DIR'), str_pattern='', setdir=True):
    """This function set up 'SUBJECTS_DIR' and output the subject code list.

    Args:
        stru_path (str, optional): path to $SUBJECTS_DIR folder in FreeSurfer. 
            Defaults to os.getenv('SUBJECTS_DIR').
        str_pattern (str, optional): string pattern used to identify subject
            folders. Defaults to ''.
        setdir (bool, optional): whether set the global env 'SUBJECTS_DIR'. 
            Defaults to True.

    Returns:
        stru_path (str): path to the structural folder.
        subj_list (str): a list of subject codes.
        
    Created by Haiyang Jin (17-7-2021)
    """
    if bool(stru_path):
        setdir=0
    
    # my sceret default path to 'fsaverage'
    if stru_path == 'myfs':
        stru_path = os.path.join(os.getenv('HOME'), 'GoogleDrive', '102_fMRI', 'fMRITemplate')
        
    if setdir:
        os.environ['SUBJECTS_DIR'] = stru_path
        print(f'\n$SUBJECTS_DIR is set as {stru_path} now...')
        
    # subject code information
    subj_list = [f for f in os.listdir(stru_path) if re.match(str_pattern, f) and '.' not in f]
    
    return stru_path, subj_list
    

def sesslist(sessid='sessid*', func_path = os.getenv('FUNCTIONALS_DIR')):
    """This function reads the session ID file and output the session list.

    Args:
        sessid (str, optional): name of the sessiond id file. OR the full name
            of the session id file (with path). Defaults to 'sessid*'.
        func_path (str, optional): the full path to the functional folder.
            Defaults to os.getenv('FUNCTIONALS_DIR').

    Raises:
        Exception: sessid should only match one session id file.

    Returns:
        str: a list of session names.
        
    Created by Haiyang Jin (17-7-2021)
    """
    if os.sep not in sessid:
        sessid_list = [f for f in os.listdir(func_path) if re.match(sessid, f) and '.' not in f]
        n_sessid = len(sessid_list)
    
        if n_sessid > 1:
            raise Exception(f'There are {n_sessid} session ID files. Please specify which you would like to use.')
        elif n_sessid == 0:
            raise Exception(f'Cannot find the session id file ({sessid}).')
        else:
            # create the session id filename (with path)
            sessFilename = os.path.join(func_path, sessid_list[0])
    else:
        # create the session id filename (with path)
        sessFilename = sessid
    
    assert bool(dir(sessFilename)), f'Cannot find the sessiond id file ({sessFilename}).'
    
    # read the session id file
    sess_list = open(sessFilename, 'r').read().split('\n')
    
    return sess_list
    
    
    
def tocontrast(fn_list, separator='.', con_sign='-vs-'):
    """This function obtains the contrast name from the strings (e.g., a label 
    name when the label name is something like roi.lh.f13.f-vs-o.*label). It 
    will obtain the strings around '-vs-'.

    Args:
        fn_list (str): a list of strings (e.g., label names).
        separator (str, optional): delimiter used to parse the fnList into 
            multiple parts and contrast name will be one of the strings. 
            Defaults to '.', which is for obtaining contrast from label name. 
            'os.sep' can be used to obtain contrast name from a path.
        con_sign (str, optional): contrast sign, i.e., the unique strings in
            the contrast names. Defaults to '-vs-'.

    Returns:
        str: a list of contrast names.
        
    Created by Haiyang Jin (17-7-2021)
    """
    # split the fn_list by separator
    fn_sep = [s.split(separator) for s in fn_list]
    # only keep the part matching con_sign
    contrast = [''.join([c for c in f if con_sign in c]) for f in fn_sep]
    
    return contrast
    
    

def tohemi(filename, fn_only=True):
    """This function determine the hemisphere based on the filename.

    Args:
        filename (str): a filename to be checked.
        fn_only (bool, optional): whether only check the filename; False:
            also check the path. Defaults to True.

    Returns:
        str: the hemi information.
        
    Created by Haiyang Jin (17-7-2021)
    """
    
    hemi_bool = [False, False]
    
    if os.sep in filename and fn_only:
        filename = os.listdir(filename)
        
    if 'lh' in filename:
        hemi_bool[0] = True
    
    if 'rh' in filename:
        hemi_bool[1] = True
    
    if sum(hemi_bool)==1:
        hemi = list(compress(['lh', 'rh'], hemi_bool))[0]
    else:
        hemi = ''
        raise Exception('Cannot determine if this file is for left or right hemisphere.')
        
    return hemi

    
    
