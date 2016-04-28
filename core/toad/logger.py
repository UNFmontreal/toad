# -*- coding: utf-8 -*-
import datetime
import sys
import os

from lib import util

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class Logger(object):

    def __init__(self, path = None):
        """Provide a simple, custom, logging capability for the toad pipeline.

        The purpose of this class is to provide a simple, custom, logging capability for the toad
        pipeline. Thanks to late nipype who were resetting the configuration before each call.

        Args
            path: the folder where the log file should be created

        """
        if path is None:
            self.__logIntoFile = False
        else:
            self.__logIntoFile = True
            self.filename = "{}/{}.log".format(path, self.getName())
            archiveLogName = "{}.archive".format(self.filename)
            self.__rotateLog(self.filename, archiveLogName)
            with open(self.filename,'w') as f:
                f.write("#########################################################################\n")
                f.write("\n")
                f.write(" Start logging task {} at {}".format(self.getName(), self.getTimestamp()))
                f.write("\n")
                f.write("\n")
                f.write("#########################################################################\n")

    def getTimestamp(self):
        """Return the current time and date formated as %Y%m%d %Hh%M

        example if the current time is  9:41 the 14 october 2014, the timestamp will
        return the string: 20141014 09h41

        Returns:
            a string that represent a timestamp

        """
        return datetime.datetime.now().strftime("%Y%m%d %Hh%M")

    def logHeader(self, methodName):
        """Format and write a user friendly header message into the log file

        Args:
            methodName: the name of method that call this function
                        valid values are: isDirty, meetRequirement, implement

        """
        if methodName == "isDirty":
            self.info("Looking if task {} need to be submit".format(self.getName()))
        elif methodName == "meetRequirement":
            self.info("Looking if all requirement are met prior submitting the task {}.".format(self.getName()))
        elif methodName == "implement":
            self.info("Starting task {} at {}.".format(self.getName(), self.getTimestamp()))

    def logFooter(self, methodName, result=False):
        """Format and write a user friendly footer message into the log file

        Args:
            methodName: the name of method that call this function
                        valid values are: isDirty, meetRequirement, implement
            result: the status return by the command specify by methodName

        """
        if methodName == "isDirty":
            if result is None:
                self.info("Ignoring flag activate, task {} will be skipped.\n\n".format(self.getName()))
            if result:
                self.info("Missing image(s), task {} will be submit.\n\n".format(self.getName()))
            else:
                self.info("Seem completed, task {} will not be submitted.\n\n".format(self.getName()))
        elif methodName == "meetRequirement":
            if result:
                self.info("All requirements met prior to submit task {}\n\n".format(self.getName()))
            else:
                self.error("Some mandatory image are missing. Finishing the pipeline now\n\n")
        elif methodName == "implement":
            self.info("Finish task {} at {}.".format(self.getName(), self.getTimestamp()))
            self.info("-------------------------------------------------------------------------\n")

    def __log(self, message, level):
        """Write a user friendly message into the console and into the log file

        Args:
            message: the message to write
            level:  the level of severity of the message: DEBUG, INFO, WARNING, ERROR etc..

        Returns:
            the execution status if the level is unknown

        """
        if level not in ['INFO','WARNING','DEBUG','ERROR']:
            return False

        if isinstance(message, tuple) and len(message) == 3:
            message = self.__commandFormatter(message)

        else:
            message = "{}: {}\n".format(level, message)

        print message
        if self.__logIntoFile:
            with open(self.filename,'a') as f:
                f.write(message)

    def info(self, message):
        """Wrapper for  user friendly message that have info level

        Args:
            message: the message to write

        """
        self.__log(message, 'INFO')

    def debug(self, message, pause = False):
        """Wrapper for user friendly message that have debug level

        Args:
            message: the message to write
            pause: Stop pipeline and ask user to hit RETURN to continue
        """
        self.__log(message, 'DEBUG')
        if pause:
            util.rawInput("Press Enter to continue...")

    def warning(self, message, pause = False):
        """Wrapper for user friendly message that have warning level

        Args:
            message: the message to write
            pause: Stop pipeline and ask user to hit RETURN to continue
        """
        self.__log(message, 'WARNING')
        if pause:
            util.rawInput("Press Enter to continue...")

    def error(self, message):
        """Wrapper for user friendly message that have warning level

        Args:
            message: the message to write

        """
        self.__log(message, 'ERROR')
        sys.exit()

    def quit(self, message = None):
        """Wrapper for user friendly message that have info level and quit the pipeline silently

        Args:
            message: the message to write

        """
        if message is not None:
            self.__log(message, 'INFO')
        sys.exit()

    def getLogger(self):
        """Return that class instance

        Returns:
            this class instance

        """
        return self

    def getLogFileName(self):
        """Return the filename of the log file

        Returns:
            Return the filename of the log file

        """
        return self.filename

    def closeLog(self, handle):
        """Close the handle of the file

        Args:
            handle: the handle of the log file

        """
        handle.close()

    def __rotateLog(self, source, target):
        """Archive the contain of a source file into the beginning of a target file

        Args:
            source: a source file name
            target: a target file name

        """
        if os.path.isfile(source):
            with open(source, 'r') as f:
                logText = f.read()
                if os.path.isfile(target):
                    with open(target, 'r+') as a:
                        contain = a.read()
                        a.seek(0, 0)
                        a.write(logText+contain)
                else:
                    with open(target, 'w') as w:
                        w.write(logText)

    def __commandFormatter(self, (cmd, output, error)):
        """Format a 3 elements tuples representing the command execute, the standards output and the standard error
        message into a convenient string

        Args:
            message: A 3 elements tuples

        Returns:
            A string
        """
        binary = cmd.split(" ")[0]
        message = "Launch {} command line...".format(binary)
        message +="Command line submit: {}".format(cmd)

        if not (output is "" or output is "None" or output is None):
            message +="Output produce by {}: {} \n".format(binary, output)

        if not (error is '' or error is "None" or error is None):
             message +="Error produce by {}: {}\n".format(binary, error)
        self.info("------------------------\n")
        return message

