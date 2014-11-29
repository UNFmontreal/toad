import datetime
import sys

__author__ = 'desmat'

class Logger(object):

    #@TODO simplify logname name creation
    def __init__(self, path = None):
        """Provide a simple, custom, logging capability for the toad pipeline.

        The purpose of this class is to provide a simple, custom, logging capability for the toad
        pipeline. Thanks to late nipype who were reset the configuration before each call.

        Args
            path: the folder where the log file should be created

        """
        if path is None:
            self.__logIntoFile = False
        else:
            self.__logIntoFile = True
            self.filename = "%s/%s.log"%(path, self.getName())
            self.handle = open(self.filename,'a')
            self.handle.write("#########################################################################\n")
            self.handle.write("\n")
            self.handle.write(" Start logging task %s at %s"%(self.getName(), self.__timestamp()))
            self.handle.write("\n")
            self.handle.write("\n")
            self.handle.write("#########################################################################\n")
            self.handle.close()


    def __timestamp(self):
        """Return the current time and date formated as %Y%m%d %Hh%M

        example if the current time is  9:41 the  14 october 2014, the timestamp will
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
            self.info("Looking if task %s need to be submit"%self.getName())
        elif methodName == "meetRequirement":
            self.info("Looking if all requirement are met prior submitting the task %s."%self.getName())
        elif methodName == "implement":
            self.info("Starting task %s at %s."%(self.getName(), self.__timestamp()))


    def logFooter(self, methodName, result=False):
        """Format and write a user friendly footer message into the log file

        Args:
            methodName: the name of method that call this function
                        valid values are: isDirty, meetRequirement, implement
            result: the status return by the command specify by methodName

        """
        if methodName == "isDirty":
            if result == None:
                self.info("Ignoring flag activate, task %s will be skipped.\n\n"%self.getName())
            if result == True:
                self.info("Missing image(s), task %s will be submit.\n\n"%self.getName())
            else:
                self.info("Seem completed, task %s will not be submitted.\n\n"%self.getName())
        elif methodName == "meetRequirement":
            if result == True:
                self.info("All requirements met prior to submit task %s\n\n"%self.getName())
            else:
                self.error("Some mandatory image are missing. Finishing the pipeline now\n\n")
        elif methodName == "implement":
            self.info("Finish task %s at %s."%(self.getName(), self.__timestamp()))
            self.info("-------------------------------------------------------------------------")


    def __log(self, message, level):
        """Write a user friendly message into the console and into the log file

        Args:
            message: the message to write
            level:  the level of severity of the message: DEBUG, INFO, WARNING, ERROR etc..

        Returns:
            the execution status if the level is unknown

        """
        if level not in ['INFO','WARNING','ERROR']:
            return False

        message = "%s: %s\n"%(level, message)
        print message
        if self.__logIntoFile:
            self.handle = open(self.filename,'a')
            self.handle.write(message)
            self.handle.close()

        if level == 'ERROR':
            sys.exit()


    def info(self, message):
        """Wrapper for  user friendly message that have info level

        Args:
            message: the message to write

        """
        self.__log(message, 'INFO')


    def warning(self, message):
        """Wrapper for user friendly message that have warning level

        Args:
            message: the message to write

        """
        self.__log(message, 'WARNING')


    def error(self, message):
        """Wrapper for user friendly message that have warning level

        Args:
            message: the message to write

        """
        self.__log(message, 'ERROR')


    def getLogger(self):
        """Return that class instance

        Returns:
            this class instance

        """
        return self


    def getLogFileName(self):
        return self.filename


    def getLog(self):
        return open(self.filename,'a')


    def closeLog(self, handle):
        handle.close()
