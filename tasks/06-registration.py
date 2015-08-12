import os

from core.generictask import GenericTask
from lib.images import Images
from lib import mriutil


__author__ = 'desmat'

class Registration(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'upsampling', 'parcellation', 'qa')


    def implement(self):

        b0 = self.getImage(self.dependDir, 'b0','upsample')
        norm= self.getImage(self.parcellationDir, 'norm')
        anat = self.getImage(self.parcellationDir, 'anat', 'freesurfer')
        aparcAsegFile =  self.getImage(self.parcellationDir, "aparc_aseg")
        rhRibbon = self.getImage(self.parcellationDir, "rh_ribbon")
        lhRibbon = self.getImage(self.parcellationDir, "lh_ribbon")
        brodmann = self.getImage(self.parcellationDir, "brodmann")
        tt5 = self.getImage(self.parcellationDir, "tt5")

        extraArgs = ""
        if self.get("parcellation", "intrasubject"):
            extraArgs += " -usesqform -dof 6"

        freesurferToDWIMatrix = self.__freesurferToDWITransformation(b0, norm, extraArgs)

        self.__applyResampleFsl(anat, b0, freesurferToDWIMatrix, self.buildName(anat, "resample"))
        mrtrixMatrix = self.__transformFslToMrtrixMatrix(anat, b0, freesurferToDWIMatrix)

        self.__applyRegistrationMrtrix(aparcAsegFile, mrtrixMatrix)
        self.__applyResampleFsl(aparcAsegFile, b0, freesurferToDWIMatrix, self.buildName(aparcAsegFile, "resample"), True)

        brodmannRegister = self.__applyRegistrationMrtrix(brodmann, mrtrixMatrix)
        self.__applyResampleFsl(brodmann, b0, freesurferToDWIMatrix, self.buildName(brodmann, "resample"), True)

        lhRibbonRegister = self.__applyRegistrationMrtrix(lhRibbon, mrtrixMatrix)
        rhRibbonRegister = self.__applyRegistrationMrtrix(rhRibbon, mrtrixMatrix)
        tt5Register = self.__applyRegistrationMrtrix(tt5, mrtrixMatrix)


        self.__applyResampleFsl(lhRibbon, b0, freesurferToDWIMatrix, self.buildName(lhRibbon, "resample"),True)
        self.__applyResampleFsl(rhRibbon, b0, freesurferToDWIMatrix, self.buildName(rhRibbon, "resample"),True)
        self.__applyResampleFsl(tt5, b0, freesurferToDWIMatrix, self.buildName(tt5, "resample"),True)

        brodmannLRegister =  self.buildName(brodmannRegister, "left_hemisphere")
        brodmannRRegister =  self.buildName(brodmannRegister, "right_hemisphere")

        self.__multiply(brodmannRegister, lhRibbonRegister, brodmannLRegister)
        self.__multiply(brodmannRegister, rhRibbonRegister, brodmannRRegister)

        #QA
        '''
        b0BrainMask = self.getImage(self.workingDir, 'anat', ['brain', 'resample'])
        aparcAseg = self.getImage(self.workingDir, 'aparc_aseg', 'resample')
        brodmann = self.getImage(self.workingDir, 'brodmann', 'resample')

        b0BrainMaskPng = self.buildName(b0, 'brain', 'png')
        aparcAsegPng = self.buildName(aparcAseg, None, 'png')
        brodmannPng = self.buildName(brodmann, None, 'png')

        self.slicerPng(b0, b0BrainMaskPng, maskOverlay=b0BrainMask, boundaries=b0BrainMask)
        self.slicerPng(b0, aparcAsegPng, segOverlay=aparcAseg, boundaries=b0BrainMask)
        self.slicerPng(b0, brodmannPng, segOverlay=brodmann, boundaries=b0BrainMask)
        '''

    def __multiply(self, source, ribbon, target):

        cmd = "mrcalc {} {} -mult {} -quiet".format(source, ribbon, target)
        self.launchCommand(cmd)
        return target


    def __freesurferToDWITransformation(self, source, reference, extraArgs):
        dwiToFreesurferMatrix = "dwiToFressurfer_transformation.mat"
        freesurferToDWIMatrix = "fressurferToDWI_transformation.mat"
        cmd = "flirt -in {} -ref {} -omat {} {}".format(source, reference, dwiToFreesurferMatrix, extraArgs)
        self.launchCommand(cmd)
        mriutil.invertMatrix(dwiToFreesurferMatrix, freesurferToDWIMatrix)
        return freesurferToDWIMatrix


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


    def __transformFslToMrtrixMatrix(self, source, b0, matrix ):
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
                          (self.getImage(self.dependDir, 'b0', 'upsample'), 'b0 upsampled'),
                          (self.getImage(self.parcellationDir, 'aparc_aseg'), 'parcellation'),
                          (self.getImage(self.parcellationDir, 'rh_ribbon'), 'right hemisphere ribbon'),
                          (self.getImage(self.parcellationDir, 'lh_ribbon'), 'left hemisphere ribbon'),
                          (self.getImage(self.parcellationDir, 'brodmann'), 'brodmann'))
        return images.isAllImagesExists()


    def isDirty(self):
        images = Images((self.getImage(self.workingDir,'anat', 'resample'), 'anatomical resampled'),
                  (self.getImage(self.workingDir,'aparc_aseg', 'resample'), 'parcellation resample'),
                  (self.getImage(self.workingDir,'aparc_aseg', 'register'), 'parcellation register'),
                  (self.getImage(self.workingDir, 'tt5', 'register'), '5tt image register'),
                  (self.getImage(self.workingDir,'brodmann', ['register', "left_hemisphere"]), 'brodmann register left hemisphere'),
                  (self.getImage(self.workingDir,'brodmann', ['register', "right_hemisphere"]), 'brodmann register right hemisphere'))
        return images.isSomeImagesMissing()

    """
    def qaSupplier(self):

        b0BrainMaskPng = self.getImage(self.workingDir, 'b0', 'brain', ext='png')
        aparcAsegPng = self.getImage(self.workingDir, 'aparc_aseg', ext='png')
        brodmannPng = self.getImage(self.workingDir, 'brodmann', ext='png')

        return Images((b0BrainMaskPng, 'Brain mask on upsampled b0'),
                      (aparcAsegPng, 'aparcaseg segmentaion on upsampled b0'),
                      (brodmannPng, 'Brodmann segmentaion on upsampled b0'),
                     )
    """