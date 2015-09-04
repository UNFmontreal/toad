# -*- coding: utf-8 -*-

import os
import glob
import ConfigParser
import sequencemri

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class SessionMRI(object):
    def __init__(self, directoryOrMriSession, archiveName = None):
        if isinstance(directoryOrMriSession, SessionMRI):
            self.__directory = directoryOrMriSession.getDirectory()
            self.__name = directoryOrMriSession.getName()
            self.__archiveName = directoryOrMriSession.getArchiveName()
        else:
            self.__directory = directoryOrMriSession
            self.__name = os.path.basename(self.__directory)
            self.__archiveName = archiveName

        self.__configParser = ConfigParser.ConfigParser()
        self.__checked = False
        self.__sequences = []


    def __eq__(self, other):
        return self.__directory == other.__directory

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        repr = "\nSessionMRI:name={},directory={}".format(self.__name, self.__directory)
        if self.__archiveName is not None:
            repr += ",archiveName={}".format(self.__archiveName)
        if self.__checked:
            repr += ", checked = True"
        repr+= "\n"
        repr += str(self.__sequences)
        return repr

    def isChecked(self):
        return self.__checked

    def setChecked(self, check):
        self.__checked = check

    def getName(self):
        return self.__name

    def setName(self, name):
        self.__name = name

    def getDirectory(self):
        return self.__directory

    def isFromArchive(self):
        return self.__archiveName is not None

    def getArchiveName(self):
        return self.__archiveName

    def getConfigParser(self):
        return self.__configParser

    def getSequences(self):
        return self.__sequences

    def appendSequence(self, sequence):
        self.__sequences.append(sequence)

    def hasPrefix(self, prefix):
        for sequence in  self.__sequences:
            if sequence.getPrefix() == prefix:
                return True
        return False


    #@TODO test for uncombine images
    def isUnfSession(self):
        filesOrDirectorys = os.listdir(self.__directory)
        nbDicoms = 0
        for filesOrDirectory in filesOrDirectorys:
            fullFileName = os.path.join(self.__directory, filesOrDirectory)
            if os.path.isfile(fullFileName):
                return False
            if filesOrDirectory.startswith("echo_"):
                return False
            nbDicoms +=len(glob.glob("{}/*.dcm".format(fullFileName)))
        return nbDicoms > 0


    def initializeMRISequences(self):
        directories = os.listdir(self.__directory)
        for directory in directories:
            fullPath = os.path.join(self.__directory, directory)
            if len(glob.glob("{}/*.dcm".format(fullPath))) > 0:
                self.__sequences.append(sequencemri.SequenceMRI(name = directory , directory = fullPath))
            elif len(glob.glob("{}/echo_*/*.dcm".format(fullPath))) > 0:
                #this is a multi echoes sequence"
                echoesDirectories = os.listdir(fullPath)
                for echoesDirectory in echoesDirectories:
                    fullEchoesPath = os.path.join(fullPath, echoesDirectory)
                    if len(glob.glob("{}/*.dcm".format(fullEchoesPath))) > 0:
                        self.__sequences.append(sequencemri.SequenceMRI(name = os.path.join(directory, echoesDirectory), directory = fullEchoesPath))


    def updatePrefixIntoConfigParser(self):
        """ write images prefix into a config file

        Args:
            configFile: a config file
            prefixs: a structure containing prefixs

        """
        if not self.__configParser.has_section('prefix'):
            self.__configParser.add_section('prefix')

        for sequence in self.getSequences():
            prefix = sequence.getPrefix()
            name = prefix.getName()
            value= prefix.getValue()
            self.__configParser.set('prefix', name, value)