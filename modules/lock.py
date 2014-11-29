import os

__author__ = 'mathieu'

class Lock(object):


    def __init__(self, logDir, name):
        """Simple lock mechanism for the toad pipeline

        The purpose of this class is to provide simple mechanism to avoid collusion
        between many concurrent execution of toad pipeline.

        Args:
            log_dir: the directory where the lock file will be store
            name: the name of the subject

        """
        self.__name = name
        self.__logDir = logDir
        self.__lockFile = "{}/{}.lock".format(logDir, name)


    def isLock(self):
        """Lock if this subject is currently running into an instance of a toad pipeline

        Returns:
            a Boolean

        """
        if os.path.exists(self.__lockFile):
            return True
        return False


    def lock(self):
        """Create a Lock for the subject that is currently running into this toad pipeline

        Returns:
            the lock filename

        """
        if self.isLock():
            return False
        open(self.__lockFile, 'a').close()
        return self.__lockFile


    def removeLock(self):
        """Remove the subject lock file

        Returns:
            the status of the operation

        """
        if not self.isLock():
            return False
        os.remove(self.__lockFile)
        return True


    def getLock(self):
        """return the lock file name if it exists

        Returns:
            if the subject is lock return the lock file name, return False otherwise
        """
        if self.isLock():
            return self.__lockFile
        return False

