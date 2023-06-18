"""
Tools for BIDS structure.
Created by Haiyang Jin (https://haiyangjin.github.io/en/about/)
"""

import os, re, glob, shutil
import json
from itertools import chain

import pynisurf.utilities as uti

def bidsdir(bidsDir='', subjwc='sub-*', setdir=True):
    """Set bidsDir as a global environment "BIDS_DIR". bidsDir's sub-directory should be the BIDS folder, which saves 'sourcedata', 'derivatives', 'sub-x', etc (or some of them).

    Parameters
    ----------
    bidsDir : str, optional
        full path to the BIDS direcotry, by default ''
    subjwc : str, optional
        wildcard to be used to identify subject list, by default 'sub-*'
    setdir : bool, optional
        set the global environment $BIDS_DIR, by default True

    Returns
    -------
    str
        full path to the BIDS direcotry
    str list
        a list of subject folders in `bidsDir`.

    Created on 2023-May-16 by Haiyang Jin (https://haiyangjin.github.io/en/about/)
    """
    
    if not bool(bidsDir):
        bidsDir = os.getenv('BIDS_DIR')
        
    # set the environment variable of BIDS_DIR
    if setdir:
        os.environ['BIDS_DIR'] = bidsDir
        print(f'\n$BIDS_DIR is set as {bidsDir} now...')
    
    # obtain the session codes
    bidslist = [f for f in os.listdir(bidsDir) if re.match(subjwc, f) and '.' not in f]

    return bidsDir, bidslist
    
    
def dcm2bids(dcmSubj, bidsSubj='', config='', isSess=False, runcmd=True):
    """Convert DICOM to BIDS with dcm2bids.

    Parameters
    ----------
    dcmSubj : str, str list
        A list of subject codes/folders storing DICOM files (if `dcmSubj` is str list); OR a wildcard string to match the subject folders storing DICOM files (if `dcmSubj` is str).
    bidsSubj : str, optional
        A list of output BIDS subject codes (e.g., {'X01', 'X02', ...}). It needs to have the same length as `dcmSubj`. Default is {'01', '02', ...} depending on `dcmSubj`. It only makes sense to input a list of string when `dcmSubj` is also a str list. Each string in `dcmSubj` correspond to each string in `bidsSubj`. [OR] strings to be put before {'01', '02, ...}.E.g., when `bidsSubj` is 'Test', the subjcode will be 'sub-Test01', 'sub-Test02'. Defaults to ''.
    config : str, optional
        the config file to deal with dicoms. Defaults to '{$BIDS_DIR}/code/bids_convert.json'.
    isSess : bool, optional
        If there are multiple subdir within dcmSubj dir, whether these dirctories are sessions (or runs). Default is False (i.e., runs). Note that if run folders are mistaken as session folders, each run will be saved as a separate session. No messages will be displayed for this case but you will notice it in the output. A special usage of `isSess` is: when `isSess` is not 0 and there is only one folder within the directory, `isSess` will be used as the session code.
    runcmd : bool, optional
        whether to run the commands. Defaults to True.

    Returns
    -------
    cmdlist : str list
        dcm2bids commands.
    status : boo vec
        status of running d2bcmd. True if no error.
    """
    
    ## Deal with inputs
    bidsDir = bidsdir(setdir=False)[0]
    
    if not bool(config):
        config=os.path.join(bidsDir, 'code', 'bids_convert.json')
    # make sure the config file exist
    assert os.path.isfile(config), (f'Cannot find the config file:\n%s', config)
    
    dcmdir = os.path.join(bidsDir, 'sourcedata')
    assert os.path.isdir(dcmdir), (f'Cannot find sourcedata/ in %s', bidsDir)
    
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
            cmd = 'dcm2bids -d %s -o %s -p %s -c %s --forceDcm2niix --clobber' % (uti.cmdpath(thisdabs), uti.cmdpath(bidsDir), bidsSubj[iSubj], config)
            
        elif not isSess:
            # if the sub-dir in dsubjDir are runs (instead of sessions)
            runfolders = [os.path.join(thisdabs, run) for run in dcmSess]
            cmd = 'dcm2bids -d %s -o %s -p %s -c %s --forceDcm2niix --clobber' % (' '.join(runfolders), uti.cmdpath(bidsDir), bidsSubj[iSubj], config)
            
        elif isSess:
            # each sub-dir is one session
            dcmid = range(len(dcmSess))
            sessid = range(1, len(dcmSess)+1)
            if len(dcmid)==1: sessid = isSess # customize the session number

            # if the subdir in dsubjDir are sessions
            cmd = ['dcm2bids -d %s -o %s -p %s -s %d -c %s --forceDcm2niix --clobber' % (uti.cmdpath(os.path.join(thisdabs, dcmSess[dcmid[x]])), uti.cmdpath(bidsDir), bidsSubj[iSubj], sessid[x], config) for x in dcmid]
                        
        cmdlist[iSubj] = cmd
    # flatten the nested list to a list
    cmdlist = list(chain(*cmdlist))
           
    ## Run cmd
    cmdlist, status = uti.runcmd(cmdlist, runcmd)
    
    return (cmdlist, status)


def fn2info(filename, secsep='_', valuesep='-', 
            modality=['bold', 'sbref', 'epi', 'T1w', 'T2w', 
            'scans', 'events',
            'inflated', 'midthickness', 'pial', 'smoothwm', 'probseg', 
            'timeseries', 'xfm', 'boldref', 'dseg', 'mask']):
    """Collects the relevant information from the filename by section (<secstr>) and value (<valuestr>) strings.

    Parameters
    ----------
    filename : str
        the file name to be parsed.
    secsep : str, optional
        the string to be used to separate the filename into different sections. Defaults to '_'.
    valuesep : str, optional
        the string to be used to separate each section into fieldname and value. Only the first valuestr will be used. Defaults to '-'.
    modality : str list, optional
        a list of strings to be identified as `modality`. Other strings will be identified as 'custom*'. Defaults to ['bold', 'sbref', 'epi', 'T1w', 'T2w', 'scans', 'events', 'inflated', 'midthickness', 'pial', 'smoothwm', 'probseg', 'timeseries', 'xfm', 'boldref', 'dseg', 'mask'].

    Returns
    -------
    dict
        the filename information in a dict.
            
    Examples
    --------
        info = fn2info('sub-002_TaskName_ses-001_Run-01_bold.nii.gz')
        info = fn2info('sub-S02_task-TN_run-4_space-fsnative_hemi-L_bold.func.gii')
        info = fn2info('sub-1_task-S_run-4_space-fsLR_den-91k_bold.dtseries.nii')
    """
    
    # remove the path
    fname = os.path.basename(filename)
    # path = os.path.dirname(filename)
    
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
    """Converts info_struct (can be obtained via `fn2info()`) into a filename (str).

    Parameters
    ----------
    info : dict
        the information in a dict. See the output of `fn2info()`.
    secsep : str, optional
        the string to be used to separate the filename into different sections. Defaults to '_'.
    valuesep : str, optional
        the string to be used to separate each section into fieldname and value. Only the first valuestr will be used. Defaults to '-'.

    Returns
    -------
    str
        the output filename.
    
    Examples
    --------
        info = fn2info('sub-002_TaskName_ses-001_Run-01_bold.nii.gz')
        fn = info2fn(info)
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

    Parameters
    ----------
    filewc : str, optional
        filename wild card to be used to identify files. Defaults to '*', i.e., all files.
    subjList : str OR str list, optional
        <list str> a list of subject folders in `bidsDir`. OR <str> wildcard strings to match the subject folders via `bids_dir()`. Defaults to 'sub-*'.
    modality : str, optional
        the moduality folders ('func', 'anat', 'fmap', ...). Defaults to 'func'.

    Returns
    -------
    list
        a list of identified files.
    """    
    
    if isinstance(subjList, str): 
        bidsDir, subjList=bidsdir('', subjList, False)
    else:
        # get bidsDir
        bidsDir = bidsdir(setdir=False)[0]
        
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
    """Fix the IntendedFor field in fmap json files. (Probably not useful anymore. It seems that this issue has been fixed in dcm2bids)

    Parameters
    ----------
    intendList : str, optional
        <list str> a list of files to be assigned to "intendedFor" of fmap json files. OR <str> wildcard strings to identify the files to be assigned to "intendedFor" of fmap json files. Defaults to '*_bold.nii.gz'.
    subjList : str, optional
        <list str> a list of subject folders in `bidsDir`. OR <str> wildcard strings to match the subject folders via `bids_dir()`. Defaults to 'sub-*'.
    fmapwc : str, optional
        wildcard for the fmap json files, for which the intendList will be added to. Defaults to '*.json', i.e., all json files in fmap/ will be updated.

    Raises
    ------
    Exception
        sanity check for session information. Data in the same folder should be from the same session.
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

    Parameters
    ----------
    taskName : str
        task name to be added to the files identified by `taskName`.
    subjList : str, optional
        `list str` a list of subject folders in `bidsDir`. OR `str` wildcard strings to match the subject folders via `bids_dir()`. Defaults to 'sub-*'.
    taskwc : str, optional
        wildcard strings to identify a list of func runs, for which `TaskName` will be added to their json files. Defaults to '*.json' and then all func files are treated as one task. The name will be `taskName`.
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
    
     
def cpevent(subjCode, eventwd='', runwd='*_bold.nii.gz', ses=''):  
    """Copy event files to the BIDS folder.

    Parameters
    ----------
    subjCode : str
        subject code in `bidsDir`.
    eventwd : str, optional
        wildcard strings to be used to identify the event files to be copied. Defaults to ''.
    runwd : str, optional
        wildcard strings to be used to identify the functional runs (BOLD), whose names will be used as the new names for the event files. Defaults to '*_bold.nii.gz'.
    ses : str, optional
        the session name. Default to '', i.e., no session informaiton/folder is available.

    Returns
    -------
    str list
        a list of srouce files.
    str list
         a list of destination files.
    """
    
    ## Deal with inputs
    bidsDir, subjList = bidsdir(setdir=False)
    assert subjCode in subjList, (f'Cannot find {subjCode} in {bidsDir}.')  
    
    # wildcard for the event files and runs
    if isinstance(eventwd, str): eventwd = [eventwd]
    if isinstance(runwd, str): runwd = [runwd]
    nwd = len(eventwd)
    assert nwd==len(runwd), (f'The length of "eventwd" (%d) and "runwd" (%d) is not the same.', nwd, len(runwd))
        
    # set session info
    if isinstance(ses, int): ses = str(ses)
    if isinstance(ses, str) & (not ses.startswith('ses-')): ses = 'ses-'+ses

    # Find and copy files
    srclist = []
    dstlist = []
    for iwd in range(nwd):
        
        # source files
        src = sorted(glob.glob(eventwd[iwd]))
        assert bool(src), (f'Cannot find %s in pwd.') % (eventwd[iwd])
        
        # destination files
        runs = sorted(glob.glob(os.path.join(bidsDir, subjCode, ses, 'func', runwd[iwd])))
        assert bool(runs), (f'Cannot find %s in %s.') % (runwd[iwd], os.path.join(bidsDir, subjCode, ses, 'func'))
        dst = [r.replace('_bold.nii.gz', '_events.tsv') for r in runs]
        
        # copy files
        [shutil.copyfile(src[i], dst[i]) for i in range(len(src))]
        
        # save src and dst lists
        srclist+=src
        dstlist+=dst
    
    return srclist, dstlist


def dupsbref(subjCode, sbrefwc='*sbref.nii.gz', boldwc='*_bold.nii.gz', rmsrc=False):
    """Duplicate the single-band reference for each of the matched bold runs.

    Parameters
    ----------
    subjCode : str list, str
        a list of subject folders in `bidsDir`. OR <str> wildcard strings to match the subject folders via `bids_dir()`. 
    sbrefwc : str, optional
        wildcard strings to identify the single-band reference files.
    boldwc : str, optional
        wildcard strings to identify the functional runs (BOLD).
    rmsrc : bool, optional
        whether to remove the original sbref files. Defaults to False.
    """
    
    # find all sb refs for this subject
    sbrefs = listfile(sbrefwc, subjCode, 'func')
    
    # duplicate the sbref for each bold run
    for sbref in sbrefs:
        # find the bold runs
        bold = glob.glob(os.path.join(os.path.dirname(sbref), boldwc))
        assert bool(bold), (f'Cannot find any BOLD files (%s) matching the single-band reference (%s).') % (boldwc, sbref)
        
        # repeat the sbref for each bold run
        [shutil.copyfile(sbref, b.replace('_bold.nii.gz', '_sbref.nii.gz')) for b in bold]
            
        # remove the sbref if needed
        if rmsrc: 
            os.remove(sbref)
    

def mkignore(ignorelist=['tmp_dcm2bids/','tmp/','code/']):
    """Make .bidsignore file in the BIDS folder.

    Parameters
    ----------
    ignorelist : list, optional
        directories or files to be ignored, by default ['tmp_dcm2bids/','tmp/','code/']
    """    
    
    # get bids dir
    bidsDir=bidsdir(setdir=False)[0]
    # make .gitignore
    uti.mkfile(ignorelist, os.path.join(bidsDir, '.bidsignore'))
    
    
def mktsv(content='sub-*', fname='participants.tsv', header='participant_id'):
    """Make participants.tsv file in the BIDS folder.

    Parameters
    ----------
    content : str, optional
        <list str> a list of subject folders in `bidsDir`. OR <str> wildcard strings to match the subject folders via `bids_dir()`. Defaults to 'sub-*'.
    fname : str, optional
        the name of the tsv file. Defaults to 'participants.tsv'.
    header : str, optional
        the header of the tsv file. Defaults to 'participant_id'.
    """
        
    # get bids dir
    bidsDir=bidsdir(setdir=False)[0]
    # get list of subjects if content is a string
    if isinstance(content, str):
        content = bidsdir(subjwc=content, setdir=False)[1]
    # make sure fname ends with '.tsv'
    if not fname.endswith('.tsv'): fname = fname + '.tsv'
    
    # make participant tsv file
    content.insert(0, header)
    uti.mkfile(content, os.path.join(bidsDir, fname))
    

def mkreadme():
    """Make README.md file in the BIDS folder.
    """
    
    # get bids dir
    bidsDir=bidsdir(setdir=False)[0]
    # copy README.md
    shutil.copyfile(os.path.join(os.path.dirname(__file__), 'resources', 'README.md'), os.path.join(bidsDir, 'README.md'))
    
    
def scaffold(force=False):
    """Make .bidsignore, participants.tsv, and README.md files in the BIDS folder.

    Parameters
    ----------
    force : bool, optional
        whether to overwrite the existing files. Defaults to False.
    """
    
    # get bids dir
    bidsDir=bidsdir(setdir=False)[0]
    
    if not os.path.isfile(os.path.join(bidsDir, '.bidsignore')) or force:
        mkignore()
    if not os.path.isfile(os.path.join(bidsDir, 'participants.tsv')) or force:
        mktsv()
    if not os.path.isfile(os.path.join(bidsDir, 'README.md')) or force:
        mkreadme()
    
    
def validator(runcmd=True):
    """Run bids_validator. This function needs Docker.

    Parameters
    ----------
    runcmd : bool, optional
        whether to run the command, by default True

    Returns
    -------
    int
        status of running the command. 0 if no error.
    """
    
    # get bids dir
    bidsDir=bidsdir(setdir=False)[0]
    # make the command for bids_validator
    cmd = 'docker run --rm -v %s:/data:ro bids/validator /data' % bidsDir
    # run the command
    return uti.runcmd(cmd, runcmd=runcmd)[1]
    
        
def fmriprep(subjCode, **kwargs):
    """Run fmriprep for one subject. This function needs Docker.

    Parameters
    ----------
    subjCode : str
        subject code in `bidsDir`.
        
    Keyword Arguments
    -----------------
    fslicense : str, optional
        path to FreeSurfer license key file. Defaults to '$HOME/Documents/license.txt'.
    outspace : str, optional
        the name of the output space. Defaults to 'fsnative fsaverage T1w MNI152NLin2009cAsym'.
    cifti : str, optional
        the resolution of the output CIFTI file. Defaults to ''.
    nthreads : int, optional
        number of threads per-process. Defaults to 8.
    maxnthreads : int, optional
        maximum number of threads per-process. Defaults to 8.
    wd : str, optional
        working dicrectory. Defaults to a folder ending with '_work' at the same level with `bidsDir`. For example, if `bidsDir` is `path/to/bids`, the default `wd` will be `path/to/bids_work`.
    ignore : str, optional
        steps to be ignored in fmriprep, e.g., {fieldmaps,slicetiming,sbref}. Defaults to ''.
    runcmd : bool, optional
        whether to run the command. Defaults to True.
    extracmd : str, optional
        extra command line arguments. Defaults to '--no-tty'.
    pathtofmriprep : str, optional
        path to fmriprep. Defaults to ''.

    Returns
    -------
    str
        the full fmriprep command.
    int 
        the status of the fmriprep command. 0 if no error.
    
    Examples
    --------
        fmriprep('sub-01')
    """
    
    defaultKwargs = {'fslicense':'$HOME/Documents/license.txt', 
                     'outspace':'fsnative fsaverage T1w MNI152NLin2009cAsym', # fsaverage6
                     'cifti':'',    # --cifti-output 91k 170k
                     'nthreads':8,     # above 8 does not seem to help (?)
                     'maxnthreads':4,  # maximum number of threads per-process
                     'wd': '',         # working dicrectory
                     'ignore': '',     # {fieldmaps,slicetiming,sbref}
                     'runcmd': True,
                     'extracmd':'--no-tty', # not use TTY --use-aroma --ignore slicetiming 
                     'pathtofmriprep':''}
    kwargs = {**defaultKwargs, **kwargs}
    
    bidsDir, subjList=bidsdir(setdir=False)

    if not subjCode.startswith('sub-'): subjCode = 'sub-'+subjCode
    assert subjCode in subjList, (f'Cannot find {subjCode} in {bidsDir}.')
    
    ## Deal with kwargs
    extracmd = []
    if bool(kwargs['fslicense']) and '--fs-license-file' not in kwargs['extracmd']:
        extracmd += ['--fs-license-file %s --fs-subjects-dir %s/derivatives/freesurfer/' % (kwargs['fslicense'], bidsDir)]
    else:
        extracmd += ['--no-freesurfer']
        
    if bool(kwargs['outspace']) and '--output-spaces %s' not in kwargs['extracmd']:
        extracmd += ['--output-spaces %s' % kwargs['outspace']]
    if bool(kwargs['cifti']) and '--cifti-output %s' not in kwargs['extracmd']:
        extracmd += ['--cifti-output %s' % kwargs['cifti']]
    
    if kwargs['nthreads']/2!=kwargs['maxnthreads'] and kwargs['nthreads']>1:
        print(f'Warning: It is highly recommended to set maxnthreads (%d) as half of nthreads (%d).' % ({kwargs['maxnthreads']}, {kwargs['nthreads']}))
    if kwargs['nthreads']>0 and '--nthreads' not in kwargs['extracmd']:
        extracmd += ['--nthreads %d' % kwargs['nthreads']]
    if kwargs['maxnthreads']>0 and '--omp-nthreads' not in kwargs['extracmd']:
        extracmd += ['--omp-nthreads %d' % kwargs['maxnthreads']]
        
    if not bool(kwargs['wd']):
        wd = os.path.join(os.path.dirname(bidsDir), os.path.basename(bidsDir)+'_work')
    else:
        wd = kwargs['wd']
    if not os.path.isdir(wd): os.mkdir(wd)
    extracmd += ['--work-dir %s' % wd]
    
    if bool(kwargs['ignore']) and '--ignore' not in kwargs['extracmd']:
        extracmd += ['--ignore %s' % kwargs['ignore']]
    if bool(kwargs['extracmd']):
        extracmd += [kwargs['extracmd']]
                
    ## Make the cmd for fmriprep
    fpcmd = '%sfmriprep-docker %s %s/derivatives/fmriprep/ participant --participant-label %s %s ' % (kwargs['pathtofmriprep'], bidsDir, bidsDir, subjCode, ' '.join(extracmd))
    
    ## Run cmd
    if kwargs['runcmd']:
        status = uti.runcmd(fpcmd)[1]
    else:
        status = None

    return fpcmd, status
