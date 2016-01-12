#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import shutil
import argparse

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
from core.dicom.dicom import Dicom
from lib import arguments


__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]
__license__ = "GPL v2"
__version__ = "0.1.0"
__maintainer__ = "Mathieu Desrosiers"
__email__ = "mathieu.desrosiers@criugm.qc.ca"
__status__ = "Prototype"


def parseArguments():
    """Prepare and parse user friendly command line arguments for sys.argv.

    Returns:
        a args stucture containing command lines arguments
    """
    parser = arguments.Parser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description ="""\n
         """)
    parser.add_argument("source", help="A SIEMENS DICOM imges root directory")
    parser.add_argument("target", help="the target directory")
    parser.add_argument('-v', '--version', action='version', version="%(prog)s ({})".format(__version__))
    args = parser.parse_args()
    return args

class Reshuffler(object):
    def __init__(self, source):
        self.__source = source
        self.__sessions = {}
        self.__initialized()


    def __initialized(self):
        for root, directories, filenames in os.walk(self.__source):
            for filename in filenames:
                dcm = Dicom(os.path.join(root, filename))
                if dcm.isDicom():
                    self.__appendDicom(dcm)

    def __appendDicom(self, dicom):
        sessionName = dicom.getSessionName()
        if self.__sessions.has_key(sessionName):
            session = self.__sessions[sessionName]
        else:
            session = Session(dicom.getSessionName())
        session.appendDicom(dicom)
        self.__sessions[sessionName] = session

    def convert(self, target):
        for sessionName, session in self.__sessions.iteritems():
            for sequenceName, sequence in session.getSequences().iteritems():
                for dicom in sequence.getDicoms():
                    dicomFileName = "{}-{:04d}.dcm".format(dicom.getSessionName(), dicom.getInstanceNumber())
                    directory = os.path.join(target, sessionName, sequenceName)
                    if sequence.isMultiEchoes():
                        directory = os.path.join(directory, "echo_{}".format(dicom.getEchoTime()))
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    fullDicomFileName = os.path.join(directory, dicomFileName)
                    shutil.copyfile(dicom.getFileName(), fullDicomFileName)


    def __repr__(self):
        cmd = ""
        for session in self.__sessions:
            cmd += "{}\n".format(session)
        return cmd


class Session(object):
    
    def __init__(self, name):
        self.__name = name
        self.__sequences = {}

    def appendDicom(self, dicom):
        if self.__sequences.has_key(dicom.getSequenceName()):
            sequence = self.__sequences[dicom.getSequenceName()]
        else:
            sequence = Sequence(dicom.getSequenceName())
        sequence.append(dicom)
        self.__sequences[dicom.getSequenceName()] = sequence

    def getName(self):
        return self.__name

    def getSequences(self):
        return self.__sequences

    def __repr__(self):
        cmd = ""
        for sequence in self.__sequences:
            cmd += "{}\n".format(sequence)
        return cmd


class Sequence(object):
    
    def __init__(self, name):
        self.__name = name
        self.__dicoms = []
        self.__echoes = []

    def getName(self):
        return self.__name

    def isMultiEchoes(self):
        return len(self.__echoes) > 1

    def append(self, dicom):
        if dicom.getEchoTime() not in self.__echoes:
            self.__echoes.append(dicom.getEchoTime())
        self.__dicoms.append(dicom)

    def getDicoms(self):
        return self.__dicoms

    def getEchoTimes(self):
        return self.__echoes

    def __repr__(self):
        cmd = "echoes = "
        cmd += " {},".join(self.__echoes)
        for dicom in self.__dicoms:
            cmd += "{}\n".format(dicom)
        return cmd

if __name__ == '__main__':

    arguments = parseArguments()
    reshuffle = Reshuffler(arguments.source)
    reshuffle.convert(arguments.target)

