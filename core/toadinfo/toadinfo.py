# -*- coding: utf-8 -*-
import os
import sys
import ConfigParser

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
from core.dicom.dicom import Dicom
__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class Toadinfo(Dicom):

    def __init__(self, filename):
        Dicom.__init__(self, filename)

    def __repr__(self):

        msg = ""
        if self.isSiemens():
            phaseEncodingDirection = self.getPhaseEncodingDirection()
            phase = ["P>>A", " A>>P", "R>>L", "L>>R"]
            msg +="\tPhase encoding: {}, {}\n".format(phaseEncodingDirection, phase[phaseEncodingDirection])

            epiFactor = self.getEpiFactor()
            if epiFactor is not None:
                msg +="\tEPIFactor: {}\n".format(epiFactor)

        if self.getEchoSpacing() is not None:
            msg +="\tEchoSpacing: {} ms\n".format(self.getEchoSpacing())

        if self.getEchoTime() is not None:
            msg +="\tEchoTime: {} ms\n".format(self.getEchoTime())
        return msg


    def writeToadConfig(self, source):

        config = ConfigParser.ConfigParser(allow_no_value = True)
        if os.path.exists(source):
            config.read(source)

        if self.isSiemens():
            if not config.has_section("denoising"):
                config.add_section("denoising")

            config.set('denoising', 'number_array_coil', self.getNumberArrayCoil())

        if not config.has_section("correction"):
            config.add_section("correction")

        if self.isSiemens():
            phaseEncodingDirection = self.getPhaseEncodingDirection()
            phase = ["posterior to anterior", "anterior to Posterior", "right to left", "left to right"]
            config.set("correction", "#The phase encoding is from {}".format(phase[phaseEncodingDirection]))
            config.set("correction", "phase_enc_dir", phaseEncodingDirection)

            if self.getEpiFactor() is not None:
                config.set("correction", "epi_factor", self.getEpiFactor())

        if self.getEchoSpacing() is not None:
            config.set("correction", "echo_spacing", self.getEchoSpacing())

        if self.getEchoTime() is not None:
            if not config.has_section("correction"):
                config.add_section("correction")
            config.set("correction", "echo_time_dwi", self.getEchoTime())

        with open(source, 'w') as w:
           config.write(w)