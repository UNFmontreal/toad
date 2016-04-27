# -*- coding: utf-8 -*-
import os
import sys
import glob
import ConfigParser

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
from lib import util
from core.toadinfo.toadinfo import Toadinfo

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class Converter(object):

    def __init__(self, arguments):
        self.__arguments = arguments
        self.__configParser = ConfigParser.ConfigParser()
        self.__configFilename = None

    def __buildFilename(self, target, prefixValue, sessionName, extension = ".nii.gz"):
        return "'{}/{}{}{}'".format(target, prefixValue, sessionName, extension)

    def convert(self, session):
        """Single entry point to convert any mri sequences

        """
        target = os.path.join(self.__arguments.dirName, session.getName())
        if not os.path.exists(target):
            os.makedirs(target)

        sequences = session.getSequences()
        if not self.__arguments.noConfig:
            self.__initializeConfigFile(sequences, target)

        for sequence in session.getSequences():

            name = sequence.getPrefix().getName()
            if name == 'dwi':
                self.__convertDwi(sequence, session, target)
            elif name == 'mag':
                self.__convertMagnitude(sequence, session, target)
            else:
                self.__convert(sequence, session, target)

    def __convert(self, sequence, session, target):
        filename = util.buildName(self.__configParser, target, sequence.getPrefix().getValue(), session.getName(), 'nii.gz')

        cmd = "mrconvert {0} {1} -force ".format(sequence.getEscapedDirectory(), filename)
        if not self.__arguments.noStride:
            cmd += " -stride 1,2,3 "

        if sequence.getPrefix().getName() == 'phase':
            cmd += " -datatype float32 "
        print cmd
        util.launchCommand(cmd)

        if not self.__arguments.noConfig:
            dicoms = glob.glob("{}/*.dcm".format(sequence.getDirectory()))
            if len(dicoms) > 0:
                toadinfo = Toadinfo(dicoms.pop())
                print 'Write convert'
                toadinfo.writeToadConfig(self.__configFilename)

    def __convertDwi(self, sequence, session, target):
        """ Convert a dwi dicom images into nifti

        the name of the resulting image will be:
            prefix_subjectName.nii.gz

        """
        dwi = util.buildName(self.__configParser, target, sequence.getPrefix().getValue(), session.getName(),'nii.gz')
        bEnc = util.buildName(self.__configParser, target, dwi, None, "b")
        bvals = util.buildName(self.__configParser, target, dwi, None, "bvals")
        bvecs = util.buildName(self.__configParser, target, dwi, None, "bvecs")

        cmd = "mrconvert {} {} -force -export_grad_mrtrix {} -export_grad_fsl {} {}"\
            .format(sequence.getEscapedDirectory(), dwi, bEnc, bvecs, bvals)

        if not self.__arguments.noStride:
            cmd += " -stride 1,2,3,4 "
        print cmd
        util.launchCommand(cmd)

        if not self.__arguments.noConfig:
            dicoms = glob.glob("{}/*.dcm".format(sequence.getDirectory()))
            if len(dicoms) > 0:
                toadinfo = Toadinfo(dicoms.pop())
                print 'Write convert dwi'
                toadinfo.writeToadConfig( self.__configFilename)

    def __convertMagnitude(self, sequence, session, target):
        """ Convert a magnitude fieldmap dicom images into nifti

        the name of the resulting image will be:
            prefix_subjectName.nii.gz


        """
        def __setMagnitudeFieldmapInConfigFiles(echo1, echo2):
            """ write magnitude image properties into a config file

            Args:
                configFile: a config file
                echo1: the echo time of the first magnitude map
                echo2: the echo time of the secong magnitude map
            """
            if os.path.exists(self.__configFilename):
                self.__configParser.read(self.__configFilename)
            if not self.__configParser.has_section("correction"):
                self.__configParser.add_section('correction')
            self.__configParser.set('correction', "echo_time_mag1", echo1)
            self.__configParser.set('correction', "echo_time_mag2", echo2)
            with open(self.__configFilename,'w') as w:
                self.__configParser.write(w)

        values = []
        pattern = os.path.join(session.getDirectory(), os.path.dirname(sequence.getName()),'echo_*')
        for directory in glob.glob(pattern):
            values.append((os.path.basename(directory).strip('echo_'), directory))
        try:
            echo1 = float(values[0][0])
            echo2 = float(values[1][0])

            if not self.__arguments.noConfig:
                if echo1 > echo2:
                    __setMagnitudeFieldmapInConfigFiles(echo2, echo1)
                else:
                    __setMagnitudeFieldmapInConfigFiles(echo1, echo2)

        except IndexError:
            return

        filename = util.buildName(self.__configParser, target, sequence.getPrefix().getValue(), session.getName(), 'nii.gz')
        cmd = "mrconvert {0} {1} -force ".format(sequence.getEscapedDirectory(), filename)
        if not self.__arguments.noStride:
            cmd += " -stride 1,2,3 "
        print cmd
        util.launchCommand(cmd)

    def __initializeConfigFile(self, sequences, target):

        if not self.__arguments.noConfig:
            self.__configFilename = os.path.join(target, "config.cfg")
            if not self.__configParser.has_section('prefix'):
                self.__configParser.add_section('prefix')

        for sequence in sequences:
            name = sequence.getPrefix().getName()
            value = sequence.getPrefix().getValue()
            self.__configParser.set('prefix', name,  value)
            if name == 'dwi':
                self.__configParser.set('prefix', 'grad',  value)

        with open(self.__configFilename, 'a') as a:
            self.__configParser.write(a)
