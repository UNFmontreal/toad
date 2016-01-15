# -*- coding: utf-8 -*-
import os

import numpy
import nibabel
import dipy.denoise.nlmeans
import dipy.denoise.noise_estimate

from core.toad.generictask import GenericTask
from lib.images import Images
from lib import util, mriutil


__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class Denoising(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject,'preparation', 'parcellation', 'qa')
        self.matlabWarning = False
        self.sigmaVector = None
        self.algorithm = None


    def implement(self):


        dwi = self.getPreparationImage("dwi")
        bVals = self.getPreparationImage('grad',  None, 'bvals')
        norm=   self.getParcellationImage('norm')
        parcellationMask = self.getParcellationImage('mask')

        b0 = os.path.join(self.workingDir, os.path.basename(dwi).replace(self.get("prefix", 'dwi'), self.get("prefix", 'b0')))
        self.info(mriutil.extractFirstB0FromDwi(dwi, b0, bVals))

        self.info("create a suitable mask for the dwi")
        extraArgs = ""
        if self.get("parcellation", "intrasubject"):
            extraArgs += " -usesqform -dof 6"

        mask = mriutil.computeDwiMaskFromFreesurfer(b0,
                                                    norm,
                                                    parcellationMask,
                                                    self.buildName(parcellationMask, 'resample'),
                                                    extraArgs)


        target = self.buildName(dwi, "denoise")

        if self.get("algorithm") == "nlmeans":

            self.algorithm = "nlmeans"
            dwiImage = nibabel.load(dwi)
            dwiData  = dwiImage.get_data()
            if self.get('number_array_coil') == "32":
                noiseMask = mriutil.computeNoiseMask(mask, self.buildName(mask, 'noise_mask'))
                noiseMaskImage = nibabel.load(noiseMask)
                noiseMaskData  = noiseMaskImage.get_data()
                sigma = numpy.std(dwiData[noiseMaskData > 0])
                self.info("sigma value that will be apply into nlmeans = {}".format(sigma))
                denoisingData = dipy.denoise.nlmeans.nlmeans(dwiData, sigma)

            else:
                self.sigmaVector, sigma, piesnoNoiseMask = self.__computeSigmaAndNoiseMask(dwiData)
                self.info("sigma value that will be apply into nlmeans = {}".format(sigma))
                denoisingData = dipy.denoise.nlmeans.nlmeans(dwiData, sigma)
                nibabel.save(nibabel.Nifti1Image(piesnoNoiseMask.astype(numpy.float32),dwiImage.get_affine()), self.buildName(target, "piesno_noise_mask"))

            nibabel.save(nibabel.Nifti1Image(denoisingData.astype(numpy.float32), dwiImage.get_affine()), target)

        elif self.get('general', 'matlab_available'):
            dwiUncompress = self.uncompressImage(dwi)

            tmp = self.buildName(dwiUncompress, "tmp", 'nii')
            scriptName = self.__createMatlabScript(dwiUncompress, tmp)
            self.__launchMatlabExecution(scriptName)

            self.info("compressing {} image".format(tmp))
            tmpCompress = util.gzip(tmp)
            self.rename(tmpCompress, target)

            if self.get("cleanup"):
                self.info("Removing redundant image {}".format(dwiUncompress))
                os.remove(dwiUncompress)
        else:
            self.matlabWarning = True
            self.warning("Algorithm {} is set but matlab is not available for this server.\n"
                         "Please configure matlab or set denoising algorithm to nlmeans or none"
                         .format(self.get("algorithm")))

    def __createMatlabScript(self, source, target):

        scriptName = os.path.join(self.workingDir, "{}.m".format(self.get("script_name")))
        self.info("Creating denoising script {}".format(scriptName))
        tags={ 'source': source,
               'target': target,
               'workingDir': self.workingDir,
               'beta': self.get('beta'),
               'rician': self.get('rician'),
               'nbthreads': self.getNTreadsDenoise()}

        if self.get("algorithm") == "aonlm":
            self.algorithm = "aonlm"
            template = self.parseTemplate(tags, os.path.join(self.toadDir, "templates", "files", "denoise_aonlm.tpl"))
        else:
            self.algorithm = "lpca"
            template = self.parseTemplate(tags, os.path.join(self.toadDir, "templates", "files", "denoise_lpca.tpl"))

        util.createScript(scriptName, template)
        return scriptName


    def __launchMatlabExecution(self, pyscript):

        self.info("Launch DWIDenoisingLPCA from matlab.")
        self.launchMatlabCommand(pyscript, None, None, 10800)


    def __computeSigmaAndNoiseMask(self, data):
        """Use piesno algorithm to estimate sigma and noise

        Args:
            data: A dMRI 4D matrix

        Returns:
            a list of float representing sigmas for each z slices
            a float representing sigma "The estimated standard deviation of the gaussian noise"
            and a mask identyfing all the pure noise voxel that were found.
        """

        try:
            numberArrayCoil = int(self.get("number_array_coil"))
        except ValueError:
            numberArrayCoil = 1
        sigmaVector = numpy.zeros(data.shape[2], dtype=numpy.float32)

        sigmaMatrix, maskNoise = dipy.denoise.noise_estimate.piesno(data, N=numberArrayCoil, return_mask=True)
        return sigmaVector, sigmaMatrix, maskNoise


    def isIgnore(self):
        return  self.get("ignore")


    def meetRequirement(self, result = True):
        images = Images((self.getPreparationImage("dwi"), 'diffusion weighted'),
                        (self.getParcellationImage('norm'), 'freesurfer normalize'),
                        (self.getParcellationImage('mask'), 'freesurfer mask'))

        return images


    def isDirty(self):
        return Images((self.getImage("dwi", 'denoise'), 'denoised'))


    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        qaImages = Images()

        #Information on denoising algorithm
        information = 'Denoising was done using the {} algorithm'.format(self.algorithm)

        if self.algorithm == "nlmeans" and \
            self.config.get("denoising", "number_array_coil") == "32":
            information = "NLMEANS algorithm is not yet implemented for 32 " \
                "coils channels images, "
            if self.config.getboolean("general", "matlab_available"):
                information += "set algorithm to `lpca` or `aonlm` or "
            information += "set `ignore: True` into the [denoising] section " \
                    "of your config.cfg file."

        if self.matlabWarning:
            information = "Algorithm `aonlm` or `lpca` was set for the " \
                    "denoising, but Matlab is not available for this server. "\
                    "Please install and configure Matlab or set `ignore: True`"\
                    " into the [denoising] section of your config.cfg file."
            qaImages.extend(Images((False, 'Denoised diffusion image')))

        qaImages.setInformation(information)

        #Get images
        dwi = self.getPreparationImage("dwi")
        dwiDenoised = self.getImage('dwi', 'denoise')
        brainMask = self.getImage('mask', 'resample')
        b0 = self.getImage('b0')
        noiseMask = self.getImage('dwi', 'noise_mask')

        #Build qa images
        if dwiDenoised:

            dwiDenoisedQa = self.plot4dVolume(dwiDenoised, fov=brainMask)
            qaImages.append((dwiDenoisedQa, 'Denoised diffusion image'))

            dwiCompareQa = self.compare4dVolumes(
                    dwi, dwiDenoised, fov=brainMask)
            qaImages.append((dwiCompareQa, 'Before and after denoising'))

            if self.algorithm == "nlmeans":
                if self.sigmaVector != None:
                    sigmaQa = self.plotSigma(self.sigmaVector, dwiDenoised)
                    qaImages.append(
                            (sigmaQa, 'Sigmas from the nlmeans algorithm'))

                if noiseMask:
                    noiseMaskQa = self.plot3dVolume(
                            b0, edges=noiseMask, fov=noiseMask)
                    qaImages.append(
                            (noiseMaskQa, 'Noise mask from the nlmeans algorithm'))

        return qaImages
