from string import Template
import subprocess
import datetime
import signal
import time
import glob
import sys
import os

__author__ = 'mathieu'


def symlink(source, target):
    """link a file into the target directory. the link name is the same as the file

    Args:
        source:  name of the source file
        target:  destination directory

    Returns
        the relative link name created

    """
    if not os.path.isabs(source):
        source = os.path.abspath(source)
    [dir, name] = os.path.split(source)
    #output = os.path.join(target, name)
    src = "../{}/{}".format(os.path.basename(os.path.normpath(dir)), name)
    os.symlink(src, name)
    return src


def gunzip(source):
    """Uncompress a file

    Args:
        source:  a filename to uncompress

    Returns
        the filename resulting from the compression

    """
    cmd = "gunzip {}".format(source)
    launchCommand(cmd)
    return source.replace(".gz","")


def gzip(source):
    """Compress a file

    Args:
        source:  a filename to compress

    Returns
        the filename resulting from the compression

    """
    cmd = "gzip {}".format(source)
    launchCommand(cmd)
    return "{}.gz".format(source)


def launchCommand(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=-1, nice=0):
    """Execute a program in a new process

    Args:
       command: a string representing a unix command to execute
       stdout: this attribute is a file object that provides output from the child process
       stderr: this attribute is a file object that provides error from the child process
       nice: run cmd  with  an  adjusted  niceness, which affects process scheduling
       timeout: Number of seconds before a process is consider void, usefull against deadlock

    Returns
        return a 2 elements tuples representing the standards output and the standard error message

    Raises
        OSError:      the function trying to execute a non-existent file.
        ValueError :  the command line is called with invalid arguments

    """

    start = datetime.datetime.now()
    process = subprocess.Popen(cmd, preexec_fn=lambda: os.nice(nice), stdout=stdout, stderr=stderr, shell=True)

    if timeout == -1:
        process.wait()
    else:
        while process.poll() is None:
            time.sleep(0.2)
            now = datetime.datetime.now()
            if (now - start).seconds > timeout:
                os.kill(process.pid, signal.SIGKILL)
                os.waitpid(-1, os.WNOHANG)
                return None, "Error, a timeout for this process occurred"

    return process.communicate()


def createScript(source, text):
    """Very not useful and way over simplistic method for creating a file

    Args:
        source: The absolute name of the script to create
        text: Text to write into the script

    Returns:
        True if the file
    """
    try:
        f = open(source, 'w')
        f.write(text)
        f.close()

    except IOError:
        return False
    return True


def __arrayOf(source, type = 'String'):
    """Convert a comma separated  string to a list of built-in elements

    Args:
       source:  a comma separated list of  string to convert
       type:        the type of element expected into the output list
                    valid value are: String, Integer, Float and Boolean
    Returns
        a list of expected type elements specified by type

    """
    list = source.replace(';', ',').split(',')
    if type in "Boolean":
        array=[]
        for i in list:
            array.append(i.lower().strip() == 'true')
        return array
    elif type in "Float":
        list = map(float, list)
    elif type in "Integer":
        list = map(int, list)
    return list


def arrayOfBoolean(source):
    """Convert a comma separated string to a list of Boolean elements

    Args:
       source: a comma separated list of  string to convert

    Returns
        a list of Boolean elements

    """
    return __arrayOf(source, 'Boolean')


def arrayOfInteger(source):
    """Convert a comma separated string to a list of Integer elements

    Args:
       source: a comma separated list of  string to convert

    Returns
        a list of Integer elements

    """
    return __arrayOf(source, 'Integer')


def arrayOfFloat(source):
    """Convert a comma separated string to a list of Float elements

    Args:
       source: a comma separated list of  string to convert

    Returns
        a list of Float elements

    """
    return __arrayOf(source, 'Float')


def arrayOfString(source):
    """Convert a comma separated string to a list of String elements

    Args:
       source: a comma separated list of  string to convert

    Returns
        a list of String elements

    """
    return __arrayOf(source, 'String')


def getImage(config, dir, prefix, postfix=None, ext="nii"):
    """A simple utility function that return an mri image given certain criteria

    Args:
        config:  a ConfigParser object
        dir:     the directory where looking for the image
        prefix:  an expression that the filename should start with
        postfix: an expression that the filename should end with (excluding the extension)
        ext:     name of the extension of the filename

    Returns:
        the absolute filename if found, False otherwise

    """
    if ext.find('.') == 0:
        ext=ext.replace(".","",1)
    if postfix is None:
        images = glob.glob("{}/{}*.{}".format(dir, config.get('prefix', prefix), ext))
    else:
        pfixs = ""
        if isinstance(postfix, str):
            pfixs = config.get('postfix', postfix)
        else:
            for element in postfix:
                pfixs = pfixs + config.get('postfix', element)
        images = glob.glob("{}/{}*{}.{}".format(dir, config.get('prefix',prefix), pfixs, ext))
    if len(images) > 0:
        return images.pop()

    return False


def buildName(config, target, source, postfix=None, ext=None, absolute=True):
    """A simple utility function that return a file name that contain the postfix and the current working directory

    The path of the filename contain the current directory
    The extension name will be the same as source unless specify by argument

    Args:
        config: A configParser that contain config.cfg information
        target: The path of the resulting target filename
        source: The input file name, a config prefix or simply a string
        postfix: An option item specified in config at the postfix section
        ext: the Extension of the new target
        absolute: a bolean if the full path must be absolute

    Returns:
        a file name that contain the postfix and the current working directory
    """
    parts = []
    if config.has_option('prefix', source):
        targetName = config.get('prefix',source)
    else:
        parts = os.path.basename(source).split(os.extsep)
        targetName = parts.pop(0)

    if postfix is not None:
        if type(postfix) is list:
            for item in postfix:
                targetName += config.get('postfix', item)
        else:
            targetName += config.get('postfix', postfix)

    extension = ""
    for part in parts:
        extension += ".{}".format(part)
    if ext is not None:
        if len(ext)>0 and ext[0] != ".":
            extension = ".{}".format(ext)
        else:
            extension = ext    

    targetName+=extension
    
    if absolute:
        targetName = os.path.join(target, targetName)
    
    return targetName


def which(source):
    def isExecutable(sourcePath):
        return os.path.isfile(sourcePath) and os.access(sourcePath, os.X_OK)

    sourcePath, sourceName = os.path.split(source)
    if sourcePath:
        if isExecutable(source):
            return source
    else:
        for dir in os.environ["PATH"].split(os.pathsep):
            dir = dir.strip('"')
            executable = os.path.join(dir, source)
            if isExecutable(executable):
                return executable

    return None


def parseTemplate(dict, template):
    """provide simpler string substitutions as described in PEP 292

    Args:
       dict: dictionary-like object with keys that match the placeholders in the template
       template: object passed to the constructors template argument.

    Returns:
        the string substitute

    """
    f = open(template, 'r')
    return Template(f.read()).safe_substitute(dict)

def displayYesNoMessage(msg):
    print msg
    while True:
        choice = raw_input("Continue? (y or n)")
        if choice == 'y':
            print "\n Subjects will failed during the execution\n"
            break
        elif choice == 'n':
            print "\nSubmit the pipeline again\n"
            sys.exit()
