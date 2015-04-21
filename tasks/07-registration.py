import os

from core.generictask import GenericTask
from lib.images import Images
from lib import mriutil


__author__ = 'desmat'

class Registration(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preprocessing', 'parcellation', 'qa')


    def implement(self):

        b0 = self.getImage(self.dependDir, 'b0','upsample')
        b02x2x2 = self.getImage(self.dependDir, 'b0','2x2x2')

        anat = self.getImage(self.parcellationDir, 'anat', 'freesurfer')
        anatBrain = self.getImage(self.preprocessingDir ,'anat', 'brain')
        aparcAsegFile =  self.getImage(self.parcellationDir, "aparc_aseg")
        rhRibbon = self.getImage(self.parcellationDir, "rh_ribbon")
        lhRibbon = self.getImage(self.parcellationDir, "lh_ribbon")
        brodmann = self.getImage(self.parcellationDir, "brodmann")

        b0ToAnatMatrix = self.__computeResample(b0, anat)
        b0ToAnatMatrixInverse = self.buildName(b0ToAnatMatrix, 'inverse', 'mat')
        self.info(mriutil.invertMatrix(b0ToAnatMatrix, b0ToAnatMatrixInverse))

        self.__applyResampleFsl(anat, b0, b0ToAnatMatrixInverse, self.buildName(anat, "resample"))
        mrtrixMatrix = self.__transformMatrixFslToMrtrix(anat, b0, b0ToAnatMatrixInverse)

        self.__applyResampleFsl(anatBrain, b0, b0ToAnatMatrixInverse, self.buildName(anatBrain, "resample"))
        self.__applyRegistrationMrtrix(aparcAsegFile, mrtrixMatrix)
        self.__applyResampleFsl(aparcAsegFile, b0, b0ToAnatMatrixInverse, self.buildName(aparcAsegFile, "resample"), True)


        b02x2x2ToAnatMatrix = self.__computeResample(b02x2x2, anat)
        b02x2x2ToAnatMatrixInverse = self.buildName(b02x2x2ToAnatMatrix, 'inverse', 'mat')
        self.info(mriutil.invertMatrix(b02x2x2ToAnatMatrix, b02x2x2ToAnatMatrixInverse))

        self.__applyResampleFsl(aparcAsegFile, b02x2x2, b02x2x2ToAnatMatrixInverse, self.buildName(aparcAsegFile, "2x2x2"), True)
        self.__applyResampleFsl(anatBrain, b02x2x2, b02x2x2ToAnatMatrixInverse, self.buildName(anatBrain, "2x2x2"))


        brodmannRegister = self.__applyRegistrationMrtrix(brodmann, mrtrixMatrix)
        self.__applyResampleFsl(brodmann, b0, b0ToAnatMatrixInverse, self.buildName(brodmann, "resample"), True)

        lhRibbonRegister = self.__applyRegistrationMrtrix(lhRibbon, mrtrixMatrix)
        rhRibbonRegister = self.__applyRegistrationMrtrix(rhRibbon, mrtrixMatrix)

        self.__applyResampleFsl(lhRibbon, b0, b0ToAnatMatrixInverse, self.buildName(lhRibbon, "resample"),True)
        self.__applyResampleFsl(rhRibbon, b0, b0ToAnatMatrixInverse, self.buildName(rhRibbon, "resample"),True)

        brodmannLRegister =  self.buildName(brodmannRegister, "left_hemisphere")
        brodmannRRegister =  self.buildName(brodmannRegister, "right_hemisphere")

        self.__multiply(brodmannRegister, lhRibbonRegister, brodmannLRegister)
        self.__multiply(brodmannRegister, rhRibbonRegister, brodmannRRegister)

        #QA
        b0BrainMask = self.getImage(self.workingDir, 'anat', ['brain', 'resample'])
        aparcAseg = self.getImage(self.workingDir, 'aparc_aseg', 'resample')
        brodmann = self.getImage(self.workingDir, 'brodmann', 'resample')

        b0BrainMaskPng = self.buildName(b0, 'brain', 'png')
        aparcAsegPng = self.buildName(aparcAseg, None, 'png')
        brodmannPng = self.buildName(brodmann, None, 'png')

        self.slicerPng(b0, b0BrainMaskPng, maskOverlay=b0BrainMask)
        self.slicerPng(b0, aparcAsegPng, segOverlay=aparcAseg)
        self.slicerPng(b0, brodmannPng, segOverlay=brodmann)


    def __multiply(self, source, ribbon, target):

        cmd = "mrcalc {} {} -mult {} -quiet".format(source, ribbon, target)
        self.launchCommand(cmd)
        return target


    def __computeResample(self, source, reference):
        """Register an image with symmetric normalization and mutual information metric

        Returns:
            return a file containing the resulting transformation
        """
        self.info("Starting registration from fsl")
        name = os.path.basename(source).replace(".nii", "")
        target = self.buildName(name, "transformation", "")
        matrix = self.buildName(name, "transformation", ".mat")
        cmd = "flirt -in {} -ref {} -cost {} -omat {} -out {}".format(source, reference, self.get('cost'), matrix, target)
        self.launchCommand(cmd)
        return matrix


    def __applyResampleFsl(self, source, reference, matrix, target, nearest = False):
        """Register an image with symmetric normalization and mutual information metric

        Args:
            source:
            reference: use this image as reference
            matrix:
            target: the output file name
            nearest: A boolean, process nearest neighbour interpolation

        Returns:
            return a file containing the resulting image transform
        """
        self.info("Starting registration from fsl")
        cmd = "flirt -in {} -ref {} -applyxfm -init {} -out {} ".format(source, reference, matrix, target)
        if nearest:
            cmd += "-interp nearestneighbour"
        self.launchCommand(cmd)
        return target


    def __transformMatrixFslToMrtrix(self, source, b0, matrix ):
        target = self.buildName(matrix, "mrtrix", ".mat")
        cmd = "transformcalc -flirt_import {} {} {} {} -quiet".format(source, b0, matrix, target)
        self.launchCommand(cmd)
        return target


    def __applyRegistrationMrtrix(self, source , matrix):
        target = self.buildName(source, "register")
        cmd = "mrtransform  {} -linear {} {} -quiet".format(source, matrix, target)
        self.launchCommand(cmd)
        return target


    def meetRequirement(self):
        images = Images((self.getImage(self.parcellationDir, 'anat', 'freesurfer'), 'high resolution'),
                          (self.getImage(self.dependDir, 'anat', 'brain'), 'freesurfer anatomical brain extracted'),
                          (self.getImage(self.dependDir, 'b0', 'upsample'), 'b0 upsampled'),
                          (self.getImage(self.dependDir, 'b0','2x2x2'), 'b0 2x2x2'),
                          (self.getImage(self.parcellationDir, 'aparc_aseg'), 'parcellation'),
                          (self.getImage(self.parcellationDir, 'rh_ribbon'), 'right hemisphere ribbon'),
                          (self.getImage(self.parcellationDir, 'lh_ribbon'), 'left hemisphere ribbon'),
                          (self.getImage(self.parcellationDir, 'brodmann'), 'brodmann'))
        return images.isAllImagesExists()


    def isDirty(self):
        images = Images((self.getImage(self.workingDir,'anat', ['brain', 'resample']), 'anatomical brain resampled'),
                  (self.getImage(self.workingDir,'anat','resample'), 'anatomical resampled'),
                  (self.getImage(self.workingDir,'anat', ['brain', '2x2x2']), 'anatomical 2x2x2 brain for dtifit'),
                  (self.getImage(self.workingDir,'aparc_aseg', '2x2x2'), 'parcellation 2x2x2 for dtifit'),
                  (self.getImage(self.workingDir,'aparc_aseg', 'resample'), 'parcellation resample'),
                  (self.getImage(self.workingDir,'aparc_aseg', 'register'), 'parcellation register'),
                  (self.getImage(self.workingDir,'brodmann', ['register', "left_hemisphere"]), 'brodmann register left hemisphere'),
                  (self.getImage(self.workingDir,'brodmann', ['register', "right_hemisphere"]), 'brodmann register right hemisphere'))
        return images.isSomeImagesMissing()


    def qaSupplier(self):

        b0BrainMaskPng = self.getImage(self.workingDir, 'b0', 'brain', ext='png')
        aparcAsegPng = self.getImage(self.workingDir, 'aparc_aseg', ext='png')
        brodmannPng = self.getImage(self.workingDir, 'brodmann', ext='png')

        return Images((b0BrainMaskPng, 'Brain mask on upsampled b0'),
                      (aparcAsegPng, 'aparcaseg segmentaion on upsampled b0'),
                      (brodmannPng, 'Brodmann segmentaion on upsampled b0'),
                     )
