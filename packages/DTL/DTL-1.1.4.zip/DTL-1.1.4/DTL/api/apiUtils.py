'''
Utility Funcs for DTL

These are imported into the DTL namespace upon import
'''
import os
import sys
import imp
import types
import re
import subprocess
import inspect
import string
import json
from functools import wraps


from DTL.api import Path

#------------------------------------------------------------
def write(*args):
    '''This is here so the API can control where the output goes, and how its goes
    This allows users to make sure their scripts are non-buffering,
    so if they are used by execute with verbose mode we can see the output'''
    line = ''.join(args)
    if not line.endswith('\n'):
        line = line + '\n'
    sys.stdout.write(line)
    sys.stdout.flush()

#------------------------------------------------------------
def execute(cmd, verbose=False, catchError=False):
    '''Given an excutable command, will wrap it in a subprocess call and return the returncode, stdout and stderr'''
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if verbose :
        while process.poll() is None:
            out = process.stdout.readline()
            if out != '' :
                write(out)

    if catchError and process.returncode:
        for line in process.stderr :
            write(line)
        write('[PROCESS FAILED]:{0}'.format(cmd))
        raise Exception('[PROCESS FAILED]:{0}'.format(cmd))
    process.stdout.seek(0,0)
    return process.returncode, process.stdout, process.stderr  

#------------------------------------------------------------
def setEnv(key, value):
    '''method to set the env in a platform independent way'''
    os.environ[key] = value
    if sys.platform == 'win32' :
        execute(['SETX',key,value], catchError=True)
    else:
        execute(['set', '{0}={1}'.format(key,value)], catchError=True)
        execute(['export', key], catchError=True)

#------------------------------------------------------------
def clearEnv(key):
    '''Convenience method for clearing env's'''
    setEnv(key, '')

#------------------------------------------------------------
def getDrives():
    '''method to get the drive letters in a platform independant way
    TODO: Make Unix Compatible'''
    from ctypes import windll
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1

    return drives

#------------------------------------------------------------
def wildcardToRe(pattern):
    """Translate a wildcard pattern to a regular expression"""
    i, n = 0, len(pattern)
    res = '(?i)' #case insensitive re
    while i < n:
        c = pattern[i]
        i = i+1
        if c == '*':
            res = res + r'[^\\]*'
        elif c == '/':
            res = res + re.escape('\\')
        else:
            res = res + re.escape(c)
    return res + "$"

#------------------------------------------------------------
def isBinary(filepath):
    """Return true if the given filepath appears to be binary."""
    #------------------------------------------------------------
    def hasBinaryByte(filepath):
        """File is considered to be binary if it contains a NULL byte."""
        with open(filepath, 'rb') as f:
            for block in f:
                if '\0' in block:
                    return True
        return False

    #------------------------------------------------------------
    def isBinaryString(filepath):
        """File is considered to be binary if the data is binary."""
        textchars = ''.join(map(chr, [7,8,9,10,12,13,27] + range(0x20, 0x100)))
        string_test = lambda bytes: bool(bytes.translate(None, textchars))
        return string_test(open(filepath).read(1024))

    #If information in the filepath has both binary data and the binary NULL byte then its safe to say its binary
    return isBinaryString(filepath) == hasBinaryByte(filepath)





#------------------------------------------------------------
def quickReload(modulename):
    """
    Searches through the loaded sys modules and looks up matching module names 
    based on the imported module.
    """
    expr = re.compile( str(modulename).replace( '.', '\.' ).replace( '*', '[A-Za-z0-9_]*' ) )

    # reload longer chains first
    keys = sys.modules.keys()
    keys.sort()
    keys.reverse()

    for key in keys:
        module = sys.modules[key]
        if ( expr.match(key) and module != None ):
            print 'reloading', key
            reload( module )



#------------------------------------------------------------
def synthesize(object, name, value, readonly=False):
    """
    Convenience method to create getters and setters for a instance. 
    Should be called from within __init__. Creates [name], set[Name], 
    _[name] on object.

    :param object: An instance of the class to add the methods to.
    :param name: The base name to build the function names, and storage variable.
    :param value: The initial state of the created variable.

    """
    storageName = '_{0}'.format(name)
    setterName = 'set{0}{1}'.format(name[0].capitalize(), name[1:])
    if hasattr(object, name):
        raise KeyError('The provided attr {0} already exists'.format(name))
    # add the storeage variable to the object
    setattr(object, storageName, value)
    # define the getter
    def customGetter(self):
        return getattr(self, storageName)
    # define the Setter
    def customSetter(self, state):
        setattr(self, storageName, state)
    # add the getter to the object, if it does not exist
    if not hasattr(object, name):
        setattr(object, name, types.MethodType(customGetter, object))
    # add the setter to the object, if it does not exist
    if not hasattr(object, setterName):
        if readonly == False :
            setattr(object, setterName, types.MethodType(customSetter, object))

#------------------------------------------------------------
def runFile( filepath, basePath=None, cmd=None, debug=False ):
    """
    Runs the filepath in a shell with proper commands given, or passes 
    the command to the shell. (CMD in windows) the current platform

    :param filepath: path to the file to execute
    :param basePath: working directory where the command should be called
    from.  If omitted, the current working directory is used.

    """
    status = False
    filepath = Path(filepath)

    # make sure the filepath we're running is a file 
    if not filepath.isfile():
        return status

    # determine the base path for the system
    if basePath is None:
        basePath = filepath.dir()

    options = { 'filepath': filepath, 'basepath': basePath }

    if cmd == None :
        if filepath.ext in ['.py','.pyw']:
            if debug:
                cmd = 'python.exe "{0}"'.format(filepath)
            else:
                cmd = 'pythonw.exe "{0}"'.format(filepath)

            status = subprocess.Popen( cmd, stdout=sys.stdout, stderr=sys.stderr, shell=debug, cwd=basePath)

    if not status :
        try:
            status = os.startfile(filepath)
        except:
            print 'runFile cannot run type (*{0})'.format(filepath.ext)

    return status

#------------------------------------------------------------
def backup(path, suffix='.bak'):
    """
    Rename a file or directory safely without overwriting an existing
    backup of the same name.

    :param path: The path object to the file or directory to make a backup of.
    :param suffix: The suffix to rename files with.
    :returns: The new path of backed up file/directory
    :rtype: str

    """
    count = -1
    new_path = None
    while True:
        if path.exists() :
            if count == -1:
                new_path = Path("{0}{1}".format(path, suffix))
            else:
                new_path = Path("{0}{1}.{2}".format(path, suffix, count))
            if new_path.exists():
                count += 1
                continue
            else:
                path.copy(new_path)
        else:
            break
    return new_path

#------------------------------------------------------------
def Run(modulename):
    tool_mod = sys.modules.get(modulename, None)
    if tool_mod is None :
        __import__(modulename)
        tool_mod = sys.modules.get(modulename, None)
    else:
        tool_mod.mainUI.instance().close()
        quickReload(modulename)
        tool_mod = sys.modules.get(modulename, None)

    Launch(tool_mod.mainUI.instance)

#------------------------------------------------------------
def Launch(ctor, modal=False):
    """
    This method is used to create an instance of a widget (dialog/window) to 
    be run inside the blurdev system.  Using this function call, blurdev will 
    determine what the application is and how the window should be 
    instantiated, this way if a tool is run as a standalone, a new 
    application instance will be created, otherwise it will run on top 
    of a currently running application.

    :param ctor: callable object that will return a widget instance, usually
    			 a :class:`QWidget` or :class:`QDialog` or a function that
    			 returns an instance of one.
    :param modal: If True, widget will be created as a modal widget (ie. blocks
    			  access to calling gui elements).
    """
    from PyQt4.QtGui import QWizard

    # always run wizards modally
    try:
        modal = issubclass(ctor, QWizard)
    except:
        pass

    # create the output instance from the class
    widget = ctor(None)

    # check to see if the tool is running modally and return the result
    if modal:
        return widget.exec_()
    else:
        widget.show()
        # run the application if this item controls it and it hasnt been run before
        return widget

#------------------------------------------------------------	
def inspectMethod(item):
    """Prints useful information about given python method."""
    print '#------------------------------------------------------------'
    print 'Inspect Python Object'
    if hasattr(item, '__name__'):
        print "NAME:    ", item.__name__
    if hasattr(item, '__class__'):
        print "TYPE:    ", item.__class__.__name__
        #This should probably use inspect to check if its a method or function
        if item.__class__.__name__ in ['instancemethod','function'] :
            print "ARGS:    ", inspect.getargspec(item)[0]
        print "METHODS: ", dir(item)
    print "ID:      ", id(item)
    print "CALLABLE:", "yes" if callable(item) else "No"
    print "VALUE:   ", repr(item)
    print "DOC:     ", getattr(item, '__doc__') if hasattr(item, '__doc__') else ""
    print '#------------------------------------------------------------'
    
#------------------------------------------------------------
def getClassName(x):
    if not isinstance(x, basestring):
        if type(x) in [types.FunctionType, types.TypeType, types.ModuleType] :
            return x.__name__
        else:
            return x.__class__.__name__
    else:
        return x

#------------------------------------------------------------
def print_json(data):
    print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

#------------------------------------------------------------
class requires(object):
    '''A simple networking decorator that allows you to
    require methods to be run before and after making the function call'''

    def __init__(self, func):
        self.func = func
        self.response = None
        wraps(func)(self)

    def __call__(self,*args, **kwargs):
        self.before()
        self.response = self.func(*args, **kwargs)
        self.after()
        return self.response
    
    def before(self):
        pass
    
    def after(self):
        pass