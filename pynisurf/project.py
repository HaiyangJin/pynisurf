import os

import pynisurf.freesurfer as fs
import pynisurf.bids as bids

            
class project:
    '''
    Create a project and store the relevant information.
    '''
   
    def __init__(self, fsdir='', bidsdir='', subjdir='', funcdir='', str_pattern='sub-*'):
        
        fs.setup(fsdir) # setup FreeSurfer
        self.fsversion = fs.version('', False)
        
        # set up BIDS
        self.bidsdir, self.bidslist = bids.bidsdir(bidsdir, str_pattern)
        self.sourcedata = os.path.join(self.bidsdir, 'sourcedata')
        
        # set up SUBJECTS_DIR & FUNCTIONALS_DIR
        if not bool(subjdir):
            subjdir = os.path.join(self.bidsdir, 'derivatives', 'subjects')
        if os.path.isdir(subjdir):
            self.updatesubjdir(subjdir, str_pattern)
        # self.subjdir, self.subjlist = fs.subjdir(subjdir, str_pattern)
            
        if not bool(funcdir):
            funcdir = os.path.join(self.bidsdir, 'derivatives', 'functionals')
        if os.path.isdir(funcdir):
            self.updatefuncdir(funcdir, str_pattern)
        # self.funcdir, self.funclist = fs.funcdir(funcdir, str_pattern)
    
    def updatesubjdir(self, subjdir, str_pattern='sub-*'):
        self.subjdir, self.subjlist = fs.subjdir(subjdir, str_pattern)
    
    def updatefuncdir(self, funcdir, str_pattern='sub-*'):
        self.funcdir, self.funclist = fs.funcdir(funcdir, str_pattern)
    
        
        
  