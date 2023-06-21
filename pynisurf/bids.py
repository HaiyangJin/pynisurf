"""
Tools for BIDS structure.
Created by Haiyang Jin (https://haiyangjin.github.io/en/about/)
"""

import os, re, glob, shutil
import json
from itertools import chain

import pynisurf.utilities as util

def bidsdir(bids_dir=None, subj_wc='sub-*', set_dir=True):
    """Set `bids_dir` as a global environment "BIDS_DIR". `bids_dir`'s sub-directory should be the BIDS folder, which saves 'sourcedata', 'derivatives', 'sub-x', etc (or some of them).

    Parameters
    ----------
    bids_dir : str, optional
        full path to the BIDS direcotry, by default None
    subj_wc : str, optional
        wildcard to be used to identify subject list, by default 'sub-*'
    set_dir : bool, optional
        set the global environment $BIDS_DIR, by default True

    Returns
    -------
    str
        full path to the BIDS direcotry
    str list
        a list of subject folders in `bids_dir`.
    """
    
    if not bool(bids_dir):
        bids_dir = os.getenv('BIDS_DIR')
        
    # set the environment variable of BIDS_DIR
    if set_dir:
        os.environ['BIDS_DIR'] = bids_dir
        print(f'\n$BIDS_DIR is set as {bids_dir} now...')
    
    # obtain the session codes
    subj_list = [f for f in os.listdir(bids_dir) if re.match(subj_wc, f) and '.' not in f]

    return bids_dir, subj_list
    
    
def dcm2bids(dcm_subj, bids_subj=None, config=None, is_ses=False, run_cmd=True):
    """Convert DICOM to BIDS with dcm2bids.

    Parameters
    ----------
    dcm_subj : str, str list
        A list of subject codes/folders storing DICOM files (if `dcm_subj` is str list); OR a wildcard string to match the subject folders storing DICOM files (if `dcm_subj` is str).
    bids_subj : str, optional
        A list of output BIDS subject codes (e.g., {'X01', 'X02', ...}). It needs to have the same length as `dcm_subj`. Default is {'01', '02', ...} depending on `dcm_subj`. It only makes sense to input a list of string when `dcm_subj` is also a str list. Each string in `dcm_subj` correspond to each string in `bids_subj`. [OR] strings to be put before {'01', '02, ...}.E.g., when `bids_subj` is 'Test', the subjcode will be 'sub-Test01', 'sub-Test02'. Defaults to None.
    config : str, optional
        the config file to deal with dicoms. Defaults to '{$BIDS_DIR}/code/bids_convert.json'.
    is_ses : bool, optional
        If there are multiple subdir within dcm_subj dir, whether these dirctories are sessions (or runs). Default is False (i.e., runs). Note that if run folders are mistaken as session folders, each run will be saved as a separate session. No messages will be displayed for this case but you will notice it in the output. A special usage of `is_ses` is: when `is_ses` is not 0 and there is only one folder within the directory, `is_ses` will be used as the session code.
    run_cmd : bool, optional
        whether to run the commands. Defaults to True.

    Returns
    -------
    cmdlist : str list
        dcm2bids commands.
    status : boo vec
        status of running d2bcmd. True if no error.
    """
    
    ## Deal with inputs
    bids_dir = bidsdir(set_dir=False)[0]
    
    if not bool(config):
        config=os.path.join(bids_dir, 'code', 'bids_convert.json')
    # make sure the config file exist
    assert os.path.isfile(config), (f'Cannot find the config file:\n%s', config)
    
    dcmdir = os.path.join(bids_dir, 'sourcedata')
    assert os.path.isdir(dcmdir), (f'Cannot find sourcedata/ in %s', bids_dir)
    
    # input subj list
    if isinstance(dcm_subj, str):
        # treat dcm_subj as wildcard
        dsubj_list = [f for f in os.listdir(dcmdir) if re.match(dcm_subj, f) and '.' not in f]
    elif isinstance(dcm_subj, list):
        dsubj_list = dcm_subj
        
    # output BIDS subj list
    if isinstance(bids_subj, str):
        bids_subj = ['%s%02d' % (bids_subj,idx+1) for idx in range(len(dsubj_list))]
    assert len(dsubj_list)==len(bids_subj), (f'The length of "dcm_subj" (%d) and "bids_subj" (%d) is not the same.', len(dsubj_list), len(bids_subj))
    
    ## Make the cmd for dcm2bids
    cmdlist = [None] * len(bids_subj)
    
    for iSubj in range(len(bids_subj)):
        
        # add full path if needed
        thisdabs = os.path.join(dcmdir, dsubj_list[iSubj])
        dcm_ses = [d for d in os.listdir(thisdabs) if os.path.isdir(os.path.join(thisdabs,d))]
                    
        if not bool(dcm_ses):
            # if no sub-dir is found in dcmDir, there is only 1 session
            cmd = 'dcm2bids -d %s -o %s -p %s -c %s --forceDcm2niix --clobber' % (util.cmdpath(thisdabs), util.cmdpath(bids_dir), bids_subj[iSubj], config)
            
        elif not is_ses:
            # if the sub-dir in dsubjDir are runs (instead of sessions)
            runfolders = [os.path.join(thisdabs, run) for run in dcm_ses]
            cmd = 'dcm2bids -d %s -o %s -p %s -c %s --forceDcm2niix --clobber' % (' '.join(runfolders), util.cmdpath(bids_dir), bids_subj[iSubj], config)
            
        elif is_ses:
            # each sub-dir is one session
            dcmid = range(len(dcm_ses))
            sessid = range(1, len(dcm_ses)+1)
            if len(dcmid)==1: sessid = [is_ses] # customize the session number

            # if the subdir in dsubjDir are sessions
            cmd = ['dcm2bids -d %s -o %s -p %s -s %d -c %s --forceDcm2niix --clobber' % (util.cmdpath(os.path.join(thisdabs, dcm_ses[dcmid[x]])), util.cmdpath(bids_dir), bids_subj[iSubj], sessid[x], config) for x in dcmid]
                        
        cmdlist[iSubj] = cmd
    # flatten the nested list to a list
    cmdlist = list(chain(*cmdlist))
           
    ## Run cmd
    cmdlist, status = util.runcmd(cmdlist, run_cmd)
    
    return (cmdlist, status)


def fn2info(filename, sec_sep='_', value_sep='-', 
            modality=['bold', 'sbref', 'epi', 'T1w', 'T2w', 
            'scans', 'events',
            'inflated', 'midthickness', 'pial', 'smoothwm', 'probseg', 
            'timeseries', 'xfm', 'boldref', 'dseg', 'mask']):
    """Collects the relevant information from the filename by section (<secstr>) and value (<valuestr>) strings.

    Parameters
    ----------
    filename : str
        the file name to be parsed.
    sec_sep : str, optional
        the string to be used to separate the filename into different sections. Defaults to '_'.
    value_sep : str, optional
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
    sec = fname[:idx].split(sec_sep)
    
    # deal with values without fieldname
    no_fieldname = [value_sep not in each for each in sec]
    backup_fields = ['custom%d' % (x+1) for x in range(len(no_fieldname))]
    # the last is modality (if applicable)
    if no_fieldname[-1]==True & (sec[-1] in modality):
        backup_fields[-1] = 'modality'
        
    # update/add fieldname
    for i, v in enumerate(no_fieldname):
        if v:
            sec[i] = backup_fields[i]+value_sep+sec[i]

    # identify all (the first) {value_sep}
    info = {}
    for isec in sec:
        idx = re.search(value_sep, isec)
        info[isec[:idx.start()]] = isec[idx.start()+1:]
    info['ext'] = ext

    return info
    

def info2fn(info, sec_sep='_', value_sep='-'):
    """Converts info_struct (can be obtained via `fn2info()`) into a filename (str).

    Parameters
    ----------
    info : dict
        the information in a dict. See the output of `fn2info()`.
    sec_sep : str, optional
        the string to be used to separate the filename into different sections. Defaults to '_'.
    value_sep : str, optional
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
            sec.append(k+value_sep+v)
    
    # join all sections and add extension
    return sec_sep.join(sec)+ext


def listfile(file_wc='*', subj_list='sub-*', modality='func', isfmriprep=True):
    """Collect the file list for a given modality.

    Parameters
    ----------
    file_wc : str, optional
        filename wild card to be used to identify files. Defaults to '*', i.e., all files.
    subj_list : str OR str list, optional
        <list str> a list of subject folders in `bids_dir`. OR <str> wildcard strings to match the subject folders via `bids_dir()`. Defaults to 'sub-*'.
    modality : str, optional
        the moduality folders ('func', 'anat', 'fmap', ...). Defaults to 'func'.
    isfmriprep: bool, optional
        whether to list the files in the fmriprep output folder. Defaults to True. When false, the files in the BIDS folder will be listed.

    Returns
    -------
    list
        a list of identified files.
    """    
    
    if isinstance(subj_list, str): 
        if isfmriprep:
            base_dir, subj_list = fpdir(subj_wc = subj_list, set_dir=False)
        else:
            base_dir, subj_list = bidsdir(subj_wc = subj_list, set_dir=False)
    else:
        if isfmriprep:
            base_dir = fpdir(set_dir=False)[0]
        else:
            base_dir = bidsdir(set_dir=False)[0]
    
    # list the matched files
    filelist = []
    for the_subj in subj_list:
        the_subj_dir = os.listdir(os.path.join(base_dir, the_subj))
        
        if modality in the_subj_dir:
            # there are no session folders
            thefile = glob.glob(os.path.join(base_dir, the_subj, modality, file_wc))
        else:
            # there are multiple session folders
            thefile = [glob.glob(os.path.join(base_dir, the_subj, session, modality, file_wc)) for session in the_subj_dir]
            thefile = list(chain(*thefile)) # flatten the nested list to a list
        filelist.append(thefile)
        
    return list(chain(*filelist)) # flatten the nested list to a list
    
   
def fixfmap(intend_list='*_bold.nii.gz', subj_list='sub-*', fmap_wc='*.json'):
    """Fix the IntendedFor field in fmap json files. (Probably not useful anymore. It seems that this issue has been fixed in dcm2bids)

    Parameters
    ----------
    intend_list : str OR str list, optional
        <list str> a list of files to be assigned to "intendedFor" of fmap json files. OR <str> wildcard strings to identify the files to be assigned to "intendedFor" of fmap json files. Defaults to '*_bold.nii.gz'.
    subj_list : str, optional
        <list str> a list of subject folders in `bids_dir`. OR <str> wildcard strings to match the subject folders via `bids_dir()`. Defaults to 'sub-*'.
    fmap_wc : str, optional
        wildcard for the fmap json files, for which the intend_list will be added to. Defaults to '*.json', i.e., all json files in fmap/ will be updated.

    Raises
    ------
    Exception
        sanity check for session information. Data in the same folder should be from the same session.
    """   
     
    # make sure fmap_wc ends with '.json'
    if not fmap_wc.endswith('.json'): fmap_wc = fmap_wc + '.json'
    
    # get all fmap files
    fmapjosns = listfile(fmap_wc, subj_list, 'fmap', isfmriprep=False)
        
    ## Fix fmap files
    for ifmap in fmapjosns:
        
        if isinstance(intend_list, list):
            # use the list as allintend directly
            allintend = intend_list
        else:
            # identify all BOLD runs in func/
            intendfiles = glob.glob(os.path.join(os.path.dirname(ifmap), '..', 'func', intend_list))
            
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


def fixfunc(task_name, subj_list='sub-*', task_wc='*.json'):
    """Fix the TaskName field in func json files.

    Parameters
    ----------
    task_name : str
        task name to be added to the files identified by `task_name`.
    subj_list : str, optional
        `list str` a list of subject folders in `bids_dir`. OR `str` wildcard strings to match the subject folders via `bids_dir()`. Defaults to 'sub-*'.
    task_wc : str, optional
        wildcard strings to identify a list of func runs, for which `TaskName` will be added to their json files. Defaults to '*.json' and then all func files are treated as one task. The name will be `task_name`.
    """    
    
    # make sure task_wc ends with '.json'
    if not task_wc.endswith('.json'): task_wc = task_wc + '.json'
    
    # get all func josn files
    funcjosns = listfile(task_wc, subj_list, 'func', isfmriprep=False)
    
    # add task name
    for ifunc in funcjosns:
        # read the json file
        with open(ifunc) as json_in:
            val = json.load(json_in)
        # add TaskName
        val['TaskName'] = task_name
        # save the json file
        with open(ifunc, "w") as json_out:
            json.dump(val, json_out, indent=4)
    
     
def cpevent(subj_code, event_wc=None, run_wc='*_bold.nii.gz', ses=None):  
    """Copy event files to the BIDS folder.

    Parameters
    ----------
    subj_code : str
        subject code in `bids_dir`.
    event_wc : str, optional
        wildcard strings to be used to identify the event files to be copied. Defaults to None.
    run_wc : str, optional
        wildcard strings to be used to identify the functional runs (BOLD), whose names will be used as the new names for the event files. Defaults to '*_bold.nii.gz'.
    ses : str, optional
        the session name. Default to None, i.e., no session informaiton/folder is available.

    Returns
    -------
    str list
        a list of srouce files.
    str list
         a list of destination files.
    """
    
    ## Deal with inputs
    bids_dir, subj_list = bidsdir(set_dir=False)
    assert subj_code in subj_list, (f'Cannot find {subj_code} in {bids_dir}.')  
    
    # wildcard for the event files and runs
    if isinstance(event_wc, str): event_wc = [event_wc]
    if isinstance(run_wc, str): run_wc = [run_wc]
    nwd = len(event_wc)
    assert nwd==len(run_wc), (f'The length of "event_wc" (%d) and "run_wc" (%d) is not the same.', nwd, len(run_wc))
        
    # set session info
    if isinstance(ses, int): ses = str(ses)
    if isinstance(ses, str) & (not ses.startswith('ses-')): ses = 'ses-'+ses

    # Find and copy files
    srclist = []
    dstlist = []
    for iwd in range(nwd):
        
        # source files
        src = sorted(glob.glob(event_wc[iwd]))
        assert bool(src), (f'Cannot find %s in pwd.') % (event_wc[iwd])
        
        # destination files
        runs = sorted(glob.glob(os.path.join(bids_dir, subj_code, ses, 'func', run_wc[iwd])))
        assert bool(runs), (f'Cannot find %s in %s.') % (run_wc[iwd], os.path.join(bids_dir, subj_code, ses, 'func'))
        dst = [r.replace('_bold.nii.gz', '_events.tsv') for r in runs]
        
        # copy files
        [shutil.copyfile(src[i], dst[i]) for i in range(len(src))]
        
        # save src and dst lists
        srclist+=src
        dstlist+=dst
    
    return srclist, dstlist


def dupsbref(subj_code, sbref_wc='*sbref.nii.gz', bold_wc='*_bold.nii.gz'):
    """Duplicate the single-band reference for each of the matched bold runs.

    Parameters
    ----------
    subj_code : str list, str
        a list of subject folders in `bids_dir`. OR <str> wildcard strings to match the subject folders via `bids_dir()`. 
    sbref_wc : str, optional
        wildcard strings to identify the single-band reference files.
    bold_wc : str, optional
        wildcard strings to identify the functional runs (BOLD).
    rmsrc : bool, optional
        whether to remove the original sbref files. Defaults to False.
    """
    
    # find all sb refs for this subject
    sbrefs = listfile(sbref_wc, subj_code, 'func', isfmriprep=False)
    
    # duplicate the sbref for each bold run
    for sbref in sbrefs:
        # find the bold runs
        bold = glob.glob(os.path.join(os.path.dirname(sbref), bold_wc))
        assert bool(bold), (f'Cannot find any BOLD files (%s) matching the single-band reference (%s).') % (bold_wc, sbref)
        
        # repeat the sbref for each bold run
        [shutil.copyfile(sbref, b.replace('_bold.nii.gz', '_sbref.nii.gz')) for b in bold]
    

def mkignore(ignore_list=['tmp_dcm2bids/','tmp/','code/']):
    """Make .bidsignore file in the BIDS folder.

    Parameters
    ----------
    ignore_list : list, optional
        directories or files to be ignored, by default ['tmp_dcm2bids/','tmp/','code/']
    """    
    
    # get bids dir
    bids_dir=bidsdir(set_dir=False)[0]
    # make .gitignore
    util.mkfile(ignore_list, os.path.join(bids_dir, '.bidsignore'))
    
    
def mktsv(content='sub-*', fname='participants.tsv', header='participant_id'):
    """Make participants.tsv file in the BIDS folder.

    Parameters
    ----------
    content : str, optional
        <list str> a list of subject folders in `bids_dir`. OR <str> wildcard strings to match the subject folders via `bids_dir()`. Defaults to 'sub-*'.
    fname : str, optional
        the name of the tsv file. Defaults to 'participants.tsv'.
    header : str, optional
        the header of the tsv file. Defaults to 'participant_id'.
    """
        
    # get bids dir
    bids_dir=bidsdir(set_dir=False)[0]
    # get list of subjects if content is a string
    if isinstance(content, str):
        content = bidsdir(subj_wc=content, set_dir=False)[1]
    # make sure fname ends with '.tsv'
    if not fname.endswith('.tsv'): fname = fname + '.tsv'
    
    # make participant tsv file
    content.insert(0, header)
    util.mkfile(content, os.path.join(bids_dir, fname))
    

def mkreadme():
    """Make README.md file in the BIDS folder.
    """
    
    # get bids dir
    bids_dir=bidsdir(set_dir=False)[0]
    # copy README.md
    shutil.copyfile(os.path.join(os.path.dirname(__file__), 'resources', 'README.md'), os.path.join(bids_dir, 'README.md'))
    
    
def scaffold(force=False):
    """Make .bidsignore, participants.tsv, and README.md files in the BIDS folder.

    Parameters
    ----------
    force : bool, optional
        whether to overwrite the existing files. Defaults to False.
    """
    
    # get bids dir
    bids_dir=bidsdir(set_dir=False)[0]
    
    if not os.path.isfile(os.path.join(bids_dir, '.bidsignore')) or force:
        mkignore()
    if not os.path.isfile(os.path.join(bids_dir, 'participants.tsv')) or force:
        mktsv()
    if not os.path.isfile(os.path.join(bids_dir, 'README.md')) or force:
        mkreadme()
    
    
def validator(run_cmd=True):
    """Run bids_validator. This function needs Docker.

    Parameters
    ----------
    run_cmd : bool, optional
        whether to run the command, by default True

    Returns
    -------
    int
        status of running the command. 0 if no error.
    """
    
    # get bids dir
    bids_dir=bidsdir(set_dir=False)[0]
    # make the command for bids_validator
    cmd = 'docker run --rm -v %s:/data:ro bids/validator /data' % bids_dir
    # run the command
    return util.runcmd(cmd, run_cmd=run_cmd)[1]
    
        
def fmriprep(subj_code, **kwargs):
    """Run fmriprep for one subject. This function needs Docker.

    Parameters
    ----------
    subj_code : str
        subject code in `bids_dir`.
        
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
        working dicrectory. Defaults to a folder ending with '_work' at the same level with `bids_dir`. For example, if `bids_dir` is `path/to/bids`, the default `wd` will be `path/to/bids_work`.
    ignore : str, optional
        steps to be ignored in fmriprep, e.g., {fieldmaps,slicetiming,sbref}. Defaults to ''.
    run_cmd : bool, optional
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
                     'run_cmd': True,
                     'extracmd':'--no-tty', # not use TTY --use-aroma --ignore slicetiming 
                     'pathtofmriprep':''}
    kwargs = {**defaultKwargs, **kwargs}
    
    bids_dir, subj_list=bidsdir(set_dir=False)

    if not subj_code.startswith('sub-'): subj_code = 'sub-'+subj_code
    assert subj_code in subj_list, (f'Cannot find {subj_code} in {bids_dir}.')
    
    ## Deal with kwargs
    extracmd = []
    if bool(kwargs['fslicense']) and '--fs-license-file' not in kwargs['extracmd']:
        extracmd += ['--fs-license-file %s --fs-subjects-dir %s/derivatives/freesurfer/' % (kwargs['fslicense'], bids_dir)]
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
        wd = os.path.join(os.path.dirname(bids_dir), os.path.basename(bids_dir)+'_work')
    else:
        wd = kwargs['wd']
    if not os.path.isdir(wd): os.mkdir(wd)
    extracmd += ['--work-dir %s' % wd]
    
    if bool(kwargs['ignore']) and '--ignore' not in kwargs['extracmd']:
        extracmd += ['--ignore %s' % kwargs['ignore']]
    if bool(kwargs['extracmd']):
        extracmd += [kwargs['extracmd']]
                
    ## Make the cmd for fmriprep
    fpcmd = '%sfmriprep-docker %s %s/derivatives/fmriprep/ participant --participant-label %s %s ' % (kwargs['pathtofmriprep'], bids_dir, bids_dir, subj_code, ' '.join(extracmd))
    
    ## Run cmd
    if kwargs['run_cmd']:
        status = util.runcmd(fpcmd)[1]
    else:
        status = None

    return fpcmd, status


def fpdir(fp_dir=None, subj_wc='sub-*', set_dir=True, legacy=True):
    """Set up the $FMRIPREP_DIR environment variable and return the full path to the $FMRIPREP_DIR and a list of subject folders in `bids_dir`.

    Parameters
    ----------
    fp_dir : str, optional
        full path to the $FMRIPREP_DIR. Defaults to None and it will obtain the $FMRIPREP_DIR as `fp_dir`. If `fp_dir` is the same as `bids_dir()` (i.e., the BIDS folder), the $FMRIPREP_DIR will be set as '`bids_dir()`/derivatives/fmriprep' (or '`bids_dir()`/derivatives`' if `legacy` is False). 
    subj_wc : str, optional
        wildcard strings to match the subject folders in `fp_dir`. Defaults to 'sub-*'.
    set_dir : bool, optional
        whether to set the environment variable of $FMRIPREP_DIR. Defaults to True.
    legacy : bool, optional
        whether to use the legacy fmriprep output folder (i.e., `bids_dir()`/derivatives/fmriprep) or the new fmriprep output folder (i.e., `bids_dir()`/derivatives). Defaults to True.
        
    Returns
    -------
    str
        the full path to the $FMRIPREP_DIR.
    str list
        a list of subject folders in `fp_dir`.
    """
    
    if not bool(fp_dir):
        fp_dir = os.getenv('FMRIPREP_DIR')
    elif fp_dir == bidsdir(set_dir=False)[0]:
        tmpdir = 'fmriprep' if legacy else ''
        fp_dir = os.path.join(bidsdir(set_dir=False)[0], 'derivatives', tmpdir)
        
    # set the environment variable of FMRIPREP_DIR
    if set_dir:
        os.environ['FMRIPREP_DIR'] = fp_dir
        print(f'\n$FMRIPREP_DIR is set as {fp_dir} now...')
    
    # obtain the session codes
    if os.path.isdir(fp_dir):
        subj_list = [f for f in os.listdir(fp_dir) if re.match(subj_wc, f) and '.' not in f]
    else:
        subj_list = []

    return fp_dir, subj_list
    