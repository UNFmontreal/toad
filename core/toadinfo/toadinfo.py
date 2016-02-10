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

    def __repr__(self): # Need to be re-written

        msg = ""
        msg_error = ""
        if self.isSiemens():

            if self.getPhaseEncodingDirection() is not None:
                phaseEncodingDirection =  self.getPhaseEncodingDirection() # Set Phase encoding direction
                phase = ["P>>A", " A>>P", "R>>L", "L>>R"]
                msg +="\tPhase encoding: {}, {}\n".format(phaseEncodingDirection, phase[phaseEncodingDirection])
            else:
                msg += "\t Phase encoding has not been correctly set\n"

            if self.getEpiFactor() is not None: # Set epiFactor
                msg +="\tEPIFactor: {}\n".format(self.getEpiFactor())
            else:
                msg += "\t EPIFactor has not been correctly set\n"

        if self.getEchoSpacing() is not None:  # Set Echo Spacing
            msg +="\tEchoSpacing: {} ms\n".format(self.getEchoSpacing())
        else:
            msg +="\tEchoSpacing has not been correctly set\n".format(self.getEchoSpacing())

        if self.getEchoTime() is not None:  # Set Echo Time
            msg +="\tEchoTime: {} ms\n".format(self.getEchoTime())
        else:
            msg +="\tEchoTime has not been correctly set\n".format(self.getEchoTime())

        return msg


    def writeToadConfig(self, source):

        config = ConfigParser.ConfigParser(allow_no_value = True)
        if os.path.exists(source):
            config.read(source)

        if self.isSiemens():
            if not config.has_section("denoising"):
                config.add_section("denoising")

            if self.getNumberArrayCoil() is not None:
                config.set('denoising', 'number_array_coil', self.getNumberArrayCoil())
            else:
                config.set('denoising', '#Number_array_coil has not been found')
                config.set('denoising', '#number_array_coil =')

        if not config.has_section("correction"):
            config.add_section("correction")

        if self.isSiemens():
            if self.getPhaseEncodingDirection() is not None:
                phaseEncodingDirection = self.getPhaseEncodingDirection()
                phase = ["posterior to anterior", "anterior to Posterior", "right to left", "left to right"]
                config.set("correction", "#The phase encoding is from {}".format(phase[phaseEncodingDirection]))
                config.set("correction", "phase_enc_dir", phaseEncodingDirection)
            else:
                config.set("correction", "#The phase encoding has not been found")
                config.set("correction", "#phase_enc_dir =")

            if self.getEpiFactor() is not None:
                config.set("correction", "epi_factor", self.getEpiFactor())
            else:
                config.set("correction", "#The EPI factor has not been found")
                config.set("correction", "#epi_factor =")

        if self.getEchoSpacing() is not None:
            config.set("correction", "echo_spacing", self.getEchoSpacing())
        else:
            config.set("correction", "#Echo spacing has not been found",)
            config.set("correction", "#echo_spacing =")

        if self.getEchoTime() is not None:
            if not config.has_section("correction"):
                config.add_section("correction")
            config.set("correction", "echo_time_dwi", self.getEchoTime())
        else:
            config.set("correction", "Echo time dwi has not been found")
            config.set("correction", "echo_time_dwi =")

        with open(source, 'w') as w:
           config.write(w)