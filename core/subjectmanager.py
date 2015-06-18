import glob
import copy
import os

from tasksmanager import TasksManager
from validation import Validation
from subject import Subject
from logger import Logger
from config import Config
from lib import util


__author__ = 'desmat'

class SubjectManager(Logger, Config):

    def __init__(self, arguments):
        """Schedule and execute pipeline tasks

        Args:
            arguments: command lines arguments specified by the user

        """
        self.arguments = arguments
        self.config = Config(self.arguments).getConfig()
        Logger.__init__(self)


    def getName(self):
        """Return the name of the SubjectManager class in a lower case

        Return:
            name of this class in a lower case
         """

        return self.__class__.__name__.lower()


    def __validateSubjects(self, subjects):
        """Verify into a list of toad subjects the integrity and validity of each subject

        Args:
            subjects: a list of toad subjects

        returns:
            a list of valid subjects

        """
        validSubjects = []
        if self.config.getboolean('arguments','validation'):
            for subject in subjects:
                if Validation(subject.getDir(), self.getLogger(), self.__copyConfig(subject.getDir())).validate():
                    self.info("{} is a valid subject, adding it to the list.".format(subject))
                    validSubjects.append(subject)
                elif self.config.getboolean('arguments', 'prompt'):
                        msg = "It seem\'m like {} is having an issue and will probably fail!".format(subject)
                        if util.displayYesNoMessage(msg, "Would you like to remove it from the list (y or n)"):
                            self.info("Removing subject {} from the submitting list\n".format(subject))
                        else:
                            self.warning("Keeping {} even if we found issues will probably make the pipeline failing\n"
                            .format(subject))
                            validSubjects.append(subject)
                else:
                    self.warning("Command prompt disabled, this submit will be submit anyway")
                    validSubjects.append(subject)
        else:
            self.warning("Skipping validation have been requested, this is a unwise and dangerous decision")
            validSubjects = subjects

        return validSubjects


    def __processLocksSubjects(self, subjects):
        """look if some subjects from a list currently are locked into the pipeline

        Args:
            subjects: a list of the subject

        Returns:
            a list of subjects that is not lock
        """
        locks = []
        for subject in subjects:
            if subject.isLock():
                locks.append(subject)
        if locks:
            if len(locks) == 1:
                subject = locks[0]
                tags = {"name": subject.getName(), "lock":subject.getLock()}
                msg = util.parseTemplate(tags, os.path.join(self.arguments.toadDir, "templates", "files", "lock.tpl"))

            else:
                subjectsNames = []
                locksFileNames = []
                for subject in locks:
                    subjectsNames.append(subject.getName())
                    locksFileNames.append(subject.getLock())
                    tags = {"names": ", ".join(subjectsNames) ,"locks":"\t,\n".join(locksFileNames)}
                    msg = util.parseTemplate(tags, os.path.join(self.arguments.toadDir, "templates", "files", "locks.tpl"))

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
            subject:  a subject

        """
        if subject.getConfig().get('general', 'server') in ['magma' , 'stark']:
            notify = " -notify "
        else:
            notify = ""

        extraFlags = ""

        if ((subject.getConfig().getboolean('tractographymrtrix', 'ignore') is False) or
            (subject.getConfig().getboolean('tractographydipy', 'ignore') is False)):
            extraFlags += " --tractography "

        if subject.getConfig().get('general', 'server') in ['mammouth']:
            extraFlags += " -l walltime=48:00:00 "


        cmd = "echo {0}/bin/toad {1} -l -p | qsub {2} -V -N {3} -o {4} -e {4} -q {5} {6}".format(self.config.get('arguments', 'toad_dir'),
              subject.getDir(), notify, subject.getName(), subject.getLogDir(),subject.getConfig().get('general', 'sge_queue'), extraFlags)
        self.info("Command launch: {}".format(cmd))

        import subprocess
        process = subprocess.Popen(cmd, stdout=None, stderr=None, shell=True)
        process.wait()


    def __copyConfig(self, directory):
        """Create a deep copy of the configuration structure

        ConfigParser is not meant to be copied and do not provide a deepcopy functionality.
        Assign config to an another variable will instead return the same references
        of the ConfigParser. So we need to implement our own deepcopy function.

        Args:
            directory:  the absolute path of the subject directory

        Returns:
            A new copy of the configuration structure
        """
        arguments = copy.deepcopy(self.arguments)
        arguments.subject = directory
        return Config(arguments).getConfig()


    def __expandDirectories(self):
        """functionnality that return every absolute directory and it subdirectories specified as input command line
            study directory

        Directory that contain a subdirectory with 01-backup name will be automaticaly discard
        Files are automaticaly discarded
        No further validation is done

        Returns
            A list unique absolute directory

        """
        def find(pattern, list):
            for item in list:
                if pattern in item:
                    return True
            return False

        results = []
        for argument in self.arguments.inputs:
            absoluteDirectory = os.path.abspath(argument)
            if os.path.isdir(absoluteDirectory):
                results.append(absoluteDirectory)
                directories = glob.glob("{}/*".format(absoluteDirectory))
                if not find("00-backup", directories):
                    for directory in directories:
                        if os.path.isdir(directory):
                            results.append(directory)

        return list(set(results))


    def __subjectsFactory(self, directories):
        """Return a list of directories who qualified for the pipeline

        Args:
            directories: a list of directory to validate

        Returns:
            subjects: a list of directory containing qualified subjects

        """
        subjects=[]
        for directory in directories:
            if Validation(directory, self.getLogger(), self.__copyConfig(directory)).isAToadSubject():
                self.info("{} seem\'s a valid toad subject entry".format(directory))
                subjects.append(Subject(self.__copyConfig(directory)))
        return subjects


    def run(self):
        """Launch the pipeline
        """

        #create the subjects
        subjects = self.__subjectsFactory(self.__expandDirectories())

        #Validate each subjects integrity
        subjects = self.__validateSubjects(subjects)

        #determine if subject that are locks
        subjects = self.__processLocksSubjects(subjects)

        #update into each subject how many subjects should be submit. This information is sensitive for load balancing the grid
        for subject in subjects:
            subject.setConfigItem("general", "nb_subjects", str(len(subjects)))

        if self.config.getboolean('arguments', 'reinitialize'):
            self.__reinitialize(subjects)
        else:
            for subject in subjects:
                    if self.config.getboolean('arguments', 'local'):
                        self.__submitLocal(subject)
                    else:
                        self.__submitGridEngine(subject)
