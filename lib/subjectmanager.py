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


    def __isDirectoryAValidSubject(self, source):
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
                    self.info("{} is a valid subject, adding it to the list.".format(os.path.basename(dir)))
                    result = True
                else:
                    self.warning("{} will be discarded".format(os.path.basename(dir)))
            else:
                self.warning("Skipping validation have been requested, this option is dangerous")
                result = True
        else:
            self.warning("{} doesn't look a directory, it will be discarded".format(dir))
        return result


    def __instantiateSubjectsFromDirectories(self):
        """Return directories who qualified for the pipeline

        Look into each subdirectory if it meet all the requirements. If yes, the subdirectory is consider
        a subject and is register into a list

        Returns:
            subjects: a list of directory containing qualified subjects

        """
        subjects = []

        self.info("Directory {} have been specified by the user.".format(self.studyDir))
        self.info("Looking for valid subjects.")

        if self.arguments.subject:
            for dir in self.arguments.subject:
                if self.__isDirectoryAValidSubject(dir):
                    subjects.append(Subject(self.__copyConfig(dir)))
        else:
            dirs = glob.glob("{}/*".format(self.studyDir))
            for dir in dirs:
                if self.__isDirectoryAValidSubject(dir):
                    subjects.append(Subject(self.__copyConfig(dir)))

        subjects = self.__processLocksSubjects(subjects)

        #Subject Load() class need to know how much valid subject are submit.
        for subject in subjects:
            subject.setConfigItem("general", "nb_subjects", str(len(subjects)))

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
                subject = locks[0]
                tags = {"name": subject.getName(), "lock":subject.getLock()}
                msg = util.parseTemplate(tags, os.path.join(self.arguments.toadDir, "templates/files/lock.tpl"))

            else:
                subjectsNames = []
                locksFileNames = []
                for subject in locks:
                    subjectsNames.append(subject.getName())
                    locksFileNames.append(subject.getLock())
                    tags = {"names": ", ".join(subjectsNames) ,"locks":"\t,\n".join(locksFileNames)}
                    msg = util.parseTemplate(tags, os.path.join(self.arguments.toadDir, "templates/files/locks.tpl"))

            if self.config.getboolean('arguments', 'prompt'):
                answer = util.displayContinueQuitRemoveMessage(msg)
            if answer == "y":
                self.info("Locks subjects will be ignored during execution\n")
                subjects = [subject for subject in subjects if subject not in locks]
            elif answer == "r":
                self.info("Removing locks and continue the pipeline\n")
                for lock in locks:
                    if os.path.isfile(lock.getLock()):
                        os.remove(lock.getLock())
                else:
                    self.error("Please submit the pipeline again\n")
            else:
                self.warning(msg)
        return subjects


    def __reinitialize(self, subjects):
        """Reinitialize the study and every subjects into the pipeline

        Move every files and images back to the subjects directory and remove
        all subdirectory that may have been created by the pipeline.
        Remove logs directory created into the root directory of the study

        Args:
            subjects:  a list of subjects

        """

        if self.config.getboolean('arguments', 'prompt'):
            if util.displayYesNoMessage("Are you sure you want to reinitialize your data at is initial stage"):
                self.info("Reinitializing all subjects")
            else:
                self.quit("Exit the pipeline now as user request")
        else:
            self.warning("Prompt message have been disabled, reinitialisation will be force")

        for subject in subjects:
            tasksmanager = TasksManager(subject)
            for task in tasksmanager.getTasks():
                task.cleanup()
            
            print "Clean up subject log"
            subject.removeLogDir()


    def __submitLocal(self, subject):
        """Submit execution of the subject locally in a shell

        Args:
            config:  a configuration structure containing pipeline options

        """
        name = subject.getName()
        self.info("Evaluating which task subject {} should process".format(name))
        tasksmanager = TasksManager(subject)

        if tasksmanager.getNumberOfRunnableTasks():
            message = "Tasks : "
            for task in tasksmanager.getRunnableTasks():
                message += "{}, ".format(task.getName())
            self.info("{}will be submitted into the pipeline".format(message))

            if not subject.isLock():
                try:
                    self.info("Starting subject {} at task {}".format(name, tasksmanager.getFirstRunnableTasks().getName()))
                    subject.lock()
                    tasksmanager.run()
                finally:
                    subject.removeLock()
                    self.info("Pipeline finish at {}, have a nice day!".format(self.getTimestamp()))
            else:
                self.__processLocksSubjects(subject)
        else:
            self.info("Subject {} already completed, it will not be submitted!".format(name))


    def __submitGridEngine(self, subject):
        """Submit execution of the subject into the grid engine

        Args:
            config:  a configuration structure containing pipeline options

        """

        cmd = "echo {0}/bin/toad -u {1} -l {2} -p | qsub -notify -V -N {3} -o {4} -e {4} -q {5}".format(self.config.get('arguments', 'toad_dir'),
              subject.getDir(), self.studyDir, subject.getName(), subject.getLogDir(), self.config.get('general','sge_queue'))
        self.info("Command launch: {}".format(cmd))
        #@DEBUG try to workaround deadlock
        import subprocess
        process = subprocess.Popen(cmd, stdout=None, stderr=None, shell=True)
        process.wait()
        #(stdout, stderr) = util.launchCommand(cmd)
        #self.info("Output produce: {}\n".format(stdout))
        #if stderr is not '':
        #    self.info("Error produce: {}\n".format(stderr))
        #self.info("------------------------\n")


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
        subjects = self.__instantiateSubjectsFromDirectories()

        if self.config.getboolean('arguments', 'reinitialize'):
            self.__reinitialize(subjects)
        else:
            for subject in subjects:
                    if self.config.getboolean('arguments', 'local'):
                        self.__submitLocal(subject)
                    else:
                        self.__submitGridEngine(subject)
