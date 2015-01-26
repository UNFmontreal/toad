from lib.generictask import GenericTask
from lib import mriutil
import os

__author__ = 'desmat'

class Registration(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preprocessing', 'parcellation', 'preparation')


    def implement(self):


        b0 = self.getImage(self.dependDir, 'b0')
        anat = self.getImage(self.preparationDir, 'anat')
        anatBrain = self.getImage(self.workingDir ,'anat', "brain")
        aparcAsegFile =  self.getImage(self.parcellationDir, "aparc_aseg")
        rhRibbon = self.getImage(self.parcellationDir, "rh_ribbon")
        lhRibbon = self.getImage(self.parcellationDir, "lh_ribbon")
        brodmann = self.getImage(self.parcellationDir, "brodmann")


        b0ToAnatMatrix = self.__computeResample(b0, anat)
        b0ToAnatMatrixInverse = mriutil.invertMatrix(b0ToAnatMatrix, self.buildName(b0ToAnatMatrix, 'inverse', 'mat'))
        self.__applyResampleFsl(anat, b0, b0ToAnatMatrixInverse)
        mrtrixMatrix = self.__transformMatrixFslToMrtrix(anat, b0, b0ToAnatMatrixInverse)


        self.__applyRegistrationMrtrix(aparcAsegFile, mrtrixMatrix)
        self.__applyResampleFsl(aparcAsegFile, b0, b0ToAnatMatrixInverse)

        anatBrainResampled = self.__applyResampleFsl(anatBrain, b0, b0ToAnatMatrixInverse)

        brodmannRegister = self.__applyRegistrationMrtrix(brodmann, mrtrixMatrix)
        brodmannResampled = self.__applyResampleFsl(brodmann, b0, b0ToAnatMatrixInverse)

        lhRibbonRegister = self.__applyRegistrationMrtrix(lhRibbon, mrtrixMatrix)
        rhRibbonRegister = self.__applyRegistrationMrtrix(rhRibbon, mrtrixMatrix)

        lhRibbonResampled = self.__applyResampleFsl(lhRibbon, b0, b0ToAnatMatrixInverse)
        rhRibbonResampled = self.__applyResampleFsl(rhRibbon, b0, b0ToAnatMatrixInverse)

        brodmannLRegister =  self.buildName(brodmannRegister, "left_hemisphere")
        brodmannRRegister =  self.buildName(brodmannRegister, "right_hemisphere")
        self.__multiply(brodmannRegister, lhRibbonRegister, brodmannLRegister)
        self.__multiply(brodmannRegister, rhRibbonRegister, brodmannRRegister)



    def __multiply(self, source, ribbon, target):
        cmd = "mrcalc {} -mul {} {}".format(source, ribbon, target)
        self.launchCommand(cmd)
        return target


    def __computeResample(self, source, reference):
        """Register an image with symmetric normalization and mutual information metric

        Returns:
            return a file containing the resulting transformation
        """
        self.info("Starting registration from fsl")
        name = os.path.basename(source).replace(".nii","")
        target = self.buildName(name, "transformation")
        matrix = self.buildName(name, "transformation", ".mat")
        cmd = "flirt -in {} -ref {} -cost {} -omat {} -out {}".format(source, reference, self.get('cost'), matrix, target)
        self.launchCommand(cmd)
        return matrix


    def __applyResampleFsl(self, source, reference, matrix):
        """Register an image with symmetric normalization and mutual information metric

        Returns:
            return a file containing the resulting transformation
        """
        self.info("Starting registration from fsl")
        name = os.path.basename(source).replace(".nii","")
        target = self.buildName(name, "resample")
        cmd = "flirt -in {} -ref {} -applyxfm -init {} -out {}".format(source, reference, matrix, target)
        self.launchCommand(cmd)
        return matrix


    def __transformMatrixFslToMrtrix(self, source, b0, matrix ):
        target = self.buildName(matrix, "mrtrix", ".mat")
        cmd = "transformcalc -flirt_import {} {} {} {}".format(source, b0, matrix, target)
        self.launchCommand(cmd)
        return target


    def __applyRegistrationMrtrix(self, source , matrix):
        target = self.buildName(source, "register")
        cmd = "mrtransform  {} -linear {} {}".format(source, matrix, target)
        self.launchCommand(cmd)
        return target


    def meetRequirement(self):

        images = {'high resolution': self.getImage(self.preparationDir, 'anat'),
                  'anatomical brain extracted': self.getImage(self.dependDir, 'anat', 'brain'),
                  'b0 upsampled': self.getImage(self.dependDir, 'b0'),
                  'parcellation': self.getImage(self.parcellationDir, 'aparc_aseg'),
                  'right hemisphere ribbon': self.getImage(self.parcellationDir, 'rh_ribbon'),
                  'left hemisphere ribbon': self.getImage(self.parcellationDir, 'lh_ribbon'),
                  'brodmann': self.getImage(self.parcellationDir, 'brodmann'),
                  'high resolution freesurfer': self.getImage(self.parcellationDir, 'freesurfer_anat')}

        return self.isAllImagesExists(images)


    def isDirty(self, result = False):
        #@TODO reimplement that
        images = {'freesurfer anatomical': self.getImage(self.workingDir,'freesurfer_anat', 'resample'),
                  'parcellation': self.getImage(self.workingDir,'aparc_aseg', 'resample'),
                  'brodmann': self.getImage(self.workingDir,'brodmann', 'resample'),
                  'white matter segmented high resolution resampled': self.getImage(self.workingDir,'anat', ['brain','wm','resample']),
                  'high resolution resampled imgage':self.getImage(self.workingDir,'anat', ['brain','resample'])}
        return self.isSomeImagesMissing(images)
