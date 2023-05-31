'''
General utilities.
'''

import subprocess, os

def cmdpath(cmdlist, **kwargs):
    """Convert directory/path to BASH compatible (e.g., convert ' ' to '\ ').

    Args:
        cmdlist (str list OR str): A list of or one cmd.
        kwargs: key and value pairs to be used to replace strings. Specifically, the key (in kwargs) is the strings to be replaced and the value (in kwargs) is the strings to be replaced with (see example below).

    Returns:
        cmdlist (str list OR str): cmd after updating.
        
    Examples:
        cmdpath('test ', e='magic') # output is 'tmagicst\\ '
    """
    
    defaultKwargs = {' ':'\ ',
                     '(':'\(',
                     ')':'\)',
                     '~':'$HOME'}
    kwargs = {**defaultKwargs, **kwargs}
    
    asstr = False
    if isinstance(cmdlist, str):
        cmdlist = [cmdlist]
        asstr = True
    
    # replace the pairs
    for (k,v) in kwargs.items():
        cmdlist = [cmd.replace(k,v) for cmd in cmdlist]
        
    if asstr:
        cmdlist = cmdlist[0]
        
    return cmdlist   
    
    
def runcmd(cmdlist, runcmd=1):
    """Run BASH command and record the status.

    Args:
        cmdlist (str list OR str): A list of or one cmd.
        runcmd (int, optional): Whether to run the commnad. Defaults to 1.

    Returns:
        cmdlist (str list OR str): A list of or one cmd.
        status (int): the status of running command (None means the commands were not run). 
    """
    
    if isinstance(cmdlist, str):
        cmdlist = [cmdlist]
        
    if runcmd:
        # run the command
        status = [subprocess.Popen(cmd, shell=True).wait() for cmd in cmdlist]
    else:
        status = None * len(cmdlist)
        
    return cmdlist, status


def listdirabs(path):
    """List all files in a directory with absolute path.

    Args:
        path (str): path to the directory.

    Returns:
        list: a list of files in the directory.
        
    Created on 2023-May-30 by Haiyang Jin (https://haiyangjin.github.io/en/about/)
    """
    return [os.path.join(path, f) for f in os.listdir(path)]


def mkfile(content=[], fname='tmp'):
    """Make a file with content.

    Args:
        content (list, optional): content of the file. Defaults to [].
        fname (str, optional): file name. Defaults to 'tmp'. 
    """
    
    # make sure content is a list
    if isinstance(content, str):
        content = [content]
    
    # write to file
    with open(fname, 'w') as f:
        for line in content:
            f.write(line+'\n')
