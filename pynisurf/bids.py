"""
Tools for BIDS strcture.
"""

import os, re, glob
import json
from itertools import chain

import pynisurf.utilities as utilities

def bidsdir(bidsdir='', str_pattern='sub-*', setdir=True):
    """Set bidsDir as a global environment "BIDS_DIR". bidsDir's sub-directory should be the BIDS folder, which saves 'sourcedata', 'derivatives', 'sub-x', etc (or some of them).

    Args:
        bidsdir (str): full path to the BIDS direcotry.
        str_pattern (str, optional): wildcard to be used to identify subject list. Defaults to 'sub-*'.
        setdir (bool, optional): set the global environment $BIDS_DIR. Defaults to True.

    Returns:
        bidsdir (str): full path to the BIDS direcotry.
        bidslist (str list): a list of BIDS subjects.
        
    Created on 2023-May-16 by Haiyang Jin (https://haiyangjin.github.io/en/about/)
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
        cmdlist (str list) dcm2bids commands.
        status (boo vec) status of running d2bcmd.
        
    Created on 2023-May-29 by Haiyang Jin (https://haiyangjin.github.io/en/about/)
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
    cmdlist, status = utilities.runcmd(cmdlist, runcmd)
    
    return (cmdlist, status)


def fn2info(fn, secsep='_', valuesep='-', 
            modality=['bold', 'sbref', 'epi', 'T1w', 'T2w', 
            'scans', 'events',
            'inflated', 'midthickness', 'pial', 'smoothwm', 'probseg', 
            'timeseries', 'xfm', 'boldref', 'dseg', 'mask']):
    """Collects the relevant information from the filename by section (<secstr>) and value (<valuestr>) strings.

    Args:
        fn (str): the file name to be parsed.
        secsep (str, optional): the string to be used to separate the filename into different sections. Defaults to '_'.
        valuesep (str, optional): the string to be used to separate each section into fieldname and value. Only the first valuestr will be used. Defaults to '-'.
        modality (list, optional): a list of strings to be identified as 'modality'. Other strings will be identified as 'custom*'. Defaults to ['bold', 'sbref', 'epi', 'T1w', 'T2w', 'scans', 'events', 'inflated', 'midthickness', 'pial', 'smoothwm', 'probseg', 'timeseries', 'xfm', 'boldref', 'dseg', 'mask'].

    Returns:
        info (dict): the information in a dict.
        
    Examples:
        info = fn2info('sub-002_TaskName_ses-001_Run-01_bold.nii.gz')
        info = fn2info('sub-S02_task-TN_run-4_space-fsnative_hemi-L_bold.func.gii')
        info = fn2info('sub-1_task-S_run-4_space-fsLR_den-91k_bold.dtseries.nii')
        
    Created on 2023-May-30 by Haiyang Jin (https://haiyangjin.github.io/en/about/)
    """
    
    # remove the path
    fname = os.path.basename(fn)
    # path = os.path.dirname(fn)
    
    # strings after the first '.' are regarded as extension
    idx = len(fname) 
    re_idx = re.search('\.', fname)
    if re_idx is not None: idx = re_idx.start()
    ext = fname[idx:]
    
    ## Gather information
    # split string by '_' for section (field) and by "-" for value
    sec = fname[:idx].split(secsep)
    
    # deal with values without fieldname
    noFieldn = [valuesep not in each for each in sec]
    backupFields = ['custom%d' % (x+1) for x in range(len(noFieldn))]
    # the last is modality (if applicable)
    if noFieldn[-1]==True & (sec[-1] in modality):
        backupFields[-1] = 'modality'
        
    # update/add fieldname
    for i, v in enumerate(noFieldn):
        if v:
            sec[i] = backupFields[i]+valuesep+sec[i]

    # identify all (the first) {valuesep}
    info = {}
    for isec in sec:
        idx = re.search(valuesep, isec)
        info[isec[:idx.start()]] = isec[idx.start()+1:]
    info['ext'] = ext

    return info
    

def info2fn(info, secsep='_', valuesep='-'):
    """converts info_struct (can be obtained via fn2info()) into a filename (str).

    Args:
        info (dict): the information in a dict.
        secsep (str, optional): the string to be used to separate the filename into different sections. Defaults to '_'.
        valuesep (str, optional): the string to be used to separate each section into fieldname and value. Only the first valuestr will be used. Defaults to '-'.

    Returns:
        fn (str): the output filename.
        
    Examples:
        info = fn2info('sub-002_TaskName_ses-001_Run-01_bold.nii.gz')
        fn = info2fn(info)
        
    Created on 2023-May-30 by Haiyang Jin (https://haiyangjin.github.io/en/about/)
    """
    
    # save extension
    if 'ext' in info.keys():
        ext = info['ext']
        info.pop('ext')
    else:
        ext = ''
        
    # join strings for each section
    sec = []
    for k,v in info.items():
        if k.startswith('custom') or (k=='modality'):
            sec.append(v)
        else:
            sec.append(k+valuesep+v)
    
    # join all sections and add extension
    return secsep.join(sec)+ext

def listfile(filewc='*', subjList='sub-*', modality='func'):
    """Collect the file list for a given modality.

    Args:
        filewc (str, optional): filename wild card to be used to identify files. Defaults to '*', i.e., all files.
        subjList (str, optional): <list str> a list of subject folders in {bidsDir}. OR <str> wildcard strings to match the subject folders via bids_dir(). Defaults to 'sub-*'. Defaults to 'sub-*'.
        modality (str, optional): the moduality folders ('func', 'anat', 'fmap', ...). Defaults to 'func'.

    Returns:
        list: a list of identified files.
    
    Created on 2023-May-30 by Haiyang Jin (https://haiyangjin.github.io/en/about/)
    """    
    
    if isinstance(subjList, str): 
        bidsDir, subjList=bidsdir('', subjList, False)
    else:
        # get bidsDir
        bidsDir, tmp = bidsdir('', 'sub-*', False)
        
    filelist = []
    for theSubj in subjList:
        theSubjDir = os.listdir(os.path.join(bidsDir, theSubj))
        
        if modality in theSubjDir:
            # there are no session folders
            thefile = glob.glob(os.path.join(bidsDir, theSubj, modality, filewc))
        else:
            # there are multiple session folders
            thefile = [glob.glob(os.path.join(bidsDir, theSubj, session, modality, filewc)) for session in theSubjDir]
            thefile = list(chain(*thefile)) # flatten the nested list to a list
        filelist.append(thefile)
        
    return list(chain(*filelist)) # flatten the nested list to a list
    
   
def fixfmap(intendList='*_bold.nii.gz', subjList='sub-*', fmapwc='*.json'):
    """Fix the IntendedFor field in fmap json files. (Probably not useful anymore.)

    Args:
        intendList (str, optional): <list str> a list of files to be assigned to "intendedFor" of fmap json files. OR <str> wildcard strings to identify the files to be assigned to "intendedFor" of fmap json files. Defaults to '*_bold.nii.gz'.
        subjList (str, optional): <list str> a list of subject folders in {bidsDir}. OR <str> wildcard strings to match the subject folders via bids_dir(). Defaults to 'sub-*'.
        fmapwc (str, optional): wildcard for the fmap json files, for which the intendList will be added to. Defaults to '*.json', i.e., all json files in fmap/ will be updated. 

    Raises:
        Exception: sanity check for session information. Data in the same folder should be from the same session.
        
    Created on 2023-May-30 by Haiyang Jin (https://haiyangjin.github.io/en/about/)
    """    
    # make sure fmapwc ends with '.json'
    if not fmapwc.endswith('.json'): fmapwc = fmapwc + '.json'
    
    # get all fmap files
    fmapjosns = listfile(fmapwc, subjList, 'fmap')
        
    ## Fix fmap files
    for ifmap in fmapjosns:
        
        if isinstance(intendList, list):
            # use the list as allintend directly
            allintend = intendList
        else:
            # identify all BOLD runs in func/
            intendfiles = glob.glob(os.path.join(os.path.dirname(ifmap), '..', 'func', intendList))
            
            # check session information
            infos = [fn2info(x) for x in intendfiles]
            ses = [x['ses'] for x in infos if 'ses' in x.keys()]
            if ses is None:
                sesstr = ''
            elif len(set(ses))==1:
                sesstr = 'ses-%s' % ses[0]
            else:
                raise Exception("It seems that more than one session file are included here.")
            
            # get the relative path of all intended files
            allintend = [os.path.join(sesstr, 'func', os.path.basename(x)) for x in intendfiles]
        
        # read the json file
        with open(ifmap) as json_in:
            val = json.load(json_in)
        # add IntendedFor
        val['IntendedFor'] = allintend
        # save the json file
        with open(ifmap, "w") as json_out:
            json.dump(val, json_out, indent=4)


def fixfunc(taskName, subjList='sub-*', taskwc='*.json'):
    """Fix the TaskName field in func json files.

    Args:
        taskName (str): task name to be added to the files identified by {taskStr}.
        subjList (str, optional): <list str> a list of subject folders in {bidsDir}. OR <str> wildcard strings to match the subject folders via bids_dir(). Defaults to 'sub-*'.
        taskwc (str, optional): wildcard strings to identify a list of func runs, for which 'TaskName' will be added to their json files. Defaults to '*.json' and then all func files are treated as one task. The name will be {taskName}.
    
    Created on 2023-May-30 by Haiyang Jin (https://haiyangjin.github.io/en/about/)
    """    
    
    # make sure taskwc ends with '.json'
    if not taskwc.endswith('.json'): taskwc = taskwc + '.json'
    
    # get all func josn files
    funcjosns = listfile(taskwc, subjList, 'func')
    
    # add task name
    for ifunc in funcjosns:
        # read the json file
        with open(ifunc) as json_in:
            val = json.load(json_in)
        # add TaskName
        val['TaskName'] = taskName
        # save the json file
        with open(ifunc, "w") as json_out:
            json.dump(val, json_out, indent=4)
    
     
            
        

