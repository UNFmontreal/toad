from tasksmanager import TasksManager
from validation import Validation
from subject import Subject
from logger import Logger
from config import Config
import util
import glob
import copy
import os

__author__ = 'desmat'

class SubjectManager(Logger, Config):

    def __init__(self, arguments):
        """Schedule and execute pipeline tasks

        Args:
            arguments: command lines arguments specified by the user

        """
        self.arguments = arguments
        self.config = Config(self.arguments).getConfig()
        self.studyDir = self.config.get('arguments', 'studyDir')
        Logger.__init__(self)


    def getName(self):
        """Return the name of the SubjectManager class  in a lower case

        Return:
            name of this class in a lower case
         """

        return self.__class__.__name__.lower()


    def __isDirAValidSubject(self, source):
        """Verify if the directory source may be consider a valid subject

        Args:
            source: an input directory

        returns:
            True if the current directory qualify as a toad subject, False otherwise

        """
        result = False
        dir = os.path.abspath(source)
        if os.path.isdir(dir):
            if self.config.getboolean('arguments','validation'):
                if Validation(dir, self.getLogger(), self.__copyConfig(dir)).run():
                    self.info("%s is a valid subject, adding it to the list."%os.path.basename(dir))
                    result = True
                else:
                    self.warning("%s will be discarded"%os.path.basename(dir))
            else:
                self.warning("Skipping validation have been requested, this option is dangerous")
                result = True
        else:
            self.warning("%s doesn't look a directory, it will be discarded"%dir)
        return result


    def __getSubjectsDirectories(self):
        """Return directories who qualified for the pipeline

        Look into each subdirectory if it meet all the requirements. If yes, the subdirectory is consider
        a subject and is register into a list

        Returns:
            subjects: a list of directory containing qualified subjects

        """
        self.info("Looking for valid subjects.")
        subjects = []

        if self.arguments.subject:
            for dir in self.arguments.subject:
                if self.__isDirAValidSubject(dir):
                    subjects.append(Subject(self.__copyConfig(dir)))
        else:
            dirs = glob.glob("%s/*"%self.studyDir)
            for dir in dirs:
                if self.__isDirAValidSubject(dir):
                    subjects.append(Subject(self.__copyConfig(dir)))

        return subjects


    def __processLocksSubjects(self, subjects):
        """look if some subject are currently lock into the pipeline

        """
        locks = []
        for subject in subjects:
            if subject.isLock():
                locks.append(subject)
        if locks:
            if len(locks) == 1:
                subject = locks.pop()
                tags = {"name": subject.getName(), "lock":subject.getLock()}
                msg = util.parseTemplate(tags, os.path.join(self.arguments.toadDir, "templates/files/lock.tpl"))

            else:
                names = []
                arrayOfLocks = []
                for subject in locks:
                    names.append(subject.getName())
                    arrayOfLocks.append(subject.getLock())
                    tags = {"names": ", ".join(names) ,"locks":"\t,\n".join(arrayOfLocks)}
                    msg = util.parseTemplate(tags, os.path.join(self.arguments.toadDir, "templates/files/locks.tpl"))

            if self.config.getboolean('arguments', 'prompt'):
                util.displayYesNoMessage(msg)
            else:
                self.warning(msg)


    def __reinitialize(self, subjects):
        """Reinitialize the study and every subjects into the pipeline

        Move every files and images back to the subjects directory and remove
        all subdirectory that may have been created by the pipeline.
        Remove logs directory created into the root directory of the study

        Args:
            subjects:  a list of subjects

        """
        if not self.config.getboolean('arguments', 'prompt'):
            msg = "Are you sure you want to reinitialize your data at is initial stage"
            util.displayYesNoMessage(msg)

        else:
            self.warning("Prompt message have been disabled")

        for subject in subjects:

            tasksmanager = TasksManager(subject)
            for task in tasksmanager.getTasks():
                task.cleanup()

            print "Clean up subject log"
            #subject.removeLogDir()


    def __submitLocal(self, subject):
        """Submit execution of the subject locally in a shell

        Args:
            config:  a configuration structure containing pipeline options

        """
        name = subject.getName()
        self.info("Evaluating which task subject %s should process"%(name))
        tasksmanager = TasksManager(subject)

        if tasksmanager.getNumberOfRunnableTasks():
            message = "Tasks : "
            for task in tasksmanager.getRunnableTasks():
                message += "%s, "%task.getName()
            self.info("%swill be submitted into the pipeline"%message)

            if not subject.isLock():
                try:
                    self.info("Starting subject %s at task %s"%(name, tasksmanager.getFirstRunnableTasks().getName()))
                    subject.lock()
                    tasksmanager.run()
                finally:
                    subject.removeLock()
            else:
                self.__processLocksSubjects(subject)
        else:
            self.info("Subject %s already completed, it will not be submitted!"%name)


    def __submitGridEngine(self, subject):
        """Submit execution of the subject into the grid engine

        Args:
            config:  a configuration structure containing pipeline options

        """

        cmd = "echo %s/bin/toad -u %s -l %s -p | qsub -notify -V -N %s -o %s -e %s -q %s"%(self.config.get('arguments', 'toadDir'),
              subject.getDir(), self.studyDir, subject.getName(), subject.getLogDir(), subject.getLogDir(), self.config.get('general','sge_queue'))
        self.info("Command launch: %s"%cmd)
        (stdout, stderr) = util.launchCommand(cmd)
        self.info("Output produce: %s\n"%stdout)
        if stderr is not '':
            self.info("Error produce: %s\n"%stderr)
        self.info("------------------------\n")


    def __copyConfig(self, dir):
        """Create a deep copy of the configuration structure

        ConfigParser is not meant to be copied and do not provide a deepcopy functionality.
        Assign config to an another variable will instead return the same references
        of the ConfigParser. So we need to implement our own deepcopy function.

        Args:
            dir:  the absolute path of the subject directory

        Returns:
            A new copy of the configuration structure
        """
        arguments = copy.deepcopy(self.arguments)
        arguments.subject = os.path.abspath(dir)
        return Config(arguments).getConfig()


    def run(self):
        """Launch the pipeline

        Raises:
            NotImplementedError: multitasks into a shell should be avoid at all cost, this
                functionnality should be probably render obsolete during the next versions

        """
        self.info("Directory %s have been specified by the user."%self.studyDir)
        subjects = self.__getSubjectsDirectories()
        self.__processLocksSubjects(subjects)

        if self.config.getboolean('arguments', 'reinitialize'):
            self.__reinitialize(subjects)
        else:
            for subject in subjects:

                    if self.config.getboolean('arguments', 'local'):
                        self.__submitLocal(subject)
                    else:
                        self.__submitGridEngine(subject)
