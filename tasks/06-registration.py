# -*- coding: utf-8 -*-
from core.toad.generictask import GenericTask
from lib.images import Images
from lib import mriutil

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class Registration(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'upsampling', 'parcellation', 'qa')


    def implement(self):

        b0 = self.getUpsamplingImage('b0','upsample')
        norm= self.getParcellationImage('norm')
        anat = self.getParcellationImage('anat', 'freesurfer')
        aparcAsegFile =  self.getParcellationImage("aparc_aseg")
        rhRibbon = self.getParcellationImage("rh_ribbon")
        lhRibbon = self.getParcellationImage("lh_ribbon")
        brodmann = self.getParcellationImage("brodmann")
        aal2 = self.getParcellationImage("aal2")
        tt5 = self.getParcellationImage("tt5")
        mask = self.getParcellationImage("mask")

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

        aal2Register = self.__applyRegistrationMrtrix(aal2, mrtrixMatrix)
        self.__applyResampleFsl(aal2, b0, freesurferToDWIMatrix, self.buildName(aal2, "resample"), True)


        lhRibbonRegister = self.__applyRegistrationMrtrix(lhRibbon, mrtrixMatrix)
        rhRibbonRegister = self.__applyRegistrationMrtrix(rhRibbon, mrtrixMatrix)
        tt5Register = self.__applyRegistrationMrtrix(tt5, mrtrixMatrix)
        maskRegister = self.__applyRegistrationMrtrix(mask, mrtrixMatrix)
        normRegister = self.__applyRegistrationMrtrix(norm, mrtrixMatrix)

        self.__applyResampleFsl(lhRibbon, b0, freesurferToDWIMatrix, self.buildName(lhRibbon, "resample"),True)
        self.__applyResampleFsl(rhRibbon, b0, freesurferToDWIMatrix, self.buildName(rhRibbon, "resample"),True)
        self.__applyResampleFsl(tt5, b0, freesurferToDWIMatrix, self.buildName(tt5, "resample"),True)
        self.__applyResampleFsl(mask, b0, freesurferToDWIMatrix, self.buildName(mask, "resample"),True)
        self.__applyResampleFsl(norm, b0, freesurferToDWIMatrix, self.buildName(norm, "resample"),True)

        #brodmannLRegister =  self.buildName(brodmannRegister, "left_hemisphere")
        #brodmannRRegister =  self.buildName(brodmannRegister, "right_hemisphere")

        #self.__multiply(brodmannRegister, lhRibbonRegister, brodmannLRegister)
        #self.__multiply(brodmannRegister, rhRibbonRegister, brodmannRRegister)


    def __multiply(self, source, ribbon, target):

        cmd = "mrcalc {} {} -mult {} -quiet".format(source, ribbon, target)
        self.launchCommand(cmd)
        return target


    def __freesurferToDWITransformation(self, source, reference, extraArgs):
        dwiToFreesurferMatrix = "dwiToFreesurfer_transformation.mat"
        freesurferToDWIMatrix = "freesurferToDWI_transformation.mat"
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
        return Images((self.getParcellationImage('anat', 'freesurfer'), 'high resolution'),
                          (self.getUpsamplingImage('b0', 'upsample'), 'b0 upsampled'),
                          (self.getParcellationImage('aparc_aseg'), 'parcellation'),
                          (self.getParcellationImage('rh_ribbon'), 'right hemisphere ribbon'),
                          (self.getParcellationImage('lh_ribbon'), 'left hemisphere ribbon'),
                          (self.getParcellationImage('tt5'), '5tt'),
                          (self.getParcellationImage('mask'), 'brain mask'),
                          (self.getParcellationImage('brodmann'), 'brodmann atlas'),
                          (self.getParcellationImage('aal2'), 'aal2 atlas'))


    def isDirty(self):
        return Images((self.getImage('anat', 'resample'), 'anatomical resampled'),
                  (self.getImage('aparc_aseg', 'resample'), 'parcellation atlas resample'),
                  (self.getImage('aparc_aseg', 'register'), 'parcellation atlas register'),
                  (self.getImage('tt5', 'register'), '5tt image register'),
                  (self.getImage('mask', 'register'), 'brain mask register'),
                  (self.getImage('tt5', 'resample'), '5tt image resample'),
                  (self.getImage('mask', 'resample'), 'brain mask resample'),
                  (self.getImage('norm', 'resample'), 'brain  resample'),
                  (self.getImage('brodmann', 'resample'), 'brodmann atlas  resample'),
                  (self.getImage('brodmann', ['register', "left_hemisphere"]), 'brodmann register left hemisphere atlas'),
                  (self.getImage('brodmann', ['register', "right_hemisphere"]), 'brodmann register right hemisphere atlas'),
                  (self.getImage('aal2', 'resample'), 'aal2 atlas resample'))


    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        #Get images
        b0 = self.getUpsamplingImage('b0', 'upsample')
        brainMask = self.getImage('mask', 'resample')
        aparcAseg = self.getImage('aparc_aseg', 'resample')
        brodmann = self.getImage('brodmann', 'resample')
        aal2 = self.getImage('aal2', 'resample')

        #Build qa names
        brainMaskPng = self.buildName(brainMask, None, 'png')
        aparcAsegPng = self.buildName(aparcAseg, None, 'png')
        brodmannPng = self.buildName(brodmann, None, 'png')
        aal2Png = self.buildName(aal2, None, 'png')

        #Build qa images
        self.slicerPng(b0, brainMaskPng, maskOverlay=brainMask, boundaries=brainMask)
        self.slicerPng(b0, aparcAsegPng, segOverlay=aparcAseg, boundaries=brainMask)
        self.slicerPng(b0, brodmannPng, segOverlay=brodmann, boundaries=brainMask)
        self.slicerPng(b0, aal2Png, segOverlay=aal2, boundaries=brainMask)

        qaImages = Images(
            (brainMaskPng, 'Brain mask on upsampled b0'),
            (aparcAsegPng, 'aparcaseg segmentation on upsampled b0'),
            (brodmannPng, 'Brodmann segmentation on upsampled b0'),
            (aal2Png, 'Aal2 segmentation on upsampled b0'))

        return qaImages
