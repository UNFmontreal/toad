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
        wmparcFile = self.getParcellationImage("wmparc")
        rhRibbon = self.getParcellationImage("rh_ribbon")
        lhRibbon = self.getParcellationImage("lh_ribbon")
        tt5 = self.getParcellationImage("tt5")
        mask = self.getParcellationImage("mask")

        extraArgs = ""
        if self.get("parcellation", "intrasubject"):
            extraArgs += " -usesqform -dof 6"

        freesurferToDWIMatrix = self.__freesurferToDWITransformation(b0, norm, extraArgs)
        mriutil.applyResampleFsl(anat, b0, freesurferToDWIMatrix, self.buildName(anat, "resample"))
        mrtrixMatrix = self.__transformFslToMrtrixMatrix(anat, b0, freesurferToDWIMatrix)

        """ Grey matter parcellation """
        mriutil.applyRegistrationMrtrix(aparcAsegFile, mrtrixMatrix, self.buildName(aparcAsegFile, "register"))
        mriutil.applyResampleFsl(aparcAsegFile, b0, freesurferToDWIMatrix, self.buildName(aparcAsegFile, "resample"), True)

        """ White matter parcellation """
        mriutil.applyRegistrationMrtrix(wmparcFile, mrtrixMatrix, self.buildName(wmparcFile, "register"))
        mriutil.applyResampleFsl(wmparcFile, b0, freesurferToDWIMatrix, self.buildName(wmparcFile, "resample"), True)

        lhRibbonRegister = mriutil.applyRegistrationMrtrix(lhRibbon, mrtrixMatrix, self.buildName(lhRibbon, "register"))
        rhRibbonRegister = mriutil.applyRegistrationMrtrix(rhRibbon, mrtrixMatrix, self.buildName(rhRibbon, "register"))
        tt5Register = mriutil.applyRegistrationMrtrix(tt5, mrtrixMatrix, self.buildName(tt5, "register"))
        maskRegister = mriutil.applyRegistrationMrtrix(mask, mrtrixMatrix, self.buildName(mask, "register"))
        normRegister = mriutil.applyRegistrationMrtrix(norm, mrtrixMatrix, self.buildName(norm, "register"))

        mriutil.applyResampleFsl(lhRibbon, b0, freesurferToDWIMatrix, self.buildName(lhRibbon, "resample"),True)
        mriutil.applyResampleFsl(rhRibbon, b0, freesurferToDWIMatrix, self.buildName(rhRibbon, "resample"),True)
        mriutil.applyResampleFsl(tt5, b0, freesurferToDWIMatrix, self.buildName(tt5, "resample"),True)
        mriutil.applyResampleFsl(mask, b0, freesurferToDWIMatrix, self.buildName(mask, "resample"),True)
        mriutil.applyResampleFsl(norm, b0, freesurferToDWIMatrix, self.buildName(norm, "resample"),True)

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



    def __transformFslToMrtrixMatrix(self, source, b0, matrix ):
        target = self.buildName(matrix, "mrtrix", ".mat")
        cmd = "transformcalc -flirt_import {} {} {} {} -quiet".format(source, b0, matrix, target)
        self.launchCommand(cmd)
        return target


    def meetRequirement(self):
        return Images((self.getParcellationImage('anat', 'freesurfer'), 'high resolution'),
                          (self.getUpsamplingImage('b0', 'upsample'), 'b0 upsampled'),
                          (self.getParcellationImage('aparc_aseg'), 'parcellation'),
                          (self.getParcellationImage('wmparc'), 'parcellation'),
                          (self.getParcellationImage('rh_ribbon'), 'right hemisphere, ribbon'),
                          (self.getParcellationImage('lh_ribbon'), 'left hemisphere ribbon'),
                          (self.getParcellationImage('tt5'), '5tt'),
                          (self.getParcellationImage('mask'), 'brain mask'))


    def isDirty(self):
        return Images((self.getImage('anat', 'resample'), 'anatomical resampled'),
                  (self.getImage('aparc_aseg', 'resample'), 'parcellation atlas resample'),
                  (self.getImage('aparc_aseg', 'register'), 'parcellation atlas register'),
                  (self.getImage('wmparc', 'resample'), 'white matter parcellation atlas resample'),
                  (self.getImage('wmparc', 'register'), 'white matter parcellation atlas register'),
                  (self.getImage('tt5', 'register'), '5tt image register'),
                  (self.getImage('mask', 'register'), 'brain mask register'),
                  (self.getImage('tt5', 'resample'), '5tt image resample'),
                  (self.getImage('mask', 'resample'), 'brain mask resample'),
                  (self.getImage('norm', 'resample'), 'brain  resample'))


    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        #Get images
        b0 = self.getUpsamplingImage('b0', 'upsample')
        brainMask = self.getImage('mask', 'resample')
        aparcAseg = self.getImage('aparc_aseg', 'resample')
        wmparc = self.getImage('wmparc', 'resample')

        #Build qa images
        brainMaskQa = self.plot3dVolume(b0, edges=brainMask, fov=brainMask)
        aparcAsegQa = self.plot3dVolume(b0, segOverlay=aparcAseg, fov=brainMask)
        wmparcQa = self.plot3dVolume(b0, segOverlay=wmparc, fov=brainMask)

        qaImages = Images(
            (brainMaskQa, 'Brain mask on upsampled b0'),
            (aparcAsegQa, 'aparcaseg segmentation on upsampled b0'),
            (wmparcQa, 'white matter segmentation on upsampled b0'))

        return qaImages
