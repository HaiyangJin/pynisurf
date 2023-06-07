import os

import pynisurf.freesurfer as fs
import pynisurf.bids as bids

            
class project:
    '''
    Create a project and store the relevant information.
    '''
   
    def __init__(self, fsdir, bidsdir='', subjdir='', funcdir='', subjwc='sub-*', legacy=True):
        
        # for legacy format, see https://fmriprep.org/en/stable/outputs.html#legacy-layout
        
        fs.setup(fsdir) # setup FreeSurfer
        self.fsversion = fs.version(toprint=False)
        
        # set up BIDS
        self.legacy = legacy
        if bool(bidsdir) and os.path.isdir(bidsdir):
            self.updatebidsdir(bidsdir, subjwc='sub-*')
        
        # set up SUBJECTS_DIR and FUNCTIONALS_DIR
        if not bool(subjdir) and bool(bidsdir):
            tmpdir = '' if legacy else 'sourcedata'
            subjdir = os.path.join(bidsdir, 'derivatives', tmpdir, 'freesurfer')
        if os.path.isdir(subjdir):
            self.updatesubjdir(subjdir, subjwc)
        # self.subjdir, self.subjlist = fs.subjdir(subjdir, subjwc)
        
        # (to be updated later)
        if bool(funcdir):
            funcdir = os.path.join(self.bidsdir, 'derivatives', 'functionals')
        if os.path.isdir(funcdir):
            self.updatefuncdir(funcdir, subjwc)
        # self.funcdir, self.funclist = fs.funcdir(funcdir, subjwc)
        
    def setbidsdir(self, bidsdir, subjwc='sub-*'):
        self.bidsdir, self.bidslist = bids.bidsdir(bidsdir, subjwc)
        self.sourcedata = os.path.join(self.bidsdir, 'sourcedata')
            
    def setsubjdir(self, subjdir, subjwc='sub-*'):
        self.subjdir, self.subjlist = fs.subjdir(subjdir, subjwc)
    
    def setfuncdir(self, funcdir, subjwc='sub-*'):
        self.funcdir, self.funclist = fs.funcdir(funcdir, subjwc)
        
    def setfpdir(self, fpdir=''):
        if bool(fpdir):
            self.fpidr = fpdir
        elif not bool(self.bidsdir):
            self.fpdir = os.path.join(self.bidsdir, 'derivatives', 'fmriprep')
        
    
        
        
  