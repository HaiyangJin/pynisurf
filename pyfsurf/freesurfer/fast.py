"""
Tools typically also involve functional data.
"""

import os
import re

def funcdir(func_path=os.getenv('FUNCTIONALS_DIR'), str_pattern='',setdir=True):
    """
    This function creates the structure for a project.

    Args:
        func_path (str, optional): the path to functional data. This path 
            will also be saved as FUNCTIONALS_DIR.. Defaults to 
            os.getenv('FUNCTIONALS_DIR').
        str_pattern (str, optional): the string pattern for session names. It
            will be used to identify all the sessions. E.g., it can be "Face*"
            (without quotes). Defaults to ''.

    Returns:
        str: path to the functional folder.
        str list: a list of session codes.
    """
    if not bool(func_path):
        func_path = os.path.join(os.getenv('SUBJECTS_DIR'), '..', 'functional_data')
        
    # set the environmental variable of FUNCTIONALS_DIR
    os.environ['FUNCTIONALS_DIR'] = func_path
    
    # obtain the session codes
    sess_list = [f for f in os.listdir(func_path) if re.match(str_pattern, f) and '.' not in f]

    return func_path, sess_list
    

def sesslist(sessid='sessid*', func_path = os.getenv('FUNCTIONALS_DIR')):
    """
    This function reads the session ID file and output the session list.

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