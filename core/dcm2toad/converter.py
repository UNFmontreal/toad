# -*- coding: utf-8 -*-
import os
import sys
import glob

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
from lib import util

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class Converter(object):

    def __init__(self, arguments, outputDirectory="toad_data"):
        self.__outputDirectory = outputDirectory
        self.__arguments = arguments
        self.__configFilename = None


    def convert(self, session):
        target = os.path.join(self.__outputDirectory, session.getName())
        if not os.path.exists(target):
            os.makedirs(target)

        if not self.__arguments.noConfig:
            self.__configFilename = os.path.join(target, "config.cfg")
            with open(self.__configFilename, 'w') as w:
                session.getConfigParser().write(w)

        for sequence in session.getSequences():
            if sequence.getPrefix().getName() == 'dwi':
                self.__convertDwi(sequence, session, target)
            elif sequence.getPrefix().getName() == 'mag':
                self.__convertMagnitude(sequence, session, target)
            else:
                self.__convert(sequence, session, target)


    def __convert(self, sequence, session, target):
        filename = "{}/{}{}".format(target, sequence.getPrefix().getValue(), session.getName())
        cmd = "mrconvert {0} {1}.nii.gz -force ".format(sequence.getDirectory(), filename)
        if not self.__arguments.noStride:
            cmd += " -stride 1,2,3 "

        if type == 'phase':
            cmd += " -datatype float32 "
        print cmd
        util.launchCommand(cmd)


    def __convertDwi(self, sequence, session, target):
        """ Convert a dwi dicom images into nifti

        the name of the resulting image will be:
            prefix_subjectName.nii.gz

        """
        filename = "{}/{}{}".format(target, sequence.getPrefix().getValue(), session.getName())
        cmd = "mrconvert {0} {1}.nii.gz -force -export_grad_mrtrix {1}.b -export_grad_fsl {1}.bvecs {1}.bvals"\
            .format(sequence.getDirectory(), filename)
        if not self.__arguments.noStride:
            cmd += " -stride 1,2,3,4 "
        print cmd
        util.launchCommand(cmd)

        if not self.__arguments.noConfig:
            dicoms = glob.glob("{}/*.dcm".format(sequence.getDirectory()))
            if len(dicoms) > 0:
                cmd = "toadinfo {} -c {}".format(dicoms.pop(), self.__configFilename)
                if self.__arguments.fieldmap:
                    cmd += " --fieldmap "
                print cmd
                util.launchCommand(cmd)


    def __convertMagnitude(self, sequence, session, target):
        """ Convert a magnitude fieldmap dicom images into nifti

        the name of the resulting image will be:
            prefix_subjectName.nii.gz


        """
        """
        configFile = os.path.join(target, self.__configFilename)
        values = []
        for directory in glob.glob("{}/echo*".format(os.path.dirname(sequence.path))):
            values.append((os.path.basename(directory).strip('echo_'), directory))
        try:
            echo1 = float(values[0][0])
            echo2 = float(values[1][0])

            if echo1 > echo2:
                source = values[0][1]
                if not self.__arguments.noConfig:
                    self.__setMagnitudeFieldmapInConfigFiles(configFile, echo2, echo1)
            else:
                source = values[1][1]
                if not self.__arguments.noConfig:
                    self.__setMagnitudeFieldmapInConfigFiles(configFile, echo1, echo2)

        except IndexError:
            return
        """
        filename = "{}/{}{}".format(target, sequence.getPrefix().getValue(), session.getName())
        cmd = "mrconvert {0} {1}.nii.gz -force ".format(sequence.getDirectory(), filename)
        if not self.__arguments.noStride:
            cmd += " -stride 1,2,3 "
        print cmd
        util.launchCommand(cmd)