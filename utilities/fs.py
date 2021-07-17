import os
import re
from itertools import compress

# subject code and session lists
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
        subj_list (str list): a list of subject codes.
    """
    if bool(stru_path):
        setdir=False
    else:
        stru_path=os.getenv('SUBJECTS_DIR')
    
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
        str list: a list of session names.
    """
    if not bool(func_path):
        func_path = os.getenv('FUNCTIONALS_DIR')
    
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
    
    
# convert/extract information
def tocontrast(fn_list, separator='.', con_sign='-vs-'):
    """This function obtains the contrast name from the strings (e.g., a label 
    name when the label name is something like roi.lh.f13.f-vs-o.*label). It 
    will obtain the strings around '-vs-'.

    Args:
        fn_list (str list): a list of strings (e.g., label names).
        separator (str, optional): delimiter used to parse the fnList into 
            multiple parts and contrast name will be one of the strings. 
            Defaults to '.', which is for obtaining contrast from label name. 
            'os.sep' can be used to obtain contrast name from a path.
        con_sign (str, optional): contrast sign, i.e., the unique strings in
            the contrast names. Defaults to '-vs-'.

    Returns:
        str list: a list of contrast names.
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
        print('Cannot determine if this file is for left or right hemisphere.')
        
    return hemi



def to_hemi_multi(fn_list, fn_only=True):
    """This function determine the hemispheres based on the filenames (if 'lh'
    or 'rh' is included in the filename).

    Args:
        fn_list (str list): a list of filenames.
        fn_only (bool, optional):  whether only check the filename; False:
            also check the path. Defaults to True.

    Returns:
        str: the hemi information.
    """
    hemis = [tohemi(x, fn_only) for x in fn_list]
    
    if len(set(hemis)) > 1:
        print('\nThese files are for both hemispheres.')
    
    return hemis


    
def tosig(fn_list):
    """This function identify the significance p-value from the filename.

    Args:
        fn_list (str): a list of filenames.

    Returns:
        float: the p-value in FreeSurfer.
    """
    if isinstance(fn_list, str): # convert to list if it is not
        fn_list = [fn_list]
            
    # find strings match f\d+ pattern
    pattern = re.compile('f\d+')  
    matches = [[p for p in pattern.finditer(f)] for f in fn_list] 
    sig_str = [''.join([s.group() for s in m]) for m in matches]
    
    # remove f from the matched strings and convert to float
    sig = [float(s[1:]) for s in sig_str]
    
    return sig
        
        

def totemplate(ana_list, patterns=['fsaverage', 'self'], default_str='unknown'):
    """This functions tries to identify the template used in the filename. By 
    default, it will identify {'fsaverage', 'self'}. This function just to
    test if the strings (e.g., 'fsaverage') are contained in the filenames.

    Args:
        ana_list (str list): a list of strings to be checked.
        patterns (list, optional): the pattern strings. Defaults to ['fsaverage', 'self'].
        default_str (str, optional): the default out strings if no patterns are
            identified in filenames. Defaults to 'unknown'.

    Returns:
        [str list]: the templates for each filename. 'unkonwn' denotes
            none of the patterns were found in the filename. 'multiple'  
            denotes at least two of the patterns were found in the filename.
    """
    if isinstance(ana_list, str):
        ana_list = [ana_list]

    n_pattern = len(patterns)       
            
    if isinstance(default_str, str):
        default_str = [default_str]
    
    # template for each combination between ana and pattern
    tmp_template = [y if y in x else '' for x in ana_list for y in patterns]
    
    # join the patterns for each in ana_list
    templates = [''.join(tmp_template[k:(k+n_pattern)]) for k in range(len(tmp_template)) if k%n_pattern==0]
    
    return templates



def ana2con(ana_list, func_path=os.getenv('FUNCTIONALS_DIR')):
    """This function reads the contrast names within the analysis folders.

    Args:
        ana_list (str list): list of analysis names.
        func_path (str, optional): path to functional folder. Defaults 
            to os.getenv('FUNCTIONALS_DIR').

    Returns:
        str list: list of contrast names.
    """
    if not bool(func_path):
        func_path = os.getenv('FUNCTIONALS_DIR')
    
    if isinstance(ana_list, str):
        ana_list = [ana_list]
    
    con_list = [None] * len(ana_list)
    for i, a in enumerate(ana_list):
        con_list[i] = [f.replace('.mat', '') for f in os.listdir(os.path.join(func_path, a)) if f.endswith('.mat')]

    return con_list



# visualization
def colors(color):
    """This function generates default rgb colors.

    Args:
        color (int list): which colors (rows) in 'colors' to be output.

    Returns:
        list: nested list of colors
    """
    clr = [
        [1, 1, 1], # white
        [1, 1, 0], # yellow
        [1, 0, 1], # magneta
        [0, 1, 0], # green
        [.5, 0, 1], # purple
        [0, 1, 1], # blue
        [0, 0, 0], # black
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    
    n_clr = len(clr)
    
    if not bool(color):
        n_color = range(n_clr)
        
    out_colors = [clr[c] for c in range(n_clr) if c in color]
        
    return out_colors
        


