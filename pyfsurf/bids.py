"""
Tools for BIDS strcture.
"""

import os
import re

def bidsdir(bidsdir, str_pattern='sub-*', setdir=True):
    """_summary_

    Args:
        bidsdir (_type_): _description_
        str_pattern (str, optional): _description_. Defaults to 'sub-*'.
        setdir (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    
    if not bool(bidsdir):
        bidsdir = os.getenv('BIDS_DIR')
        
    # set the environment variable of BIDS_DIR
    if setdir:
        os.environ['BIDS_DIR'] = bidsdir
        print(f'\n$BIDS_DIR is set as {bidsdir} now...')
    
    # obtain the session codes
    bidslist = [f for f in os.listdir(bidsdir) if re.match(str_pattern, f) and '.' not in f]

    return bidsdir, bidslist
    
