
import os
import pynisurf.freesurfer as fs
import pynisurf.bids as bids

            
class project:

    def __init__(self, fsdir, bidsdir='', fpdir ='', subjdir='', funcdir='', subjwc='sub-*', legacy=True):
        """Create a project and store the relevant information.

        Parameters
        ----------
        fsdir : str
            the FreeSurfer directory (where FreeSurfer is installed)
        bidsdir : str, optional
            directory to the BIDS directory, i.e., the direcotry stores the dcm2bids output. by default '' (will not set up this directory)
        fpdir : str, optional
            directory to the fMRIPrep output, by default '' (will not set up this directory)
        subjdir : str, optional
            directory to the SUBJECTS_DIR in FreeSurfer, by default '<bidsdir>/derivatives/freesurfer'
        funcdir : str, optional
            directory to the FUNCTIONALS_DIR in FreeSurfer, by default <bidsdir>/derivatives/functionals'
        subjwc : str, optional
            wildcard to identify subject list, by default 'sub-*'
        legacy : bool, optional
            whether the fMRIPrep output is in legacy format (more see https://fmriprep.org/en/stable/outputs.html#legacy-layout), by default True
        """

        fs.setup(fsdir) # setup FreeSurfer
        self.fsversion = fs.version(toprint=False)
        
        # set up BIDS
        self.legacy = legacy
        if bool(bidsdir) and os.path.isdir(bidsdir):
            self.setbidsdir(bidsdir, subjwc='sub-*')
            self.setfpdir(fpdir)
        
        # set up SUBJECTS_DIR and FUNCTIONALS_DIR
        if not bool(subjdir) and bool(bidsdir):
            tmpdir = '' if legacy else 'sourcedata'
            subjdir = os.path.join(bidsdir, 'derivatives', tmpdir, 'freesurfer')
        if os.path.isdir(subjdir):
            self.setsubjdir(subjdir, subjwc)
        # self.subjdir, self.subjlist = fs.subjdir(subjdir, subjwc)
        
        # (to be updated later)
        if bool(funcdir):
            funcdir = os.path.join(self.bidsdir, 'derivatives', 'functionals')
        if os.path.isdir(funcdir):
            self.setfuncdir(funcdir, subjwc)
        # self.funcdir, self.funclist = fs.funcdir(funcdir, subjwc)
        
    def setbidsdir(self, bidsdir, subjwc='sub-*'):
        """Set BIDS directory and update the subject list.

        Parameters
        ----------
        bidsdir : str
            directory to the BIDS directory, i.e., the direcotry stores the dcm2bids output. by default '' (will not set up this directory)
        subjwc : str, optional
            wildcard to identify subject list, by default 'sub-*'
        """
        self.bidsdir, self.bidslist = bids.bidsdir(bidsdir, subjwc)
        self.sourcedata = os.path.join(self.bidsdir, 'sourcedata')
            
    def setsubjdir(self, subjdir, subjwc='sub-*'):
        """Set SUBJECTS_DIR and update the subject list.

        Parameters
        ----------
        subjdir : str
            directory to the SUBJECTS_DIR in FreeSurfer.
        subjwc : str, optional
            wildcard to identify subject list, by default 'sub-*'
        """
        self.subjdir, self.subjlist = fs.subjdir(subjdir, subjwc)
    
    def setfuncdir(self, funcdir, subjwc='sub-*'):
        """Set FUNCTIONALS_DIR and update the subject list.

        Parameters
        ----------
        funcdir : str
            directory to the FUNCTIONALS_DIR in FreeSurfer.
        subjwc : str, optional
            wildcard to identify subject list, by default 'sub-*'
        """
        self.funcdir, self.funclist = fs.funcdir(funcdir, subjwc)
        
    def setfpdir(self, fpdir=''):
        """Set the directory to the fMRIPrep output.

        Parameters
        ----------
        fpdir : str, optional
            directory to the fMRIPrep output, by default '' (will not set up this directory)
        """
        if bool(fpdir):
            self.fpidr = fpdir
        elif not bool(self.bidsdir):
            self.fpdir = os.path.join(self.bidsdir, 'derivatives', 'fmriprep')
        
  