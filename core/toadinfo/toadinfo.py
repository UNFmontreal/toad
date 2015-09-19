# -*- coding: utf-8 -*-
import os
import sys
import ConfigParser

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
from pydicom.filereader import read_file
from pydicom.tag import Tag
from ascconv import Ascconv

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]

manufacturers = ['Philips', 'GE', 'SIEMENS']

class Toadinfo(object):



    def __init__(self, filename):
        self.__fileName = filename
        self.__echoTime = None
        self.__bandwidthPerPixelPhaseEncode = None
        self.__siemensHeader = None
        self.__manufacturer = None
        self.__initialize()

    def __repr__(self):
        phaseEncodingDirection = self.__siemensHeader.getPhaseEncodingDirection()
        phase = ["P>>A", " A>>P", "R>>L", "L>>R"]
        msg = "\tPhase encoding: {}, {}\n".format(phaseEncodingDirection, phase[phaseEncodingDirection])

        epiFactor = self.__siemensHeader.getEpiFactor()
        if epiFactor is not None:
            msg +="\tEPIFactor: {}\n".format(epiFactor)

        if self.getEchoSpacing() is not None:
            msg +="\tEchoSpacing: {} ms\n".format(self.getEchoSpacing())

        if self.__echoTime is not None:
            msg +="\tEchoTime: {} ms\n".format(self.__echoTime)
        return msg

    def __initialize(self):

        dicomHeader = read_file(self.__fileName,
                                    defer_size=None,
                                    stop_before_pixels=True,
                                    toad=True)

        if 'Manufacturer' in dicomHeader:
            for manufacturer in manufacturers:
                if manufacturer in dicomHeader.Manufacturer:
                    self.__manufacturer = manufacturer

        bandwidthPerPixelPhaseEncodeTag = Tag((0x0019, 0x1028))
        if dicomHeader.has_key(bandwidthPerPixelPhaseEncodeTag):
            self.__bandwidthPerPixelPhaseEncode = float(dicomHeader[bandwidthPerPixelPhaseEncodeTag].value)

        if 'EchoTime' in dicomHeader:
            self.__echoTime = float(dicomHeader.EchoTime)

        self.__siemensHeader = Ascconv(self.__fileName)


    def getSiemensHeader(self):
        return self.__siemensHeader


    def getEchoTime(self):
        return self.__echoTime

    def getEchoSpacing(self):

        try:
            echoSpacing = 1/(self.__bandwidthPerPixelPhaseEncode* self.__siemensHeader.getEpiFactor()) *1000.0 * \
                          self.__siemensHeader.getPatFactor() * self.__siemensHeader.getPhaseResolution() * \
                          self.__siemensHeader.getPhaseOversampling()
        except (KeyError, IndexError, TypeError):
            return None
        return echoSpacing


    def writeToadConfig(self, source):

        config = ConfigParser.ConfigParser(allow_no_value = True)
        if os.path.exists(source):
            config.read(source)

        if not config.has_section("denoising"):
            config.add_section("denoising")

        config.set('denoising', 'number_array_coil', self.__siemensHeader.getNumberArrayCoil())

        if not config.has_section("correction"):
            config.add_section("correction")

        phaseEncodingDirection = self.__siemensHeader.getPhaseEncodingDirection()
        phase = ["posterior to anterior", "anterior to Posterior", "right to left", "left to right"]
        config.set("correction", "#The phase encoding is from {}".format(phase[phaseEncodingDirection]))
        config.set("correction", "phase_enc_dir", phaseEncodingDirection)

        if self.__siemensHeader.getEpiFactor() is not None:
            config.set("correction", "epi_factor", self.__siemensHeader.getEpiFactor())

        if self.getEchoSpacing() is not None:
            config.set("correction", "echo_spacing", self.getEchoSpacing())

        if self.getEchoTime() is not None:
            if not config.has_section("correction"):
                config.add_section("correction")
            config.set("correction", "echo_time_dwi", self.getEchoTime())

        with open(source, 'w') as w:
           config.write(w)