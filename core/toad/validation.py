# -*- coding: utf-8 -*-
import os
from lib import mriutil, util

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class Validation(object):


    def __init__(self, workingDir, config):
        """Class which is primary goal is to determine if a toad subject is valid

        Validate all files and images into subject subdirectory and determine if that subject is valid
        Valid structure should contain:
            A High resolution image
            A diffusion tensor image
            A gradient encoding file, optionnaly in bvals, bvecs format
            Optionnaly, B0_Anterior-Posterior and/or B0_Posterior-Anterior image
            Optionnal aparc_aseg, freesurfer_anat
            only one T1,dwi, .b per subject

        the task name 00-backup is a hardcoded and cannot be changed


        Args:
            workingDir: absolute path to the subject directory
            config:     a configuration structure containing pipeline options

        """
        self.config = config
        self.workingDir = workingDir
        self.backupDir = os.path.join(self.workingDir, "00-backup")


    def isAToadSubject(self):
        """Determine if the directory contain all the necessary images to be consider a toad subject.

        Must have at least.
            1 high resolution anatomical image (nii or nii.gz)
            1 diffusion weighted image (nii or nii.gz)
            A corresponding B (.b) encoding or a pair of bvecs (.bvecs), bvals (.bvals) encoding file

        Returns:
            False if one of those file are missing, True otherwise

        """
        result = True

        if os.path.exists(self.backupDir):
                self.info("{} directory exists, assuming validation have already done before".format(self.backupDir))
                result = True
        else:

            if not (util.getImage(self.config, self.workingDir, 'anat') or
                        util.getImage(self.config, self.workingDir, 'anat', None, 'nii')):
                self.warning("No high resolution image found into {} directory".format(self.workingDir))
                result = False

            if not (util.getImage(self.config, self.workingDir, 'dwi') or
                    util.getImage(self.config, self.workingDir, 'dwi', None, 'nii')):
                self.warning("No diffusion weight image found into {} directory".format(self.workingDir))
                result = False

            if (not util.getImage(self.config, self.workingDir, 'grad', None, 'b')) and \
                    (not util.getImage(self.config, self.workingDir, 'grad', None, 'bvals') or not
                    util.getImage(self.config, self.workingDir, 'grad', None, 'bvecs')):
                self.warning("No valid .b encoding or (.bvals, .bvecs) files found in directory: {}".format(self.workingDir))
                result = False

        return result


    def isValidForPipeline(self):
        """Execute validation for the working directory

        this function is usually call by the task manager

        Returns:
            a Boolean that represent if the directory is a valid subject

        """
        self.info("Start validation of {} directory".format(self.workingDir))

        if os.path.exists(self.backupDir):
            #@TODO evaluate if 01-backup should be a valid toad structure
            self.info("{} directory exists, assuming validation have already done before".format(self.backupDir))
            return True

        if not os.path.exists(self.workingDir) or not os.path.isdir(self.workingDir):
            self.warning("Directory {} is not valid".format(self.workingDir))
            return False

        #make sure there is no space into filename
        if self.__isSpaceFoundIntoSubject():
            return False

        if not self.__isAValidStructure():
            self.warning("Directory {} does not appear to be a valid toad structure".format(self.workingDir))
            return False

        return True


    def __isSpaceFoundIntoSubject(self):
        """Look into the entire structure if some filename or directory contains space character

        Returns:
            a Boolean that represent if space have been found into filename, False otherwise

        """
        for root, directories, filenames in os.walk(self.workingDir):
            for filename in filenames:
                absoluteName = os.path.join(root, filename)
                if " " in absoluteName:
                    self.warning("Space character in {} is not supported by all toad dependencies tools. "
                                        .format(absoluteName))
                    return True
        return False


    def __isAValidStructure(self):
        """Determine if the directory is a valid structure

        Returns:
            a Boolean that represent if the subject integrity test pass for that directory

        """

        #Anatomical, Dwi and gradient encoding direction are mandatory input
        anat = util.getImage(self.config, self.workingDir, 'anat')
        if not anat:
            if util.getImage(self.config, self.workingDir, 'anat', None, 'nii'):
                self.warning("Found some uncompressed nifti images into {} directory. "
                           "Please gzip those images and resubmit the pipeline again".format(self.workingDir))
                return False
            self.warning("No high resolution image found into {} directory".format(self.workingDir))
            return False

        dwi = util.getImage(self.config, self.workingDir, 'dwi')
        if not dwi:
            if util.getImage(self.config, self.workingDir, 'dwi', None, 'nii'):
                self.warning("Found some uncompressed  nifti image into {} directory. "
                           "Please gzip those images and resubmit the pipeline again".format(self.workingDir))
                return False
            self.warning("No diffusion weight image found into {} directory".format(self.workingDir))
            return False

        bEnc = util.getImage(self.config, self.workingDir,'grad', None, 'b')
        bVals = util.getImage(self.config, self.workingDir,'grad', None, 'bvals')
        bVecs = util.getImage(self.config, self.workingDir,'grad', None, 'bvecs')

        if (not bEnc) and (not bVals or not bVecs):
            self.warning("No valid .b encoding or (.bvals, .bvecs) files found in directory: {}".format(self.workingDir))
            return False

        else:

            nbDirections = mriutil.getNbDirectionsFromDWI(dwi)
            if nbDirections <= 45:
                msg = "Found only {} directions into {} image. Hardi model will not be accurate with diffusion weighted image " \
                      "that contain less than 45 directions\n\n".format(nbDirections, dwi)
                self.warning(msg)
                #return False

            if bEnc and not self.__isValidEncoding(nbDirections, '.b'):
                self.warning("Encoding file {} is invalid".format(bEnc))
                return False

            if bVals and not self.__isValidEncoding(nbDirections, '.bvals'):
                self.warning("Encoding file {} is invalid".format(bEnc))
                return False

            if bVecs and not self.__isValidEncoding(nbDirections, '.bvecs'):
                self.warning("Encoding file {} is invalid".format(bVecs))
                return False

        #Validate optionnal images
        images = {
                  'anat': (anat, 'high resolution'),
                  'dwi': (dwi,'diffusion weighted'),
                  'mag': (util.getImage(self.config, self.workingDir, 'mag'), 'MR magnitude '),
                  'phase': (util.getImage(self.config, self.workingDir, 'phase'), 'MR phase '),
                  'b0_ap': (util.getImage(self.config, self.workingDir, 'b0_ap'), "posterior to anterior b0 "),
                  'b0_pa': (util.getImage(self.config, self.workingDir, 'b0_pa'), "anterior to posterior b0")}


        if self.config.get('arguments', 'debug') == 'True':
            self.debug("Images found into {} directory: {}".format(self.workingDir, images))


        if self.config.getboolean('arguments', 'prompt'):

            for key, (value, description) in images.iteritems():
                if value:
                    if not mriutil.isDataStridesOrientationExpected(value, self.config.get('preparation', 'stride_orientation'))\
                            and self.config.getboolean("preparation", "force_realign_strides"):
                        msg = "Data strides layout for {} is unexpected and force_realign_strides is set to True.\n \
                               If you continue, all unexpected images will be realign accordingly.\n\
                               Only a copy of the original images will be alter.".format(value)
                        if not util.displayYesNoMessage(msg):
                            self.warning("Remove this subject from the list?")
                            return False
                        else:
                            break

            #if one and only one b0 image is given, make sure that the b0 image is not on same direction than the dwi.
            if (not (images['b0_ap'][0] and images['b0_pa'][0])) and (images['b0_ap'][0] or images['b0_pa'][0])  \
                and (self.config.get("correction", "ignore") == "False"):
                if ((self.config.get("correction", "phase_enc_dir") == "0") and images['b0_pa'][0]) \
                    or ((self.config.get("correction", "phase_enc_dir") == "1")  and images['b0_ap'][0]):
                        msg = "Found only one B0 image into the subject directory and that B0 is in " \
                              "the same phase encoding direction than the DWI.\n" \
                              "We recommend to remove the B0 image so at least a motion correction will be perform"
                        if not util.displayYesNoMessage(msg):
                            self.warning("Remove this subject from the list?")
                            return False

            if images['mag'][0] and images['phase'][0] and (images['b0_ap'][0] or images['b0_pa'][0]):
                msg = "Found both Fieldmap and B0 images into the subject directory\n" \
                      "We recommend to disabled fieldmap correction?"
                if not util.displayYesNoMessage(msg):
                    self.warning("Remove this subject from the list?")
                    return False

            if self.config.get('denoising', 'algorithm') == "nlmeans"  and \
                self.config.get('denoising', 'number_array_coil') == "32" and \
                    not self.config.getboolean('denoising', 'ignore'):

                msg = "NLMEANS algorithm is not yet implemented for 32 coils channels images.\n" \

                if self.config.getboolean('general', 'matlab_available'):
                    msg += "set algorithm to lpca or aonlm into [denoising] section of your config.cfg.\nOtherwise " \

                msg += "set ignore: True into [denoising] section of your config.cfg.\n" \
                        "This subject will probably failed"

                if not util.displayYesNoMessage(msg, "Continue anyway? (y or n)"):
                    self.warning("Remove this subject from the list?")
                    return False

        return True


    def __isValidEncoding(self, nbDirection, type):
        """Determine if an image with a prefix exists into the subject directory

        Args:
            nbDirection: number of direction into DWI image
            type: type of encoding file. Valid values are: .b, .bvals, .bvecs

        Returns:
            a Boolean that represent if the encoding file is valid

        """

        result = True

        encoding = util.getImage(self.config, self.workingDir, 'grad', None, type)
        if not encoding:
            self.warning("No {} encoding file found in directory: {}"
                                .format(type, self.workingDir))
            result = False

        f = open(encoding,'r')
        lines = f.readlines()
        f.close()

        if type=='.bvals':
            for line in lines:
                nbElements = len(line.split())
                if nbElements != nbDirection:
                    self.warning("Expecting {} elements in {} file, counting {}"
                                        .format(nbDirection, encoding, nbElements))
                    result = False

        elif type=='.bvecs':
            if len(lines) != 3:
                self.warning("Expecting 3 vectors in {} file, counting {}".format(encoding, len(lines)))
                result = False
            for line in lines:
                if len(line.split()) != nbDirection:
                    self.warning("Expecting {} values in {} file, counting {}"
                                        .format(nbDirection, encoding, len(line.split())))
                    result = False

        elif type=='.b':
            if len(lines) != nbDirection:
                self.warning("Expecting {} lines in {} file, counting {}".format(nbDirection, type, len(lines)))
                result = False

            for index, line in enumerate(lines):
                if len(line.split()) != 4:
                    self.warning("Expecting 4 elements at line {} of file {}, counting {}"
                                        .format(index+1, encoding, len(line.split())))
                    result = False
        else:
            self.warning("Unknown encoding file type")
            result = False

        return result
