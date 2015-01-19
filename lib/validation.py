# -*- coding: utf-8 -*-
from lib import mriutil, util
import glob
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
            Optionnal aparc_aseg, anat_freesurfer
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
            self.logger.info("{} directory exists, assuming validation is o.k.".format(self.backupDir))
            return True

        if not os.path.exists(self.workingDir) or not os.path.isdir(self.workingDir):
            self.logger.error("Directory {} is not valid".format(self.workingDir))
            return False

        if not self.__isValidStructure():
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


    def __isValidStructure(self):
        """Determine if the directory is a valid structure

        Returns:
            a Boolean that represent if validation is required for that directory

        """
        if not self.__validateImage(self.config.get('prefix','anat')):
            return False

        if not self.__validateImage(self.config.get('prefix','dwi')):
            return False


        dwi = util.getImage(self.config, self.workingDir,'dwi')

        #@TODO send data layout warning if strides are not 1,2,3
        #make sure that diffusion image Z scale layout is oriented correctly
        #if not mriutil.isDataLayoutValid(dwiImage):
        #    self.error("Data layout for {} image is unexpected. "
        #                        "Only data layout = [ +0 +1 +2 +3 ] could be process".format(dwiImage))

        nbDirections = mriutil.getNbDirectionsFromDWI(dwi)
        if nbDirections <= 45:
            msg = "Found only {} directions into {} image. Hardi model will not be accurate with diffusion weighted image " \
                  "that contain less than 45 directions\n\n".format(nbDirections, self.dwi)
            if self.config.getboolean('arguments', 'prompt'):
                util.displayYesNoMessage(msg)
            else:
                self.warning(msg)


        bEnc = util.getImage(self.config, self.workingDir,'grad', None, 'b')
        bVal = util.getImage(self.config, self.workingDir,'grad', None, 'bval')
        bVec = util.getImage(self.config, self.workingDir,'grad', None, 'bvec')

        if (not bEnc) and (not bVal or not bVec):
            self.logger.warning("No valid .b encoding or pair of .bval, .bvec"
                                " file found in directory: {}".format(self.workingDir))
            return False
        #@TODO uncomment and fix not all zero bvec value in the first line
        """
        if bEnc and not self.__isValidEncoding(nbDirections, '.b'):
            self.logger.warning("Encoding file {} is invalid".format(bEnc))
            return False

        if bVal and not self.__isValidEncoding(nbDirections, '.bval'):
            self.logger.warning("Encoding file {} is invalid".format(bEnc))
            return False
        if bVec and not self.__isValidEncoding(nbDirections, '.bvec'):
            self.logger.warning("Encoding file {} is invalid".format(bVec))
            return False
        """
        return True


    def __validateImage(self, prefix):
        """Determine if an image with a prefix exists into the subject directory

        Args:
            prefix: prefix that is required into the filename

        Returns:
            a Boolean that represent if the image filename exist

        """        
        files = glob.glob("{}/{}*.nii*".format(self.workingDir, prefix))
        if not files:
            self.logger.warning("No {} images found with pattern {}* in directory: {}"
                                .format(prefix.replace("_",""), prefix, self.workingDir))
            return False
        if len(files) > 1:
            self.logger.warning("Found many {} images in directory {}, please provide only one"
                                .format(prefix.replace("_",""), self.workingDir))
            return False
        filename = os.path.basename(files.pop())

        #make sure that some postfix are not contain in the image file
        for (key, item) in self.config.items("postfix"):
            if item in filename:
                self.logger.warning("Image name {} contain postfix {} which is prohibited".format(filename,item))
                return False
        return True


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
                if index == 0:
                    for token in line.split():
                        if token not in "0" :
                            self.logger.warning("Expecting only zero values in the first line of file {}, found value {}"
                                                .format(encoding, token))
                            return False
                if len(line.split()) != 4:
                    self.logger.warning("Expecting 4 elements at line {} of file {}, counting {}"
                                        .format(index+1, encoding, len(line.split())))
                    return False
        else:
            self.logger.warning("Unknown encoding file type")
            return False
        return True