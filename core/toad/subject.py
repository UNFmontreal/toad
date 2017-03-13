# -*- coding: utf-8 -*-
import shutil
import os
import xml.dom.minidom
import ConfigParser
import StringIO

from core.toad.validation import Validation
from logger import Logger
from lib import xmlhelper
from lock import Lock
__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


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

    def createXmlSoftwareVersionConfig(self, xmlSoftwaresTags):
        """ Write software versions into a source filename

        Args:
            xmlDocument: a minidom document
            source: file name to write configuration into

        Returns:
            True if the operation is a success, False otherwise
        """
        xmlFilename = os.path.join(self.getLogDir(), self.__config.get('general', 'versions_file_name'))
        xmlToadTag = xmlhelper.createOrParseXmlDocument(xmlFilename)
        xmlToadTag.appendChild(xmlhelper.createApplicationTags(xmlSoftwaresTags))
        with open(xmlFilename, 'w') as w:
            xmlToadTag.writexml(w)
        return True

    def writeConfigRunning(self, target):
        # Create a deep copy of the configuration object
        #http://stackoverflow.com/questions/23416370/manually-building-a-deep-copy-of-a-configparser-in-python-2-7
        config_string = StringIO.StringIO()
        self.__config.write(config_string)

        # We must reset the buffer to make it ready for reading.
        config_string.seek(0)
        config_running = ConfigParser.ConfigParser()
        config_running.readfp(config_string)

        # Remove "ignore" options in each sections
        for section in config_running.sections():
            for name, value in config_running.items(section):
                if name == "ignore":
                    config_running.remove_option(section, "ignore")
                    print "remove ignore for {}".format(section)

        # Remove "arguments" section
        if "arguments" in config_running.sections():
            config_running.remove_section("arguments")
            print "remove arguments"

        configRunning = open(target, 'w')
        config_running.write(configRunning)
        configRunning.close()

