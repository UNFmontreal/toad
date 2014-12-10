from lock import Lock
import shutil
import os

__author__ = 'mathieu'

class Subject(Lock):


    def __init__(self, config):
        """A valid individual able to run tasks.

        Must be validated as a prerequisite

        Args:
            config: a self.config ConfigParser object.

        """
        self.__config = config
        self.__subjectDir = self.__config.get('arguments', 'subjectDir')
        self.__name = os.path.basename(self.__subjectDir)
        self.__logDir = os.path.join(self.__subjectDir, self.__config.get('dir', 'log'))
        if not os.path.exists(self.__logDir):
            os.mkdir(self.__logDir)
        Lock.__init__(self, self.__logDir, self.__name)

    def __repr__(self):
	return self.__name	

    def getName(self):
        return self.__name

    def getSubjectDir(self):
        return self.__subjectDir

    def getLogDir(self):
        return self.__logDir


    def removeLogDir(self):
        if os.path.exists(self.__logDir):
            shutil.rmtree(self.__logDir)


    def getConfig(self):
        return self.__config


    def getDir(self):
        return self.__subjectDir
