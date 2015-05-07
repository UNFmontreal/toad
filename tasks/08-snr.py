from core.generictask import GenericTask
from lib.images import Images
import nibabel
import scipy.ndimage.morphology
__author__ = 'cbedetti'


class Snr(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preparation', 'parcellation', 'eddy', 'fieldmap', 'denoising', 'qa')


    def implement(self):
        dwiPreparation = self.getImage(self.preparationDir, 'dwi')
        dwiUnwarp = self.__getUnwarpImage()
        dwiDenoising = self.getImage(self.denoisingDir, 'dwi', 'denoise')

        b0 = self.getImage(self.dependDir, 'b0','upsample')
        brain = self.getImage(self.registrationDir, 'anat', ['brain', 'resample'])
        maskCc = self.__computeCcMask(dwi, mask, fit)
        maskNoise = self.__computeNoiseMask(self, brain)

        #QA
        dwiPreparationSnrPng = self.buildName(dwi, 'snr', 'png')
        dwiPreparationHistPng = self.buildName(dwi, 'hist', 'png')
        dwiUnwarpSnrPng = self.buildName(dwiRaw, 'snr', 'png')
        dwiUnwarpHistPng = self.buildName(dwiRaw, 'hist', 'png')
        dwiDenoisingSnrPng = self.buildName(dwiRaw, 'snr', 'png')
        dwiDenoisingHistPng = self.buildName(dwiRaw, 'hist', 'png')

        maskCcPng = self.buildName(maskCc, None, 'png')
        maskNoisePng = 

        self.noiseAnalysis(dwiPreparation, maskNoise, maskCc, dwiPreparationSnrPng, dwiPreparationHistPng)
        if dwiUnwarp:
            self.noiseAnalysis(dwiUnwarp, maskNoise, maskCc, dwiUnwarpSnrPng, dwiUnwarpHistPng)
        if dwiDenoising:
            self.noiseAnalysis(dwiDenoising, maskNoise, maskCc, dwiDenoisingSnrPng, dwiDenoisingHistPng)
        self.slicerPng(b0, maskCcPng, maskOverlay=maskCc)
        self.slicerPng(b0, maskNoisePng, maskOverlay=maskNoise)


    def __getUnwarpImage(self):
        dwi = self.getImage(self.fieldmapDir, 'dwi', 'unwarp')
        if not dwi:
            dwi = self.getImage(self.eddyDir, 'dwi', 'eddy'):
        return dwi


    def __computeNoiseMask(self, brain):
        """
        """
        target = 'mask_noise.nii.gz'
        brainImage = nibabel.load(brain)
        brainData = brainImage.get_data()
        brainData[brainData>0] = 1
        maskNoise = scipy.ndimage.morphology.binary_dilation(brainData, iterations=10)
        maskNoise[..., :maskNoise.shape[-1]//2] = 1
        maskNoise = ~maskNoise
        mask_noise_img = nibabel.Nifti1Image(mask_noise.astype(np.uint8), affine)
        nibabel.save(mask_noise_img, target)
        return target


    def meetRequirement(self):
        """Validate if all requirements have been met prior to launch the task

        Returns:
            True if all requirement are meet, False otherwise
        """
        images = Images((self.getImage(self.preparationDir, 'dwi'), 'diffusion weighted'),
                        (, 'aparc_aseg from freesurfer'),
                        (, 'Brain mask')
                       )
        return images.isAllImagesExists()


    def isDirty(self):
        """Validate if this tasks need to be submit during the execution

        Returns:
            True if any expected file or resource is missing, False otherwise
        """
        images = Images((self.getImage(self.workingDir, 'dwi', 'snr', ext='png'), 'SNR of the raw DWI'),
                        (self.getImage(self.workingDir, 'dwi', 'hist', ext='png'), 'Noise histogram for the raw DWI'),
                        (self.getImage(self.workingDir, 'dwi', 'maskccpart', ext='png'), 'Corpus callosum mask')
                       )
        return images.isSomeImagesMissing()


    def qaSupplier(self):
        dwiPreparationSnrPng = self.getImage(self.workingDir, 'dwi', 'snr', ext='png')
        dwiPreparationHistPng = self.getImage(self.workingDir, 'dwi', 'hist', ext='png')
        images = Image((dwiPreparationSnrPng, 'SNR for each volume of the raw DWI'),
                       (dwiPreparationHistPng, 'Noise histogram for the raw DWI'))

        dwiUnwarpSnrPng = self.getImage(self.workingDir, 'dwi', ['denoise', 'snr'], ext='png')
        dwiUnwarpHistPng = self.getImage(self.workingDir, 'dwi', 'hist', ext='png')
        if dwiUnwarpSnrPng:
            images.extend((dwiUnwarpSnrPng, 'SNR for each volume of the unwarped DWI'),
                          (dwiUnwarpHistPng, 'Noise histogram for the unwarped DWI'))

        if not(self.config.get('denoising', 'algorithm').lower() in 'none'):
            dwiDenoisingSnrPng = self.getImage(self.workingDir, 'dwi', ['denoise', 'snr'], ext='png')
            dwiDenoisingHistPng = self.getImage(self.workingDir, 'dwi',['denoise', 'hist'], ext='png')
            images.extend((dwiDenoisingSnrPng, 'SNR for each volume of the unwarped DWI'),
                          (dwiDenoisingHistPng, 'Noise histogram for the unwarped DWI'))

        maskCcPng = self.getImage(self.workingDir, 'dwi', 'maskccpart', ext='png')
        maskNoisePng
        images.extend((maskCcPng, 'Corpus callosum mask to compute SNR'),
                      (maskNoisePng, 'Noise mask to compute SNR'))

        return images

