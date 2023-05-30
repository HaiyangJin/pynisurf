"""
Tools for BIDS strcture.
"""

import os
import re
from itertools import chain

import pynisurf.utilities as utilities

def bidsdir(bidsdir, str_pattern='sub-*', setdir=True):
    """Set bidsDir as a global environment "BIDS_DIR". bidsDir's sub-directory should be the BIDS folder, which saves 'sourcedata', 'derivatives', 'sub-x', etc (or some of them).

    Args:
        bidsdir (str): full path to the BIDS direcotry.
        str_pattern (str, optional): wildcard to be used to identify subject list. Defaults to 'sub-*'.
        setdir (bool, optional): set the global environment $BIDS_DIR. Defaults to True.

    Returns:
        bidsdir (str): full path to the BIDS direcotry.
        bidslist (str list): a list of BIDS subjects.
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
    
def dcm2bids(dcmSubj, bidsSubj='', config='', isSess=False, runcmd=True):
    """Convert DICOM to BIDS with dcm2bids.

    Args:
        dcmSubj (str list OR str): a list of subject folders storing DICOM files. [OR] a wildcard string to match the subject folders storing saving DICOM files.
        bidsSubj (str list OR str, optional): a list of output BIDS subject codes (e.g., {'X01', 'X02', ...}). It needs to have the same length as dcmSubj. Default is {'01', '02', ...} depending on dcmSubj. It only makes sense to input a list of string when {dcmSubj} is also a list of str. Each string in {dcmSubj} correspond to each string in {bidsSubj}. [OR] strings to be put before {'01', '02, ...}.E.g., when bidsSubj is 'Test', the subjcode will be 'sub-Test01', 'sub-Test02'. Defaults to ''.
        config (str, optional): the config file to deal with dicoms. Defaults to '{$BIDS_DIR}/codes/bids_convert.json'.
        isSess (boo or int, optional): If there are multiple subdir within dcmSubj dir, whether these dirctories are sessions (or runs). Default is False (i.e., runs). Note that if run folders are mistaken as session folders, each run will be saved as a separate session. No messages will be displayed for this case but you will notice it in the output. A special usage of isSess is: when isSess is not 0 and there is only one folder withi9n subdir, isSess will be used as the session code.
        runcmd (int, optional): Whether to run the commands. Defaults to True.

    Returns:
        d2bcmd (str list) dcm2bids commands.
        isnotok (boo vec) status of running d2bcmd.
    """
    
    ## Deal with inputs
    bidsdir = os.getenv('BIDS_DIR')
    
    if not bool(config):
        config=os.path.join(bidsdir, 'codes', 'bids_convert.json')
    # make sure the config file exist
    assert os.path.isfile(config), (f'Cannot find the config file:\n%s', config)
    
    dcmdir = os.path.join(bidsdir, 'sourcedata')
    assert os.path.isdir(dcmdir), (f'Cannot find sourcedata/ in %s', bidsdir)
    
    # input subj list
    if isinstance(dcmSubj, str):
        # treat dcmSubj as wildcard
        dsubjList = [f for f in os.listdir(dcmdir) if re.match(dcmSubj, f) and '.' not in f]
    elif isinstance(dcmSubj, list):
        dsubjList = dcmSubj
        
    # output BIDS subj list
    if isinstance(bidsSubj, str):
        bidsSubj = ['%s%02d' % (bidsSubj,idx+1) for idx in range(len(dsubjList))]
    assert len(dsubjList)==len(bidsSubj), (f'The length of "dcmSubj" (%d) and "bidsSubj" (%d) is not the same.', len(dsubjList), len(bidsSubj))
    
    ## Make the cmd for dcm2bids
    cmdlist = [None] * len(bidsSubj)
    
    for iSubj in range(len(bidsSubj)):
        
        # add full path if needed
        thisdabs = os.path.join(dcmdir, dsubjList[iSubj])
        dcmSess = [d for d in os.listdir(thisdabs) if os.path.isdir(os.path.join(thisdabs,d))]
                    
        if not bool(dcmSess):
            # if no sub-dir is found in dcmDir, there is only 1 session
            cmd = 'dcm2bids -d %s -o %s -p %s -c %s --forceDcm2niix --clobber' % (utilities.cmdpath(thisdabs), utilities.cmdpath(bidsdir), bidsSubj[iSubj], config)
            
        elif not isSess:
            # if the sub-dir in dsubjDir are runs (instead of sessions)
            runfolders = [os.path.join(thisdabs, run) for run in dcmSess]
            cmd = 'dcm2bids -d %s -o %s -p %s -c %s --forceDcm2niix --clobber' % (' '.join(runfolders), utilities.cmdpath(bidsdir), bidsSubj[iSubj], config)
            
        elif isSess:
            # each sub-dir is one session
            dcmid = range(len(dcmSess))
            sessid = range(1, len(dcmSess)+1)
            if len(dcmid)==1: sessid = isSess # customize the session number

            # if the subdir in dsubjDir are sessions
            cmd = ['dcm2bids -d %s -o %s -p %s -s %d -c %s --forceDcm2niix --clobber' % (utilities.cmdpath(os.path.join(thisdabs, dcmSess[dcmid[x]])), utilities.cmdpath(bidsdir), bidsSubj[iSubj], sessid[x], config) for x in dcmid]
                        
        cmdlist[iSubj] = cmd
    # flatten the nested list to a list
    cmdlist = list(chain(*cmdlist))
           
    ## Run cmd
    cmdlisttmp, isnotok = utilities.runcmd(cmdlist, runcmd)
    
    return (cmdlisttmp, isnotok)
   
