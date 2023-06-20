
import os
import pynisurf.freesurfer as fs
import pynisurf.bids as bids

            
class project:

    def __init__(self, fs_dir, bids_dir=None, subj_wc='sub-*', isfped=False, legacy=True):
        """Create a project: set up FreeSurfer and make some global environment variables (e.g., `$BIDS_DIR`, `$SUBJECTS_DIR`).

        Parameters
        ----------
        fs_dir : str
            FreeSurfer directory (where FreeSurfer is installed)
        bids_dir : str, optional
            directory to the BIDS directory, i.e., the direcotry stores the dcm2bids output. by default None (will not set up this directory)
        subj_wc : str, optional
            wildcard to identify subject list, by default 'sub-*'
        isfped : bool, optional
            whether fmriPrep has been conducted. Default to False.
        legacy : bool, optional
            whether the fMRIPrep output is in legacy format (more see https://fmriprep.org/en/stable/outputs.html#legacy-layout), by default True
        """

        fs.setup(fs_dir) # setup FreeSurfer
        self.fsversion = fs.version(toprint=False)
        
        # set up BIDS
        self.legacy = legacy
        self.setbidsdir(bids_dir, subj_wc='sub-*')
        self.setfpdir(bids_dir, subj_wc, set_dir=isfped, legacy=legacy)
        
        # set up SUBJECTS_DIR if needed 
        tmpdir = '' if legacy else 'sourcedata'
        subj_dir = os.path.join(bids_dir, 'derivatives', tmpdir, 'freesurfer')
        self.setsubjdir(subj_dir, subj_wc)
        
        # set up FUNCTIONALS_DIR if needed
        func_dir = os.path.join(self.bidsdir, 'derivatives', 'functionals')
        self.setfuncdir(func_dir, subj_wc)

        
    def setbidsdir(self, bids_dir, subj_wc='sub-*'):
        """Set BIDS directory and update the subject list.

        Parameters
        ----------
        bids_dir : str
            directory to the BIDS directory, i.e., the direcotry stores the dcm2bids output. by default None (will not set up this directory)
        subj_wc : str, optional
            wildcard to identify subject list, by default 'sub-*'
        """
        if os.path.isdir(bids_dir):
            self.bidsdir, self.bidslist = bids.bidsdir(bids_dir, subj_wc, setdir=True)

            
    def setsubjdir(self, subj_dir, subj_wc='sub-*'):
        """Set SUBJECTS_DIR and update the subject list.

        Parameters
        ----------
        subj_dir : str
            directory to the SUBJECTS_DIR in FreeSurfer.
        subj_wc : str, optional
            wildcard to identify subject list, by default 'sub-*'
        """
        if os.path.isdir(subj_dir):
            self.subjdir, self.subjlist = fs.subjdir(subj_dir, subj_wc)
    
    
    def setfuncdir(self, func_dir, subj_wc='sub-*'):
        """Set FUNCTIONALS_DIR and update the subject list.

        Parameters
        ----------
        func_dir : str
            directory to the FUNCTIONALS_DIR in FreeSurfer.
        subj_wc : str, optional
            wildcard to identify subject list, by default 'sub-*'
        """
        if os.path.isdir(func_dir):
            self.funcdir, self.funclist = fs.funcdir(func_dir, subj_wc)
        
    def setfpdir(self, fp_dir, subj_wc='sub-*', set_dir=True, legacy=True):
        """Set the directory to the fMRIPrep output.

        Parameters
        ----------
        fp_dir : str, optional
            directory to the fMRIPrep output, by default None (will not set up this directory)
        subj_wc : str, optional
            wildcard to identify subject list, by default 'sub-*'
        set_dir : bool, optional
            whether to set up the directory, by default True
        legacy : bool, optional
        """
        if os.path.isdir(fp_dir):
            self.fpdir, self.fplist = bids.fpdir(fp_dir, subj_wc, set_dir=set_dir, legacy=legacy)
  