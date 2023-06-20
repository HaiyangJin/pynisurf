"""
Utilities that are frequently used in FreeSurfer related analysis.
"""

import os
import re
from itertools import compress

# convert/extract information
def tocontrast(fn_list, separator='.', con_sign='-vs-'):
    """Obtains the contrast name from the strings (e.g., a label 
    name when the label name is something like roi.lh.f13.f-vs-o.*label). It 
    will obtain the strings around '-vs-'.

    Parameters
    ----------
    fn_list : str list
        a list of strings (e.g., label names).
    separator : str, optional
        delimiter used to parse the fnList into multiple parts and contrast name will be one of the strings. Defaults to '.', which is for obtaining contrast from label name. 'os.sep' can be used to obtain contrast name from a path.
    con_sign : str, optional
        contrast sign, i.e., the unique strings in the contrast names, by default '-vs-'

    Returns
    -------
    str list
        a list of contrast names
    """    

    # split the fn_list by separator
    fn_sep = [s.split(separator) for s in fn_list]
    # only keep the part matching con_sign
    contrast = [''.join([c for c in f if con_sign in c]) for f in fn_sep]
    
    return contrast
    

def _tohemi(filename, fn_only=True):
    """This function determine the hemisphere based on the filename.

    Parameters
    ----------
    filename : str
        a filename to be checked.
    fn_only : bool, optional
        whether only check the filename; False: also check the path. Defaults to True.

    Returns
    -------
    str
        the hemi information
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


def tohemi(fn_list, fn_only=True):
    """This function determine the hemispheres based on the filenames (if 'lh'
    or 'rh' is included in the filename).

    Parameters
    ----------
    fn_list : str list
        a list of filenames.
    fn_only : bool, optional
        whether only check the filename; False: also check the path. Defaults to True.

    Returns
    -------
    str
        the hemi information.
    """    

    hemis = [_tohemi(x, fn_only) for x in fn_list]
    
    if len(set(hemis)) > 1:
        print('\nThese files are for both hemispheres.')
    
    return hemis

    
def tosig(fn_list):
    """This function identify the significance p-value from the filename.

    Parameters
    ----------
    fn_list : str
        a list of filenames.

    Returns
    -------
    float
        the p-value in FreeSurfer.
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
    """This functions tries to identify the template used in the filename. By default, it will identify {'fsaverage', 'self'}. This function just to test if the strings (e.g., 'fsaverage') are contained in the filenames.

    Parameters
    ----------
    ana_list : str list
        a list of strings to be checked.
    patterns : list, optional
        the pattern strings, by default ['fsaverage', 'self']
    default_str : str, optional
        the default out strings if no patterns are identified in filenames, by default 'unknown'

    Returns
    -------
    str list
        the templates for each filename. 'unkonwn' denotes none of the patterns were found in the filename. 'multiple' denotes at least two of the patterns were found in the filename.
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

    Parameters
    ----------
    ana_list : str list
        list of analysis names.
    func_path : _type_, optional
        path to functional folder. Defaults to os.getenv('FUNCTIONALS_DIR').

    Returns
    -------
    str list
        list of contrast names.
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

    Parameters
    ----------
    color : int list
        which colors (rows) in 'colors' to be output.

    Returns
    -------
    list
        nested list of colors
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
        