# -*- coding: utf-8 -*-
from datetime import timedelta
from datetime import datetime
import subprocess
import traceback
import shutil
import os

from lib.images import Images
from core.toad.logger import Logger
from core.toad.qa import Qa
from load import Load
from lib import util


__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class GenericTask(Logger, Load, Qa):

    def __init__(self, subject, *args):
        """Set up a TASK child class environment.

        Initialise the Global Configuration, the Logger, the system load routines.
        Define a list of dependencies prerequisite to run this tasks.
        Define, create and aliases a Working directory for the tasks.

        If more arguments have been supplied to generic tasks, GenericTask will create an alias
        for each additionnal arg adding the suffix Dir to the name provided
        on the first optionnal arg provided to __init__

        """

        self.__order = self.initializeTasksOrder()
        self.__name = self.__class__.__name__.lower()
        self.__moduleName = self.__class__.__module__.split(".")[-1]
        self.__cleanupBeforeImplement = True
        self.config = subject.getConfig()
        self.subject = subject
        self.subjectDir = self.subject.getDir()
        self.toadDir = self.config.get('arguments', 'toad_dir')
        self.workingDir = os.path.join(self.subjectDir, self.__moduleName)
        self.logDir = os.path.join(self.subjectDir, self.get('dir', 'log'))
        self.qaDir = os.path.join(self.subjectDir, '00-qa')
        self.tasksAsReferences = None
        Logger.__init__(self, subject.getLogDir())
        Load.__init__(self, self.config)
        Qa.__init__(self)
        self.dependencies = []
        self.__dependenciesDirNames = {}
        for arg in args:
            self.dependencies.append(arg)


    def initializeDependenciesDirectories(self, tasks):
        for index, dependency in enumerate(self.dependencies):
            for task in tasks:
                if dependency == task.__name:
                    self.__dependenciesDirNames["{}Dir".format(dependency)] = task.workingDir
                    setattr(self, "{}Dir".format(dependency), task.workingDir)


    def initializeTasksAsReferences(self, tasks):
        self.tasksAsReferences = tasks


    def initializeTasksOrder(self):
        """if the task file name contain the prefix xx- who xx represent an integer. Use that value as a weight
            to establish priority during for qa generation

        Return
            order: a weight that will be take into account during tasks sorting
        """
        order = None
        module = self.__class__.__module__.split('-')

        if len(module) >1:
            try:
                order = int(module[0])
            except ValueError:
                pass
        return order


    def getOrder(self):
        """return the order of execution of this subclasses

        Args:
            order: an integer that represent the order of the execution of the task
        """
        return self.__order


    def setOrder(self, order):
        """Define the order of execution of the subclasses

        Args:
            order: an integer that represent the order of the execution of the task
        """
        self.__order = order

    def __repr__(self):
        """Return the name of the task as a a printable representation of the task object."""
        return self.__name


    def __eq__(self, other):
        """Override method of the operator equal"""
        return (isinstance(other, type(self))
                and (self.__name, self.__order) == (other.__name, other.__order))


    def __ne__(self, other):
        """Override method of the operator not equal"""
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result


    def __lt__(self, other):
        """Override method of the operator less than"""
        return self.__order < other.__order


    def __hash__(self):
        """Called for operations on members of collections dictionnary. Should return an integer"""
        return (hash(self.__name)<<1) ^ hash(self.__order)



    def __getattr__(self, items):
        """A simple Generic function that wrap getImage
            return an mri image given certain criteria
            this is a wrapper over mriutil getImage function

        Args:
            prefix:  an expression that the filename should start with
            postfix: an expression that the filename should end with (excluding the extension)
            ext:     name of the extension of the filename. defaults: nii.gz

        Returns:
            the relative filename if found, False otherwise

        """
        if items.startswith('get') and items.endswith('Image'):
            if "getImage" in items:
                directory = self.workingDir
            else:
                taskName = items[3:-5].lower()
                directory = getattr(self, "{}Dir".format(taskName))
                if not directory:
                    self.warning("method {} request into task {} but {} dependencies not found,  "
                                 .format(items, self.getName(),taskName))

            def wrapper(*args):
                arguments = [self.config, directory] + list(args)
                return util.getImage(*arguments)
            return wrapper
        else:
            return False


    def __implement(self):
        """Generic implementation of a tasks

        -A task should create and move into is own working space

        """
        self.info("Launching implementation of {} task".format(self.getName()))
        if not os.path.exists(self.workingDir):
            self.info("Creating {} directory".format(self.workingDir))
            os.mkdir(self.workingDir)

        if self.config.has_option("arguments", "stop_before_task"):
            if (self.config.get("arguments", "stop_before_task") == self.__name or
                self.config.get("arguments", "stop_before_task") == self.__moduleName.lower()):
                self.quit("Reach {} which is the value set by stop_before_task. Stopping the pipeline as user request"
                             .format(self.config.get("arguments", "stop_before_task")))
        os.chdir(self.workingDir)
        util.symlink(self.getLogFileName(), self.workingDir)
        if "qaSupplier" in dir(self):
            self.updateQaMenu()
        self.implement()
        self.info("Create and supply images to the qa report ")
        if "qaSupplier" in dir(self):
            self.createQaReport(self.qaSupplier())
        else:
            self.info("task {} does not implement qaSupplier method".format(self.getName()))

        os.chdir(self.subjectDir)


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
        result = self.meetRequirement()
        if isinstance(result, Images):
            if self.get("arguments", "debug"):
                self.debug(result)
            result = result.isAllImagesExists()

        elif isinstance(result, bool):
            if self.get("arguments", "debug"):
                self.debug("No debugging information provided for this tasks")
        else:
            self.error("Illegal value return by meetRequirement method for task {}".format(self.getName()))

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
            if isinstance(result, Images):
                if self.get("arguments", "debug"):
                    self.debug(result)
                result = result.isSomeImagesMissing()
            elif isinstance(result, bool):
                if self.get("arguments", "debug"):
                    self.debug("No debugging information provided for this tasks")
            else:
                self.error("Illegal value return by isDirty method for task {}".format(self.getName()))

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
            os.chdir(self.subjectDir)
            shutil.rmtree(self.workingDir)


    def run(self):
        """Method that have the responsibility to launch the implementation

        Args:
            tasks: the list of all  qualified task for this pipeline

        """
        #@TODO relocate logHeader 'implements'
        attempt = 0
        self.logHeader("implement")
        start = datetime.now()

        if self.__meetRequirement():
            try:
                nbSubmission = int(self.config.get('general', 'nb_submissions'))
            except ValueError:
                nbSubmission = 3

            while(attempt < nbSubmission):
                if self.__cleanupBeforeImplement:
                    self.__cleanup()

                try:
                    self.__implement()
                except (KeyboardInterrupt, SystemExit):
                    self.error("KeyboardInterrupt or SystemExit caught, pipeline will exit")
                    raise
                except Exception, exception:
                    print "exception=",exception
                    print "traceBack = ", traceback.format_exc()
                    self.warning("Exception have been caught, the error message is: {}".format(exception))
                    self.warning("Traceback is: {}".format(traceback.format_exc()))
                if attempt == nbSubmission:
                    self.error("I already execute this task {} time and failed, exiting the pipeline")

                elif self.isTaskDirty():
                    self.info("A problems occur during the execution of this task, resubmitting this task again")
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


    def get(self, *args):
        """Utility that return a config element value from config.cfg base on superclass name as section

        Args:
           args: list of arguments as positional arguments. 
            if only 1 arguments is provide, the section will be the class name (the current class). and the argument will be the options name as specify in config.cfg
            if more arguments is provide, the first arguments will be the section and de second argument will be the the options name as specify in config.cfg

        Returns:
            If value is equal to True or False return a boolean, return a string otherwise
            A string value

        """
        if len(args) < 2:
            value = self.config.get(self.getName(), args[0])
        else:
            value = self.config.get(args[0], args[1])
        if value in ["True", "true"]:
            return True
        elif value in ["False", "false"]:
            return False
        else:
            return value


    def launchCommand(self, cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=None, nice=0):
        """Execute a program in a new process

        Args:
            command: a string representing a unix command to execute
            stdout: this attribute is a file object that provides output from the child process
            stderr: this attribute is a file object that provides error from the child process
            timeout: Number of seconds before a process is consider inactive, usefull against deadlock
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

        self.info("Launch {} command line...".format(binary))
        self.info("Command line submit: {}".format(cmd))

        (executedCmd, output, error)= util.launchCommand(cmd, stdout, stderr, timeout, nice)
        if not (output is "" or output is "None" or output is None):
            self.info("Output produce by {}: {} \n".format(binary, output))

        if not (error is '' or error is "None" or error is None):
            self.info("Error produce by {}: {}\n".format(binary, error))
        self.info("------------------------\n")


    def launchMatlabCommand(self, source, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=None, nice=0):
        """Execute a Matlab script in a new process

        The script must contains all paths and program that are necessary to run the script

        Args:
            source: A matlab script to execute in the current working directory
            stdout: this attribute is a file object that provides output from the child process
            stderr: this attribute is a file object that provides error from the child process
            timeout: Number of seconds before a process is consider inactive, usefull against deadlock
            nice: run cmd  with  an  adjusted  niceness, which affects process scheduling
        Returns
            return a 3 elements tuples representing the command execute, the standards output and the standard error message

        """

        [scriptName, ext] = os.path.splitext(os.path.basename(source))
        tags={ 'script': scriptName, 'workingDir': self.workingDir}
        cmd = self.parseTemplate(tags, os.path.join(self.toadDir, "templates", "files", "matlab.tpl"))
        self.info("Launching matlab command: {}".format(cmd))
        self.launchCommand(cmd, stdout, stderr, timeout, nice)


    def buildName(self, source, postfix, ext=None, absolute = True):
        """A simple utility function that return a file name that contain the postfix and the current working directory

        The filename is always into the current working  directory
        The extension name will be the same as source unless specify as argument

        Args:
            source: the input file name
            postfix: single element or array of elements which option item specified in config at the postfix section
            ext: the extension of the new target

        Returns:
            a file name that contain the postfix and the current working directory
        """
        absoluteBuildName = util.buildName(self.config, self.workingDir, source, postfix, ext, absolute)
        return os.path.basename(absoluteBuildName.replace("'",""))


    def uncompressImage(self, source):
        """Copy a source image into current working directory and uncompress it

        Args:
            source:  name of the source file
        Returns
            name of the output file

        """
        imageDir = os.path.dirname(source)
        if not imageDir or (imageDir in self.workingDir):
            target = source
        else:
            self.info("Copying image {} into {} directory".format(source, self.workingDir))
            shutil.copy(source, self.workingDir)
            target = os.path.join(self.workingDir, os.path.basename(source))

        self.info("Uncompress image.".format(target))
        return util.gunzip(target)


    def rename(self, source, target):
        """rename an image name specify as source

        Args:
            source:  name of the source file
            target:  name of the output file

        Returns
            name of the output file

        """
        self.info("renaming {} to {}".format(source, target))

        if os.path.exists(source):
            os.rename(source, target)
            return target
        else:
            self.warning("unable to find {} image".format(source))
            return False


    def parseTemplate(self, dict, template):
        """provide simpler string substitutions as described in PEP 292

        Args:
           dict: dictionary-like object with keys that match the placeholders in the template
           template: object passed to the constructors template argument.

        Returns:
            the string substitute

        """

        return util.parseTemplate(dict, template)

