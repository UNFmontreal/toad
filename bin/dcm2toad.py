#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import glob
import shutil
import tempfile
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
from lib import arguments, util

class SessionDicom(object):

    def __init__(self):
        self.__directory = None
        self.__singleEchoesDicoms = []
        self.__manyEchoesDicoms = []


    def __init__(self, directory):
        self.__directory = directory


    def shuffleDicom(self):
        tmpDirectory = tempfile.mkdtemp()
        print "tmpDirectory=", tmpDirectory
        cmd = "find {} -name \"*.dcm\"".format(self.__directory)
        results = util.launchCommand(cmd)[1]
        dicoms = results.split()
        for dicom in dicoms:
            shutil.copy(dicom, tmpDirectory)

if __name__ == '__main__':
    print sys.argv[1]
    session = SessionDicom(sys.argv[1])
    session.shuffleDicom()

    """
    def __mapDicomsFiles(self):
        self.__singleEchoesDicoms = glob.glob("{}/*/*.dcm".format(self.__directory))
        self.__manyEchoesDicoms.extend(glob.glob("{}/*/*/*.dcm".format(self.__directory)))


    def __isDirectoryContainDicomSession(self):
        if len(self.__singleEchoesDicoms) > 0:
    """