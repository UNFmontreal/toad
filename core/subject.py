from core.validation import Validation
from core.logger import Logger
from xml.parsers.expat import ExpatError
from xml.dom import minidom
from lock import Lock
import shutil
import os

__author__ = 'mathieu'

class Subject(Logger, Lock, Validation):


    def __init__(self, config):
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
        #the subject logger must be call without file information during initialization
        Logger.__init__(self)
        Lock.__init__(self, self.__logDir, self.__name)
        Validation.__init__(self, self.__subjectDir, self.__config)


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
    
    def activateLogDir(self):
        """ create the log directory and create the versions.xml file
            The log dir should be avtivate only if this object is tested as a valid toad subjects
            See Valifation.isAToadSubject()

        """
        if not os.path.exists(self.__logDir):
            self.info("creating log dir {}".format(self.__logDir))
            os.mkdir(self.__logDir)
        Logger.__init__(self, self.__logDir)


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


    def createXmlSoftwareVersionConfig(self, xmlDocument):
        """ Write software versions into a source filename

        Args:
            xmlDocument: a minidom document
            source: file name to write configuration into

        Returns:
            True if the operation is a success, False otherwise
        """
        versionFile = os.path.join(self.getLogDir(), self.__config.get('general', 'versions_file_name'))
        if os.path.exists(versionFile):
            try:
                xml = minidom.parse(versionFile)
                if len(xml.getElementsByTagName("toad")) == 1:
                    if len(xmlDocument.getElementsByTagName("application")) != 1:
                        self.warning("none or too many tag name application into the software version structure")
                        return False
                    xmlToad = xml.getElementsByTagName("toad")[0]
                    xmlDocumentToad = xmlDocument.getElementsByTagName("application")[0]
                    xmlToad.appendChild(xmlDocumentToad)
                    xmlDocument = xmlToad
            except ExpatError:
                self.warning('Cannot understand {} xml structure, I will overwrite it?'.format(versionFile))

        with open(versionFile, 'w') as w:
            xmlDocument.writexml(w)
        return True
