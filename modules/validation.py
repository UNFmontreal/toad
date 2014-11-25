# -*- coding: utf-8 -*-
from modules import mriutil, util
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
            self.logger.info("%s directory exists, assuming validation is o.k."%self.backupDir)
            return True

        if not os.path.exists(self.workingDir) or not os.path.isdir(self.workingDir):
            self.logger.error("Directory %s is not valid"%(self.workingDir))
            return False

        if not self.__isValidStructure():
            self.logger.error("Directory %s does not appear to be a valid toad structure"%self.workingDir)
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


        dwiImage = util.getImage(self.config, self.workingDir,'dwi')

        #@TODO fix data layout incomprehesion
        #make sure that diffusion image Z scale layout is oriented correctly
        #if not mriutil.isDataLayoutValid(dwiImage):
        #    self.error("Data layout for %s image is unexpected. "
        #                        "Only data layout = [ +0 +1 +2 +3 ] could be process"%dwiImage)

        nbDirections = mriutil.getNbDirectionsFromDWI(dwiImage)

        bEnc = util.getImage(self.config, self.workingDir,'grad', None, 'b')
        bVal = util.getImage(self.config, self.workingDir,'grad', None, 'bval')
        bVec = util.getImage(self.config, self.workingDir,'grad', None, 'bvec')

        if (not bEnc) and (not bVal or not bVec):
            self.logger.warning("No valid .b encoding or pair of .bval, .bvec"
                                " file found in directory: %s"%self.workingDir)
            return False

        if bEnc and not self.__isValidEncoding(nbDirections, '.b'):
            self.logger.warning("Encoding file %s is invalid"%bEnc)
            return False

        if bVal and not self.__isValidEncoding(nbDirections, '.bval'):
            self.logger.warning("Encoding file %s is invalid"%bEnc)
            return False
        if bVec and not self.__isValidEncoding(nbDirections, '.bvec'):
            self.logger.warning("Encoding file %s is invalid"%bVec)
            return False
        return True


    def __validateImage(self, prefix):
        """Determine if an image with a prefix exists into the subject directory

        Args:
            prefix: prefix that is required into the filename

        Returns:
            a Boolean that represent if the image filename exist

        """        
        files = glob.glob("%s/%s*.nii*"%(self.workingDir, prefix))
        if not files:
            self.logger.warning("No %s images found with pattern %s* in directory: %s"
                                %(prefix.replace("_",""),prefix, self.workingDir))
            return False
        if len(files) > 1:
            self.logger.warning("Found many %s images in directory %s, please provide only one"
                                %(prefix.replace("_",""), self.workingDir))
            return False
        filename = os.path.basename(files.pop())

        #make sure that some postfix are not contain in the image file
        for (key, item) in self.config.items("postfix"):
            if item in filename:
                self.logger.warning("Image name %s contain postfix %s which is prohibited"%(filename,item))
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
            self.logger.warning("No %s encoding file found in directory: %s"
                                %(type, self.workingDir))
            return False

        f = open(encoding,'r')
        lines = f.readlines()
        f.close()

        if type=='.bval':
            for line in lines:
                nbElements = len(line.split())
                if nbElements != nbDirection:
                    self.logger.warning("Expecting %s elements in %s file, counting %s"%(nbDirection,
                                                                                         encoding, nbElements))
                    return False

        elif type=='.bvec':
            if len(lines) != 3:
                self.logger.warning("Expecting 3 vectors in %s file, counting %s"%(encoding, len(lines)))
                return False
            for line in lines:
                if len(line.split()) != nbDirection:
                    self.logger.warning("Expecting %s values in %s file, counting %s"%(nbDirection,
                                                                                       encoding, len(line.split())))
                    return False

        elif type=='.b':
            if len(lines) != nbDirection:
                self.logger.warning("Expecting %s lines in %s file, counting %s"%(nbDirection, type, len(lines)))
                return False

            for index, line in enumerate(lines):
                if index == 0:
                    for token in line.split():
                        if token not in "0" :
                            self.logger.warning("Expecting only zero values in the first line of file %s, found value %s"
                                                %(encoding, token))
                            return False
                if len(line.split()) != 4:
                    self.logger.warning("Expecting 4 elements at line %s of file %s, counting %s"
                                        %(index+1, encoding, len(line.split())))
                    return False
        else:
            self.logger.warning("Unknown encoding file type")
            return False
        return True