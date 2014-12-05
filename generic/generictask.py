from modules.logger import Logger
from datetime import timedelta
from datetime import datetime
from modules import util
from modules.load import Load
from generic import singleton
import subprocess
import shutil
import glob
import os

__author__ = 'desmat'


class GenericTask(Logger, Load):

    def __init__(self, subject, *args):
        """Set up a TASK child class environment.

        Initialise the Global Configuration, the Logger, the system load routines.
        Define a list of dependencies prerequisite to run this tasks.
        Define, create and aliases a Working directory for the tasks.

        If more arguments have been supplied to generic tasks, GenericTask will create an alias
        for each additionnal arg adding the suffix Dir to the name provided and then create  an alias 'dependDir'
        on the first optionnal arg provided to __init__

        """

        self.__order = None
        self.__name = self.__class__.__name__.lower()
        self.__cleanupBeforeImplement = True
        self.config = subject.getConfig()
        self.subjectDir = subject.getDir()
        self.toadDir = self.config.get('arguments', 'toadDir')
        self.workingDir = os.path.join(self.subjectDir,  self.__class__.__module__.split(".")[-1])
        Logger.__init__(self, subject.getLogDir())
        Load.__init__(self, self.config.get('general', 'nthreads'))
        self.dependencies = []
        self.__dependenciesDirNames = {}
        for arg in args:
            self.dependencies.append(arg)
        for i, arg in enumerate(args):
            images = glob.glob("{}/tasks/??-{}.py".format(self.toadDir, arg))
            if len(images) == 1:
                [name, ext] = os.path.splitext(os.path.basename(images[0]))
                dir = os.path.join(self.subjectDir, name)
                setattr(self, "{}Dir".format(arg), dir)
                self.__dependenciesDirNames["{}Dir".format(arg)] = dir
                if i == 0:
                    self.dependDir = dir


    def getOrder(self):
        return self.__order


    def setOrder(self, order):
        self.__order = order


    def __repr__(self):
        return self.__name


    def __eq__(self, other):
        return (isinstance(other, type(self))
                and (self.__name, self.__order) == (other.__name, other.__order))


    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result


    def __lt__(self, other):
        return self.__order < other.__order


    def __hash__(self):
        return (hash(self.__name)<<1) ^ hash(self.__order)


    def __implement(self):
        """Generic implementation of a tasks

        -A task should create and move into is own working space

        """
        if not os.path.exists(self.workingDir):
            self.info("Creating {} directory".format(self.workingDir))
            os.mkdir(self.workingDir)
        currentDir = os.getcwd()
        os.chdir(self.workingDir)
        util.symlink(self.getLogFileName(), self.workingDir)
        self.implement()
        os.chdir(currentDir)



    #this is where all the science occurs
    def implement(self):
        """Placeholder for the business logic implementation

         This function need to be implemented by a subclass of GenericTask

        Raises:
            NotImplementedError: this function have not been overridden by it's subClass

        """
        raise NotImplementedError


    def __meetRequirement(self):
        """Base class that validate that all requirements have been met prior to launch the task

            make sure that all dependent directory exists (why?)
            then call superclass meetRequirement

        """
        self.logHeader("meetRequirement")

        #@TODO clarify this situation
        #for key, value in self.__dependenciesDirNames.iteritems():

        #    #make sure that this directory is not optionnal
        #    if not os.path.exists(value):
        #        self.error("Mandatory directory {} not found".format(value))
        result = self.meetRequirement()
        self.logFooter("meetRequirement", result)
        return result


    def meetRequirement(self, result = False):
        """Validate that all requirements have been met prior to launch the task

        This function need to be implemented by a subclass of GenericTask

        Args:
            result: A convenient boolean that we expect to be use for storing the status of this function

        Returns:
            result: True if all requirement are meet, False otherwise

        Raises:
            NotImplementedError: this function have not been overridden by it's subClass

        """
        raise NotImplementedError


    def isIgnore(self):
        """Parameter that determine if a tasks is optional

            if an overload of this method return True, the current tasks will be ignore

            Returns:
                True if this tasks should be skipped, False otherwise
        """
        return False


    def isTaskDirty(self):
        """Base class that validate if this tasks need to be submit for implementation

        """
        self.logHeader("isDirty")
        if self.isIgnore():
            self.logFooter("isDirty", None)
            return False

        if not os.path.exists(self.workingDir):
            self.info("Directory {} not found".format(self.workingDir))
            self.logFooter("isDirty", True)
            return True

        else:
            result = self.isDirty()
            self.logFooter("isDirty", result)
            return result


    def isDirty(self, result = False):
        """Validate if this tasks need to be submit for implementation

        This function need to be implemented by a subclass of GenericTask

        Args:
            result: A convenient boolean that we expect to be use for storing the status of this function

        Returns:
            result: True if this tasks need to be submit for implementation, False otherwise

        Raises:
            NotImplementedError: this function have not been overridden by it's subClass

        """
        raise NotImplementedError

    def setCleanupBeforeImplement(self, cleanup=True):
        """Determine if the working directory need to be cleanup before launching task implementation
        """
        self.__cleanupBeforeImplement = cleanup

    def __cleanup(self):
        """Base class that remove every files that may have been produce during the execution of the parent task.

        """
        self.cleanup()


    def cleanup(self):
        """Default implementation of the cleanup files. This method remove any files that may have been produce
           during the execution.

        Can and should be overwritten by a parent class

        """
        if os.path.exists(self.workingDir) and os.path.isdir(self.workingDir):
            self.info("Cleaning up \"deleting\" {} directory".format(self.workingDir))
            shutil.rmtree(self.workingDir)


    def run(self):
        """Method that have the responsability to lauch the implementation

        """
        #@TODO relocate logHeader 'implements'
        attempt = 0
        self.logHeader("implement")
        start = datetime.now()
        if self.__meetRequirement():
            try:
                nbSubmission = int(self.config.get('general','nbsubmissions'))
            except ValueError:
                nbSubmission = 3

            while(attempt < nbSubmission):
                if self.__cleanupBeforeImplement:
                    self.__cleanup()
                self.__implement()
                if attempt == nbSubmission:
                    self.error("Cannot execute this task successfully, exiting the pipeline")
                elif self.isDirty():
                    self.info("A problems occur during the task execution, resubmitting this task again")
                    attempt += 1
                else:
                    finish = datetime.now()
                    self.info("Time to finish the task = {} seconds".format(str(timedelta(seconds=(finish - start).seconds))))
                    self.logFooter("implement")
                    break

    def getName(self):
        """Return the name of this class into lower case
        """
        return self.__name


    def getDependencies(self):
        """Return the list of all prerequisite to run this tasks.
        """
        return self.dependencies


    def get(self, option):
        """Utility that return a config element value from config.cfg base on superclass name as section

        Args:
           option: the options name as specify in config.cfg file

        Returns:
            A string value

        """
        return self.config.get(self.getName(), option)


    def getBoolean(self, option):
        """Utility that return a config element value from config.cfg base on superclass name as section

        Args:
           option: the options name as specify in config.cfg file

        Returns:
            A boolean value

        """
        return self.config.getboolean(self.getName(), option)


    def launchCommand(self, cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, nice = 2):
        """Execute a program in a new process

        Args:
           command: a string representing a unix command to execute
           stdout: this attribute is a file object that provides output from the child process
           stderr: this attribute is a file object that provides error from the child process
           nice: run cmd  with  an  adjusted  niceness, which affects process scheduling

        Returns
            return a 3 elements tuples representing the command execute, the standards output and the standard error message

        Raises
            OSError:      the function trying to execute a non-existent file.
            ValueError :  the command line is called with invalid arguments

        """

        binary = cmd.split(" ").pop(0)
        if util.which(binary) is None:
            self.error("Command {} not found".format(binary))

        self.info("Launch {} command line...\n".format(binary))
        self.info("Command line submit: {}\n".format(cmd))

        out = None
        err = None

        if stdout=='log':
            out = self.getLog()
            self.info("Output will be log in {} \n".format(out.name))
        if stderr=='log':
            err = self.getLog()
            self.info("Error will be log in {} \n".format(err.name))

        (output, error)= util.launchCommand(cmd, out, err, nice)
        if stdout is not "None":
            self.info("Output produce by {}: {} \n".format(binary, output))

        if error != '' or error != "None":
            self.info("Error produce by {}: {}\n".format(binary, error))
        self.info("------------------------\n")


    def launchMatlabCommand(self, source, singleThread = True):
        """Execute a Matlab script in a new process

        The script must contains all paths and program that are necessary to run the script

        Args:
            source: A matlab script to execute in the current working directory
            singleThread: If matlab should run in multithread mode
        Returns
            return a 3 elements tuples representing the command execute, the standards output and the standard error message

        """

        if singleThread:
            singleCompThread = "-singleCompThread"
        else:
            singleCompThread=""

        [scriptName, ext] = os.path.splitext(os.path.basename(source))
        tags={ 'script': scriptName, 'workingDir': self.workingDir, 'singleCompThread': singleCompThread}
        cmd = self.parseTemplate(tags, os.path.join(self.toadDir, "templates/files/matlab.tpl"))
        self.info("Launching matlab command: {}".format(cmd))
        self.launchCommand(cmd, 'log')


    def getImage(self, dir, prefix, postfix=None, ext="nii"):
        """A simple utility function that return an mri image given certain criteria

        this is a wrapper over mriutil getImage function

        Args:
            dir:     the directory where looking for the image
            prefix:  an expression that the filename should start with
            postfix: an expression that the filename should end with (excluding the extension)
            ext:     name of the extension of the filename

        Returns:
            the absolute filename if found, False otherwise

        """
        return util.getImage(self.config, dir, prefix, postfix, ext)


    def getTarget(self, source, postfix, ext=None, absolute = True):
        """A simple utility function that return a file name that contain the postfix and the current working directory

        The path of the filename contain the current working  directory
        The extension name will be the same as source unless specify as argument

        Args:
            source: the input file name
            postfix: single element or array of elements which option item specified in config at the postfix section
            ext: the extension of the new target

        Returns:
            a file name that contain the postfix and the current working directory
        """
        return util.getTarget(self.config, self.workingDir, source, postfix, ext, absolute)


    def isSomeImagesMissing(self, dict):
        """Iterate over a dictionary of getImage to see if all image exists

        This function is an helper for isDirty and meetRequirement method
        The key represent a description of the image, the value is a call to getImage.

        Args:
            dict: key: contain a description of the image
                  value: contain  getImage call

        Returns:
            True if some image do not exists, False otherwise
        """
        result = False
        for key, value in dict.iteritems():
            if not value:
                self.info("No {} image found".format(key))
                result = True
        return result


    def isAllImagesExists(self, dict):
        """Iterate over a dictionary of getImage to see if all image exists

        This function is an helper for isDirty and meetRequirement method
        The key represent a description of the image, the value is a call to getImage.

        Args:
            dict: key: contain a description of the image
                  value: contain  getImage call

        Returns:
            True if all images in the dictionary exists, False otherwise
        """
        return not self.isSomeImagesMissing(dict)


    def parseTemplate(self, dict, template):
        """provide simpler string substitutions as described in PEP 292

        Args:
           dict: dictionary-like object with keys that match the placeholders in the template
           template: object passed to the constructors template argument.

        Returns:
            the string substitute

        """

        return util.parseTemplate(dict, template)
