"""
Tools typically also involve functional data.
"""

import os
import re

def funcdir(func_dir=os.getenv('FUNCTIONALS_DIR'), str_pattern=None, set_dir=True):
    """Set the FUNCTIONAL_DIR environment variable and return the path

    Parameters
    ----------
    func_dir : str, optional
        the path to functional data. This path will also be saved as $FUNCTIONALS_DIR., by default os.getenv('FUNCTIONALS_DIR')
    str_pattern : str, optional
        the string pattern for session names. It will be used to identify all the sessions. E.g., it can be "Face*" (without quotes)., by default None
    set_dir : bool, optional
        whether to set the global environment, by default True

    Returns
    -------
    str
        path to the functional folder.
    str list
        a list of session codes.
    """    

    if not bool(func_dir):
        func_dir = os.path.join(os.getenv('SUBJECTS_DIR'), '..', 'functionals')
        
    if set_dir:
        # set the environment variable of FUNCTIONALS_DIR
        os.environ['FUNCTIONALS_DIR'] = func_dir
    
    # obtain the session codes
    sess_list = [f for f in os.listdir(func_dir) if re.match(str_pattern, f) and '.' not in f]

    return func_dir, sess_list
    

def sesslist(sessid='sessid*', func_dir = os.getenv('FUNCTIONALS_DIR')):
    """This function reads the session ID file and output the session list.

    Parameters
    ----------
    sessid : str, optional
        name of the sessiond id file. OR the full name of the session id file (with path), by default 'sessid*'
    func_dir : _type_, optional
        the full path to the functional folder, by default os.getenv('FUNCTIONALS_DIR')

    Returns
    -------
    str list
        a list of session names.

    Raises
    ------
    Exception
        sessid should only match one session id file
    """    
    
    if not bool(func_dir):
        func_dir = os.getenv('FUNCTIONALS_DIR')
    
    if os.sep not in sessid:
        sessid_list = [f for f in os.listdir(func_dir) if re.match(sessid, f) and '.' not in f]
        n_sessid = len(sessid_list)
    
        if n_sessid > 1:
            raise Exception(f'There are {n_sessid} session ID files. Please specify which you would like to use.')
        elif n_sessid == 0:
            raise Exception(f'Cannot find the session id file ({sessid}).')
        else:
            # create the session id filename (with path)
            sess_fname = os.path.join(func_dir, sessid_list[0])
    else:
        # create the session id filename (with path)
        sess_fname = sessid
    
    assert bool(dir(sess_fname)), f'Cannot find the sessiond id file ({sess_fname}).'
    
    # read the session id file
    sess_list = open(sess_fname, 'r').read().split('\n')
    
    return sess_list