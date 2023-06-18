"""
Tools typically also involve functional data.
"""

import os
import re

def funcdir(funcdir=os.getenv('FUNCTIONALS_DIR'), str_pattern='',setdir=True):
    """Set the FUNCTIONAL_DIR environment variable and return the path

    Parameters
    ----------
    funcdir : str, optional
        the path to functional data. This path will also be saved as $FUNCTIONALS_DIR., by default os.getenv('FUNCTIONALS_DIR')
    str_pattern : str, optional
        the string pattern for session names. It will be used to identify all the sessions. E.g., it can be "Face*" (without quotes)., by default ''
    setdir : bool, optional
        whether to set the global environment, by default True

    Returns
    -------
    str
        path to the functional folder.
    str list
        a list of session codes.
    """    

    if not bool(funcdir):
        funcdir = os.path.join(os.getenv('SUBJECTS_DIR'), '..', 'functionals')
        
    if setdir:
        # set the environment variable of FUNCTIONALS_DIR
        os.environ['FUNCTIONALS_DIR'] = funcdir
    
    # obtain the session codes
    sess_list = [f for f in os.listdir(funcdir) if re.match(str_pattern, f) and '.' not in f]

    return funcdir, sess_list
    

def sesslist(sessid='sessid*', funcdir = os.getenv('FUNCTIONALS_DIR')):
    """This function reads the session ID file and output the session list.

    Parameters
    ----------
    sessid : str, optional
        name of the sessiond id file. OR the full name of the session id file (with path), by default 'sessid*'
    funcdir : _type_, optional
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
    
    if not bool(funcdir):
        funcdir = os.getenv('FUNCTIONALS_DIR')
    
    if os.sep not in sessid:
        sessid_list = [f for f in os.listdir(funcdir) if re.match(sessid, f) and '.' not in f]
        n_sessid = len(sessid_list)
    
        if n_sessid > 1:
            raise Exception(f'There are {n_sessid} session ID files. Please specify which you would like to use.')
        elif n_sessid == 0:
            raise Exception(f'Cannot find the session id file ({sessid}).')
        else:
            # create the session id filename (with path)
            sessFilename = os.path.join(funcdir, sessid_list[0])
    else:
        # create the session id filename (with path)
        sessFilename = sessid
    
    assert bool(dir(sessFilename)), f'Cannot find the sessiond id file ({sessFilename}).'
    
    # read the session id file
    sess_list = open(sessFilename, 'r').read().split('\n')
    
    return sess_list