# -*- coding: utf-8 -*-

class freesurfer:
  '''
  Some custome codes for performing analysis in FreeSurfer.
  '''
  
      
  def __init__(self, fshome=''):
    
    import os
    import sys
    
    # set up FreeSurfer
    if not os.getenv('FREESURFER_HOME', 'Not set') == 'Not set':
      print('FreeSurfer was already set up.')
    else:
      # obtain fshome if it is not set
      if fshome == '':
        if sys.platform == 'linux':
          fshome = '/usr/local/freesurfer'
        elif sys.platform == 'darwin':
          fshome = '/Applications/freesurfer'
        else:
          print('Platform not supported.')
      elif not fshome[0] == os.path.sep:    
      # [Please ignore this part; some shortcuts for setting up]
        fshome = '/Applications/freesurfer/%s' % fshome
      
      # set up FreeSurfer
      os.environ['FREESURFER_HOME'] = fshome
      os.environ['SUBJECTS_DIR'] = os.path.join(fshome, 'subjects')
      os.system('source ' + fshome + os.path.sep + 'FreeSurferEnv.sh')
      
      # add PATH and other environment variables
      
    self.version = 'v0.00000001'
    self.fshome = os.getenv('FREESURFER_HOME')
    self.subjdir = os.getenv('SUBJECTS_DIR')
    
     
  # set $SUBJECTS_DIR 
  def subjdir(self, subjdir='', str_pattern='', setdir=1):
    '''
    
    Parameters
    ----------
    subjdir : <string> ['']
      the full path of the $SUBJECTS_DIR in FreeSurfer.
    str_pattern : <string> ['']
      string pattern to identify subject folders.
    setdir : <boolean> [1]
      1 [default]: setenv $SUBJECTS_DIR; 0: do not set.

    Returns
    -------
    None.

    '''
    import os
    
    if subjdir == '':
      # get 'SUBJECTS_DIR' from FreeSurfer
      subjdir = os.getenv('SUBJECTS_DIR', 'Not set')
      setdir = 0
    elif not os.path.isdir(subjdir):
      raise Exception("subjdir does not exist.")
    
    if setdir:
      os.environ['SUBJECTS_DIR'] = subjdir
      print('SUBJECTS_DIR is set as {} now...', {subjdir})
      
    # gather subject code list
    subj_list = os.listdir(os.path.join(subjdir, str_pattern))
            
    self.subjdir = subjdir   # $SUBJECTS_DIR
    self.subjlist = subj_list  # a list of subject codes
    
    return subjdir, subj_list
        
        
  def funcdir(self, funcdir, str_pattern='', setdir=1):
  
    import os
     
    if funcdir == '':
      # get '$FUNCTIONALS_DIR' from FreeSurfer
      funcdir = os.getenv('FUNCTIONALS_DIR', 'Not set')
      setdir = 0
    elif not os.path.isdir(funcdir):
      raise Exception("funcdir does not exist.")
    
    if setdir:
      os.environ['FUNCTIONALS_DIR'] = funcdir
      print('FUNCTIONALS_DIR is set as {} now...', {funcdir})
    
    # gather subject code list
    sess_list = os.listdir(os.path.join(funcdir, str_pattern))
    
    self.funcdir = funcdir
    self.sesslist = sess_list
    
    return funcdir, sess_list
    





