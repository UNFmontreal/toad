# -*- coding: utf-8 -*-
from lib import mriutil, util
import os


class Validation(object):


    def __init__(self, workingDir, logger, config):
        """Determine if that subject is valid

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


    def run(self):
        """Execute validation for the working directory

        this function is usually call by the task manager

        Returns:
            a Boolean that represent if the directory is a valid subject

        """

        if not self.isDirty():
            self.logger.info("{} directory exists, assuming validation have already done before".format(self.backupDir))
            return True

        if not os.path.exists(self.workingDir) or not os.path.isdir(self.workingDir):
            self.logger.error("Directory {} is not valid".format(self.workingDir))
            return False

        if not self.__isAValidStructure():
            self.logger.error("Directory {} does not appear to be a valid toad structure".format(self.workingDir))
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
            a Boolean that represent if validation is required for that directory

        """

        #Anatomical, Dwi and gradient fieldmap are mandatory input
        anat = util.getImage(self.config, self.workingDir, 'anat')
        if not anat:
            if util.getImage(self.config, self.workingDir, 'anat', None, 'nii'):
                self.logger.error("Found some uncompressed images into {} directory. "
                           "gzip those images and resubmit the pipeline again".format(self.workingDir))
            self.logger.error("No high resolution image found into {} directory".format(self.workingDir))

        dwi = util.getImage(self.config, self.workingDir, 'dwi')
        if not dwi:
            if util.getImage(self.config, self.workingDir, 'dwi', None, 'nii'):
                self.logger.error("Found some uncompressed image into {} directory. "
                           "gzip those images and resubmit the pipeline again".format(self.workingDir))
            self.logger.error("No diffusion weight image found into {} directory".format(self.workingDir))

        bEnc = util.getImage(self.config, self.workingDir,'grad', None, 'b')
        bVal = util.getImage(self.config, self.workingDir,'grad', None, 'bval')
        bVec = util.getImage(self.config, self.workingDir,'grad', None, 'bvec')

        if (not bEnc) and (not bVal or not bVec):
            self.logger.error("No valid .b encoding or (.bval, .bvec) files found in directory: {}".format(self.workingDir))
        else:

            nbDirections = mriutil.getNbDirectionsFromDWI(dwi)
            if nbDirections <= 45:
                msg = "Found only {} directions into {} image. Hardi model will not be accurate with diffusion weighted image " \
                      "that contain less than 45 directions\n\n".format(nbDirections, dwi)
                if self.config.getboolean('arguments', 'prompt'):
                    if util.displayYesNoMessage(msg):
                        self.info("The pipeline may failed during the execution")
                    else:
                        self.quit()
                else:
                    self.warning(msg)


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
                if not mriutil.isDataStridesOrientationExpected(value) and self.config.getboolean('arguments', 'prompt') \
                        and self.config.getboolean("preparation", "force_realign_strides"):
                    msg = "Data strides layout for {} is unexpected and force_realign_strides is set to True.\n \
                           If you continue, all unexpected images will be realign accordingly.\n\
                           Only a copy of the original images will be alter.".format(value)
                    if not util.displayYesNoMessage(msg):
                        self.quit("Quit the pipeline as user request")
                    else:
                        break

        return True

    """
    def __validateNiftiImage(self, prefix):
        Determine if an image with a prefix exists into the subject directory

        Args:
            prefix: prefix that is required into the filename

        Returns:
            a Boolean that represent if the image filename exist



        files = glob.glob("{}/{}*.nii*".format(self.workingDir, prefix))
        if not files:
            self.logger.warning("No {} images found with pattern {}* in directory: {}"
                                .format(prefix.replace("_",""), prefix, self.workingDir))
            return False
        if len(files) > 1:
            self.logger.warning("Found many {} images in directory {}, only one should be provided"
                                .format(prefix.replace("_",""), self.workingDir))
            return False

        filename = os.path.basename(files.pop())
        #make sure that some postfix are not contain in the image file
        for (key, item) in self.config.items("postfix"):
            if item in filename:
                self.logger.warning("Image name {} contain postfix {} which is prohibited".format(filename,item))
                return False
        return True
    """

    def __isValidEncoding(self, nbDirection, type):
        """Determine if an image with a prefix exists into the subject directory

        Args:
            nbDirection: number of direction into DWI image
            type: type of encoding file. Valid values are: .b, .bval, .bvec

        Returns:
            a Boolean that represent if the encoding file is valid

        """
        encoding = util.getImage(self.config, self.workingDir, 'grad', None, type)
        if not encoding:
            self.logger.warning("No {} encoding file found in directory: {}"
                                .format(type, self.workingDir))
            return False

        f = open(encoding,'r')
        lines = f.readlines()
        f.close()

        if type=='.bval':
            for line in lines:
                nbElements = len(line.split())
                if nbElements != nbDirection:
                    self.logger.warning("Expecting {} elements in {} file, counting {}"
                                        .format(nbDirection, encoding, nbElements))
                    return False

        elif type=='.bvec':
            if len(lines) != 3:
                self.logger.warning("Expecting 3 vectors in {} file, counting {}".format(encoding, len(lines)))
                return False
            for line in lines:
                if len(line.split()) != nbDirection:
                    self.logger.warning("Expecting {} values in {} file, counting {}"
                                        .format(nbDirection, encoding, len(line.split())))
                    return False

        elif type=='.b':
            if len(lines) != nbDirection:
                self.logger.warning("Expecting {} lines in {} file, counting {}".format(nbDirection, type, len(lines)))
                return False

            for index, line in enumerate(lines):
                if len(line.split()) != 4:
                    self.logger.warning("Expecting 4 elements at line {} of file {}, counting {}"
                                        .format(index+1, encoding, len(line.split())))
                    return False
        else:
            self.logger.warning("Unknown encoding file type")
            return False
        return True
