# -*- coding: utf-8 -*-

import os
import ConfigParser
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from core.dicomparser.dicomparser import DicomParser
__author__ = "Mathieu Desrosiers, Arnaud Bore"
__copyright__ = "Copyright (C) 2016, TOAD"
__credits__ = ["Mathieu Desrosiers", "Arnaud Bore"]


class Toadinfo(DicomParser):

    def __init__(self, filename):
        DicomParser.__init__(self, filename)

    def __repr__(self): # Need to be re-written

        msg = ""
        msg_error = ""
        if self.isSiemens():

            if self.getPhaseEncodingDirection() is not None:
                phaseEncodingDirection = self.getPhaseEncodingDirection() # Set Phase encoding direction
                phase = ["P>>A", " A>>P", "R>>L", "L>>R"]
                msg += "\tPhase encoding: {}, {}\n".format(phaseEncodingDirection, phase[phaseEncodingDirection])
            else:
                msg += "\tPhase encoding has not been correctly set\n"

            if self.getEpiFactor() is not None: # Set epiFactor
                msg += "\tEPIFactor: {}\n".format(self.getEpiFactor())
            else:
                msg += "\tEPIFactor has not been correctly set\n"

        if self.getEchoSpacing() is not None:  # Set Echo Spacing
            msg += "\tEchoSpacing: {} ms\n".format(self.getEchoSpacing())
        else:
            msg += "\tEchoSpacing has not been correctly set\n".format(self.getEchoSpacing())

        if self.getEchoTime() is not None:  # Set Echo Time
            msg += "\tEchoTime: {} ms\n".format(self.getEchoTime())
        else:
            msg += "\tEchoTime has not been correctly set\n".format(self.getEchoTime())

        return msg

    def writeToadConfig(self, source):

        config = ConfigParser.ConfigParser()
        if os.path.exists(source):
            config.read(source)

        if not config.has_section("methodology"):  # Add information: Methodology
            config.add_section("methodology")

        config.set('methodology', 'manufacturer', self.getManufacturer())
        config.set('methodology', 'magneticfieldstrength', self.getMagneticFieldStrength())
        config.set('methodology', 'mrmodel', self.getMRModel())

        if self.getSequenceName() == 'Diffusion':  # Save information about diffusion
            config.set('methodology', 'dwi_tr', self.getRepetitionTime())
            config.set('methodology', 'dwi_te', self.getEchoTime())
            config.set('methodology', 'dwi_flipangle', self.getFlipAngle())
            config.set('methodology', 'dwi_voxelsize', self.getVoxelSize())
            config.set('methodology', 'dwi_matrixsize', self.getMatrixSize())
            config.set('methodology', 'dwi_numberslices', self.getNumberSlices())
            config.set('methodology', 'dwi_fov', self.getFOV())
            config.set('methodology', 'dwi_studyUID', self.getStudyUID())

            if not config.has_section("correction"):  # Add information about correction step
                config.add_section("correction")

            if self.getEchoSpacing() is not None:  # Add information about echo spacing if not None
                config.set("correction", "echo_spacing", self.getEchoSpacing())
            else:
                config.set("correction", "#Echo spacing has not been found", )
                config.set("correction", "#echo_spacing")

            if not config.has_section("denoising"):  # Add information about denoising
                config.add_section("denoising")

            if self.getNumberArrayCoil() is not 0:
                config.set('denoising', 'number_array_coil', self.getNumberArrayCoil())
            else:
                config.set('denoising', '#Number_array_coil has not been found', '')
                config.set('denoising', '#number_array_coil')

        elif self.getSequenceName() == 'Structural T1':  # Save information about anatomic T1
            config.set('methodology', 't1_tr', self.getRepetitionTime())
            config.set('methodology', 't1_te', self.getEchoTime())
            config.set('methodology', 't1_ti', self.getInversionTime())
            config.set('methodology', 't1_flipangle', self.getFlipAngle())
            config.set('methodology', 't1_voxelsize', self.getVoxelSize())
            config.set('methodology', 't1_matrixsize', self.getMatrixSize())
            config.set('methodology', 't1_numberslices', self.getNumberSlices())
            config.set('methodology', 't1_fov', self.getFOV())
            config.set('methodology', 't1_studyUID', self.getStudyUID())

        # If Siemens add information about number of coils
        if self.isSiemens() and self.getSequenceName() == 'Diffusion':

            config.set('methodology', 'dwi_bValue', self.getbValue())  # B Value
            config.set('methodology', 'dwi_numDirections', self.getNumberDirections())  # Num Directions
            config.set('methodology', 'dwi_patfactor', self.getPatFactor())

            if not config.has_section("correction"):  # Add information about correction step
                config.add_section("correction")
            else:
                if self.getPhaseEncodingDirection() is not None:
                    phaseEncodingDirection = self.getPhaseEncodingDirection()
                    phase = ["posterior to anterior", "anterior to Posterior", "right to left", "left to right"]
                    config.set("correction", "#The phase encoding is from {}".format(phase[phaseEncodingDirection]))
                    config.set("correction", "phase_enc_dir", phaseEncodingDirection)
                else:
                    config.set("correction", "#The phase encoding has not been found", '')
                    config.set("correction", "#phase_enc_dir")

                if self.getEpiFactor() is not None:
                    config.set("correction", "epi_factor", self.getEpiFactor())
                else:
                    config.set("correction", "#The EPI factor has not been found", '')
                    config.set("correction", "#epi_factor")

        #  Set intersession option
        if config.has_option('methodology', 't1_studyUID') and config.has_option('methodology', 'dwi_studyUID'):
            if config.get('methodology','t1_studyUID') == config.get('methodology','dwi_studyUID'):
                config.set('methodology', 'intrasession', True)
            else:
                config.set('methodology', 'intrasession', False)

        with open(source, 'w') as w:
            config.write(w)
