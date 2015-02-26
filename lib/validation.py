# -*- coding: utf-8 -*-
from lib import mriutil, util
import os

class Validation(object):


    def __init__(self, workingDir, logger, config):
        """Class which is primary goal is to determine if a toad subject is valid

        Validate all files and images into subject subdirectory and determine if that subject is valid
        Valid structure should contain:
            A High resolution image
            A diffusion tensor image
            A gradient encoding file, optionnaly in bval, bvec format
            Optionnaly, B0_Anterior-Posterior and/or B0_Posterior-Anterior image
            Optionnal aparc_aseg, freesurfer_anat
            only one T1,dwi, .b per subject

        Args:
            workingDir: absolute path to the subject directory
            logger:     the logger for that pipeline
            config:     a configuration structure containing pipeline options

        """
        self.config = config
        self.logger = logger
        self.workingDir = workingDir
        self.backupDir = os.path.join(self.workingDir, "00-backup")


    def isAToadSubject(self):
        """Determine if the directory contain all the necessary images to be consider a toad subject.

        Must have at least.
            1 high resolution anatomical image (nii or nii.gz)
            1 diffusion weighted image (nii or nii.gz)
            A corresponding B (.b) encoding or a pair of bvec (.bvec), bval (.bval) encoding file

        Returns:
            False if one of those file are missing, True otherwise

        """
        result = True

        if not (util.getImage(self.config, self.workingDir, 'anat') or
                    util.getImage(self.config, self.workingDir, 'anat', None, 'nii')):
            self.logger.warning("No high resolution image found into {} directory".format(self.workingDir))
            result = False

        if not (util.getImage(self.config, self.workingDir, 'dwi') or
                util.getImage(self.config, self.workingDir, 'dwi', None, 'nii')):
            self.logger.warning("No diffusion weight image found into {} directory".format(self.workingDir))
            result = False

        if (not util.getImage(self.config, self.workingDir,'grad', None, 'b')) and \
                (not util.getImage(self.config, self.workingDir,'grad', None, 'bval') or not
                util.getImage(self.config, self.workingDir,'grad', None, 'bvec')):
            self.logger.warning("No valid .b encoding or (.bval, .bvec) files found in directory: {}".format(self.workingDir))
            result = False

        return result


    def validate(self):
        """Execute validation for the working directory

        this function is usually call by the task manager

        Returns:
            a Boolean that represent if the directory is a valid subject

        """

        if not self.isDirty():
            #@TODO evaluate if 00-backup should be a valid toad structure
            self.logger.info("{} directory exists, assuming validation have already done before".format(self.backupDir))
            return True

        if not os.path.exists(self.workingDir) or not os.path.isdir(self.workingDir):
            self.logger.warning("Directory {} is not valid".format(self.workingDir))
            return False

        if not self.__isAValidStructure():
            self.logger.warning("Directory {} does not appear to be a valid toad structure".format(self.workingDir))
            return False

        return True


    def isDirty(self):
        """Determine if a validation tasks should be executed for that directory

        if raw directory exists, we consider that validation have already done prior,
        @TODO this trivial stategy should be improve in a future version

        Returns:
            a Boolean that represent if validation is required for that directory

        """
        return not os.path.exists(self.backupDir)


    def __isAValidStructure(self):
        """Determine if the directory is a valid structure

        Returns:
            a Boolean that represent if the subject integrity test pass for that directory

        """

        #Anatomical, Dwi and gradient encoding direction are mandatory input
        anat = util.getImage(self.config, self.workingDir, 'anat')
        if not anat:
            if util.getImage(self.config, self.workingDir, 'anat', None, 'nii'):
                self.logger.warning("Found some uncompressed nifti images into {} directory. "
                           "Please gzip those images and resubmit the pipeline again".format(self.workingDir))
                return False
            self.logger.warning("No high resolution image found into {} directory".format(self.workingDir))
            return False

        dwi = util.getImage(self.config, self.workingDir, 'dwi')
        if not dwi:
            if util.getImage(self.config, self.workingDir, 'dwi', None, 'nii'):
                self.logger.warning("Found some uncompressed  nifti image into {} directory. "
                           "Please gzip those images and resubmit the pipeline again".format(self.workingDir))
                return False
            self.logger.warning("No diffusion weight image found into {} directory".format(self.workingDir))
            return False

        bEnc = util.getImage(self.config, self.workingDir,'grad', None, 'b')
        bVal = util.getImage(self.config, self.workingDir,'grad', None, 'bval')
        bVec = util.getImage(self.config, self.workingDir,'grad', None, 'bvec')

        if (not bEnc) and (not bVal or not bVec):
            self.logger.warning("No valid .b encoding or (.bval, .bvec) files found in directory: {}".format(self.workingDir))
            return False
        else:

            nbDirections = mriutil.getNbDirectionsFromDWI(dwi)
            if nbDirections <= 45:
                msg = "Found only {} directions into {} image. Hardi model will not be accurate with diffusion weighted image " \
                      "that contain less than 45 directions\n\n".format(nbDirections, dwi)
                self.logger.warning(msg)
                return False

            if bEnc and not self.__isValidEncoding(nbDirections, '.b'):
                self.logger.warning("Encoding file {} is invalid".format(bEnc))
                return False

            if bVal and not self.__isValidEncoding(nbDirections, '.bval'):
                self.logger.warning("Encoding file {} is invalid".format(bEnc))
                return False

            if bVec and not self.__isValidEncoding(nbDirections, '.bvec'):
                self.logger.warning("Encoding file {} is invalid".format(bVec))
                return False

        #Validate optionnal images
        images = {
                  'high resolution': anat,
                  'diffusion weighted': dwi,
                  'MR magnitude ': util.getImage(self.config, self.workingDir, 'mag'),
                  'MR phase ': util.getImage(self.config, self.workingDir, 'phase'),
                  'parcellation': util.getImage(self.config, self.workingDir,'aparc_aseg'),
                  'anatomical': util.getImage(self.config, self.workingDir, 'anat','freesurfer'),
                  'left hemisphere ribbon': util.getImage(self.config, self.workingDir, 'lh_ribbon'),
                  'right hemisphere ribbon': util.getImage(self.config, self.workingDir, 'rh_ribbon'),
                  'brodmann': util.getImage(self.config, self.workingDir, 'brodmann'),
                  "posterior to anterior b0 ": util.getImage(self.config, self.workingDir, 'b0PA'),
                  "anterior to posterior b0": util.getImage(self.config, self.workingDir, 'b0AP')}

        for key, value in images.iteritems():
            if value:
                if not mriutil.isDataStridesOrientationExpected(value, self.config.get('preparation','stride_orientation'))\
                        and self.config.getboolean('arguments', 'prompt')\
                        and self.config.getboolean("preparation", "force_realign_strides"):
                    msg = "Data strides layout for {} is unexpected and force_realign_strides is set to True.\n \
                           If you continue, all unexpected images will be realign accordingly.\n\
                           Only a copy of the original images will be alter.".format(value)
                    if not util.displayYesNoMessage(msg):
                        self.logger.warning("Remove this subject from the list?")
                        return False
                    else:
                        break

        return True


    def __isValidEncoding(self, nbDirection, type):
        """Determine if an image with a prefix exists into the subject directory

        Args:
            nbDirection: number of direction into DWI image
            type: type of encoding file. Valid values are: .b, .bval, .bvec

        Returns:
            a Boolean that represent if the encoding file is valid

        """

        result = True

        encoding = util.getImage(self.config, self.workingDir, 'grad', None, type)
        if not encoding:
            self.logger.warning("No {} encoding file found in directory: {}"
                                .format(type, self.workingDir))
            result = False

        f = open(encoding,'r')
        lines = f.readlines()
        f.close()

        if type=='.bval':
            for line in lines:
                nbElements = len(line.split())
                if nbElements != nbDirection:
                    self.logger.warning("Expecting {} elements in {} file, counting {}"
                                        .format(nbDirection, encoding, nbElements))
                    result = False

        elif type=='.bvec':
            if len(lines) != 3:
                self.logger.warning("Expecting 3 vectors in {} file, counting {}".format(encoding, len(lines)))
                result = False
            for line in lines:
                if len(line.split()) != nbDirection:
                    self.logger.warning("Expecting {} values in {} file, counting {}"
                                        .format(nbDirection, encoding, len(line.split())))
                    result = False

        elif type=='.b':
            if len(lines) != nbDirection:
                self.logger.warning("Expecting {} lines in {} file, counting {}".format(nbDirection, type, len(lines)))
                result = False

            for index, line in enumerate(lines):
                if len(line.split()) != 4:
                    self.logger.warning("Expecting 4 elements at line {} of file {}, counting {}"
                                        .format(index+1, encoding, len(line.split())))
                    result = False
        else:
            self.logger.warning("Unknown encoding file type")
            result = False

        return result
