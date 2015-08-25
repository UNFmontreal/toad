from lock import Lock
from validation import Validation
import shutil
import os

__author__ = 'mathieu'

class Subject(Lock, Validation):


    def __init__(self, config, softwareVersions):
        """A valid individual who have the capability to run tasks.
            This class have the responsability to write a document of the softwares and versions
            into the log directory

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
        self.__createSoftwareVersionXmlConfig(softwareVersions)

    def __repr__(self):
        return self.__name


    def getName(self):
        """get the name of that instance

        Returns
            the name of that instance

        """
        return self.__name


    def getLogDir(self):
        """get the name of the log directory

        Returns
            the name of the log directory

        """
        return self.__logDir


    def removeLogDir(self):
        """Utility function that delete the subject log directory

        """
        if os.path.exists(self.__logDir):
            shutil.rmtree(self.__logDir)


    def getConfig(self):
        """Utility function that return the ConfigParser 

        Returns
            the ConfigParser
        """
        return self.__config


    def setConfigItem(self, section, item, value):
        """Utility function that register a value into the config parser

        Returns
            the ConfigParser
        """
        self.__config.set(section, item, value)


    def getDir(self):
        """get the name of the subject directory

        Returns
            the name of the subject directory

        """
        return self.__subjectDir


    def __createSoftwareVersionXmlConfig(self, xmlDocument,  source = 'version.xml'):
        """ wrote software versions into a source filename

        Args:
            xmlDocument: a minidom document
            source: file name to write configuration into
        """
        with open(os.path.join(self.getLogDir(), source), 'a') as a:
            xmlDocument.writexml(a)