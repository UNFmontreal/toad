import os

import dipy.denoise.noise_estimate
import dipy.denoise.nlmeans
import nibabel
import numpy

from core.generictask import GenericTask
from lib.images import Images
from lib import util, mriutil


__author__ = 'desmat'

class Denoising(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'correction', 'preparation', 'parcellation', 'qa')
        self.matlabWarning = False
        self.sigmaVector = None


    def implement(self):

        dwi = self.__getDwiImage()
        bVals = self.__getBValsImage()
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
                                                    self.buildName(parcellationMask, 'temporary'),
                                                    extraArgs)

        target = self.buildName(dwi, "denoise")

        if self.get("algorithm") == "nlmeans":

            dwiImage = nibabel.load(dwi)
            dwiData  = dwiImage.get_data()
            self.sigmaVector, sigma, maskNoise = self.__computeSigmaAndNoiseMask(dwiData)
            self.info("sigma value that will be apply into nlmeans = {}".format(sigma))

            denoisingData = dipy.denoise.nlmeans.nlmeans(dwiData, sigma)
            nibabel.save(nibabel.Nifti1Image(denoisingData.astype(numpy.float32), dwiImage.get_affine()), target)
            nibabel.save(nibabel.Nifti1Image(maskNoise.astype(numpy.float32),
                                             dwiImage.get_affine()), self.buildName(target, "noise_mask"))

        elif self.get('general', 'matlab_available'):
            dwi = self.__getDwiImage()
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


    def __getDwiImage(self):
        if self.getCorrectionImage("dwi", 'corrected'):
            return self.getCorrectionImage("dwi", 'corrected')
        else:
            return self.getPreparationImage("dwi")


    def __getBValsImage(self):
        if self.getCorrectionImage('grad',  None, 'bvals'):
            return self.getCorrectionImage('grad',  None, 'bvals')
        else:
            return self.getPreparationImage('grad',  None, 'bvals')



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
            template = self.parseTemplate(tags, os.path.join(self.toadDir, "templates", "files", "denoise_aonlm.tpl"))
        else:
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
        sigmaMatrix = numpy.zeros_like(data, dtype=numpy.float32)
        sigmaVector = numpy.zeros(data.shape[2], dtype=numpy.float32)
        maskNoise = numpy.zeros(data.shape[:-1], dtype=numpy.bool)


        for idx in range(data.shape[2]):
            sigmaMatrix[:, :, idx], maskNoise[:, :, idx] = dipy.denoise.noise_estimate.piesno(data[:, :, idx],
                                                                                         N=numberArrayCoil,
                                                                                         return_mask=True)
            sigmaVector[idx] = sigmaMatrix[0,0,idx,0]
        return sigmaVector, numpy.median(sigmaVector), maskNoise


    def isIgnore(self):
        return  self.get("ignore")


    def meetRequirement(self, result = True):
        images = Images((self.getCorrectionImage("dwi", 'corrected'), 'corrected'),
                       (self.getPreparationImage("dwi"), 'diffusion weighted'))

        if not images.isAtLeastOneImageExists():
            return False

        images = Images((self.getParcellationImage('norm'), 'freesurfer normalize'),
                        (self.getParcellationImage('mask'), 'freesurfer mask'))

        return images


    def isDirty(self):
        return Images((self.getImage("dwi", 'denoise'), 'denoised'))


    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        qaImages = Images()
        algorithm = self.get("algorithm")

        #Information on denoising algorithm
        information = 'Algorithm {} is set'.format(algorithm)
        if self.matlabWarning:
            information += ' but matlab is not available on this server'
        qaImages.setInformation(information)

        #Get images
        dwi = self.__getDwiImage()
        dwiDenoised = self.getImage('dwi', 'denoise')
        brainMask = self.getCorrectionImage('mask', 'corrected')
        b0 = self.getCorrectionImage('b0', 'corrected')
        noiseMask = self.getImage('dwi', 'noise_mask')

        #Build qa images
        if dwiDenoised:
            dwiDenoisedGif = self.buildName(dwiDenoised, None, 'gif')
            dwiCompareGif = self.buildName(dwiDenoised, 'compare', 'gif')
            self.slicerGif(dwiDenoised, dwiDenoisedGif, boundaries=brainMask)
            self.slicerGifCompare(dwi, dwiDenoised, dwiCompareGif, boundaries=brainMask)
            qaImages.extend(Images(
                (dwiDenoisedGif, 'Denoised diffusion image'),
                (dwiCompareGif, 'Before and after denoising'),
                ))

            if algorithm == "nlmeans":
                sigmaPng = self.buildName(dwiDenoised, 'sigma', 'png')
                noiseMaskPng = self.buildName(noiseMask, None, 'png')
                self.plotSigma(self.sigmaVector, sigmaPng)
                self.slicerPng(b0, noiseMaskPng, maskOverlay=noiseMask, boundaries=noiseMask)
                qaImages.extend(Images(
                    (sigmaPng, 'Sigmas from nlmeans algorithm'),
                    (noiseMaskPng, 'Noise mask from nlmeans algorithm'),
                    ))

        return qaImages
