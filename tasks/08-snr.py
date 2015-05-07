from core.generictask import GenericTask
from lib.images import Images
from lib import mriutil
import os
import nibabel
import numpy
import scipy.ndimage.morphology
__author__ = 'cbedetti'


class Snr(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preparation', 'parcellation', 'eddy', 'fieldmap',
                                            'denoising', 'registration', 'masking', 'qa')


    def implement(self):
        dwiPreparation = self.getImage(self.preparationDir, 'dwi')
        dwiUnwarp = self.__getUnwarpImage()
        dwiDenoising = self.getImage(self.denoisingDir, 'dwi', 'denoise')

        bVals= self.getImage(self.preparationDir, 'grad', None, 'bvals')
        if not bVals:
            bVals= self.getImage(self.eddyDir, 'grad', None, 'bvals')

        b0 = os.path.join(self.workingDir,
                          os.path.basename(dwiPreparation).replace(self.config.get("prefix", 'dwi'), self.config.get("prefix", 'b0')))
        self.info(mriutil.extractFirstB0FromDwi(dwiPreparation, b0, bVals))
        brain = self.getImage(self.registrationDir, 'anat', ['brain', 'resample'])
        #aparcAseg = self.getImage(self.registrationDir, 'aparc_aseg', 'resample')
        maskCc = self.getImage(self.maskingDir, 'aparc_aseg',['253','mask'])

        #self.info(mriutil.mrcalc(aparcAseg, '253', self.buildName('aparc_aseg', ['253','mask'], 'nii.gz')))

        maskCc2mm = self.__resampling(maskCc, b0)
        brain2mm = self.__resampling(brain, b0)
        maskNoise2mm = self.__computeNoiseMask(brain2mm)

        #QA
        dwiPreparationSnrPng = self.buildName(dwiPreparation, ['native', 'snr'], 'png')
        dwiPreparationHistPng = self.buildName(dwiPreparation, ['native', 'hist'], 'png')
        dwiUnwarpSnrPng = self.buildName(dwiUnwarp, 'snr', 'png')
        dwiUnwarpHistPng = self.buildName(dwiUnwarp, 'hist', 'png')
        dwiDenoisingSnrPng = self.buildName(dwiDenoising, 'snr', 'png')
        dwiDenoisingHistPng = self.buildName(dwiDenoising, 'hist', 'png')

        maskCcPng = self.buildName(maskCc2mm, None, 'png')
        maskNoisePng = self.buildName(maskNoise2mm, None, 'png')

        self.noiseAnalysis(dwiPreparation, maskNoise2mm, maskCc2mm, dwiPreparationSnrPng, dwiPreparationHistPng)
        if dwiUnwarp:
            self.noiseAnalysis(dwiUnwarp, maskNoise2mm, maskCc2mm, dwiUnwarpSnrPng, dwiUnwarpHistPng)
        if dwiDenoising:
            self.noiseAnalysis(dwiDenoising, maskNoise2mm, maskCc2mm, dwiDenoisingSnrPng, dwiDenoisingHistPng)
        self.slicerPng(b0, maskCcPng, maskOverlay=maskCc2mm, boundaries=maskCc2mm)
        self.slicerPng(b0, maskNoisePng, maskOverlay=maskNoise2mm, boundaries=maskNoise2mm, vmax=100)


    def __getUnwarpImage(self):
        dwi = self.getImage(self.fieldmapDir, 'dwi', 'unwarp')
        if not dwi:
            dwi = self.getImage(self.eddyDir, 'dwi', 'eddy')
        return dwi


    def __computeNoiseMask(self, brain):
        """
        """
        target = self.buildName(brain, 'mask_noise')
        brainImage = nibabel.load(brain)
        brainData = brainImage.get_data()
        brainData[brainData>0] = 1
        maskNoise = scipy.ndimage.morphology.binary_dilation(brainData, iterations=25)
        maskNoise[..., :maskNoise.shape[-1]//2] = 1
        maskNoise = ~maskNoise
        nibabel.save(nibabel.Nifti1Image(maskNoise.astype(numpy.uint8), brainImage.get_affine()), target)
        return target


    def __resampling(self, source, template):
        """Upsample an image specify as input

        The upsampling value should be specified into the config.cfg file

        Args:
            source: The input file
            voxelSize: Size of the voxel

        Return:
            The resulting output file name
        """
        self.info("Launch resampling on {}.\n".format(source))
        target = self.buildName(source, '2x2x2')
        #if len(voxelSize.strip().split(" "))!=3:
        #    self.warning("Voxel size not specified correctly during upsampling")

        #cmd = "mri_convert -voxsize {} --input_volume {} --output_volume {}".format(voxelSize, source, target)
        cmd = "mrtransform -oversample 2,2,2 -template {} {} {}".format(template, source, target)
        self.launchCommand(cmd)
        return target


    def meetRequirement(self):
        """Validate if all requirements have been met prior to launch the task

        Returns:
            True if all requirement are meet, False otherwise
        """
        images = Images((self.getImage(self.preparationDir, 'dwi'), 'diffusion weighted'),
                        (self.getImage(self.registrationDir, 'anat', ['brain', 'resample']), 'Brain image from bet'),
                        (self.getImage(self.maskingDir, 'aparc_aseg',['253','mask']), 'Corpus Callusum mask from masking task'),
                       )
        return images.isAllImagesExists()


    def isDirty(self):
        """Validate if this tasks need to be submit during the execution

        Returns:
            True if any expected file or resource is missing, False otherwise
        """
        images = Images((self.getImage(self.workingDir, 'dwi', ['native', 'snr'], ext='png'), 'SNR of the raw DWI'),
                        (self.getImage(self.workingDir, 'dwi', ['native', 'hist'], ext='png'), 'Noise histogram for the raw DWI'),
                       )
        return images.isSomeImagesMissing()


    def qaSupplier(self):
        dwiPreparationSnrPng = self.getImage(self.workingDir, 'dwi', ['native', 'snr'], ext='png')
        dwiPreparationHistPng = self.getImage(self.workingDir, 'dwi', ['native', 'hist'], ext='png')
        images = Images((dwiPreparationSnrPng, 'SNR for each volume of the raw DWI'),
                        (dwiPreparationHistPng, 'Noise histogram for the raw DWI'))

        dwiUnwarpSnrPng = self.getImage(self.workingDir, 'dwi', ['eddy', 'snr'], ext='png')
        dwiUnwarpHistPng = self.getImage(self.workingDir, 'dwi', ['eddy', 'hist'], ext='png')
        if dwiUnwarpSnrPng:
            images.extend(Images((dwiUnwarpSnrPng, 'SNR for each volume of the unwarped DWI'),
                                 (dwiUnwarpHistPng, 'Noise histogram for the unwarped DWI'),
                                )
                         )

        if not(self.config.get('denoising', 'algorithm').lower() in 'none'):
            dwiDenoisingSnrPng = self.getImage(self.workingDir, 'dwi', ['denoise', 'snr'], ext='png')
            dwiDenoisingHistPng = self.getImage(self.workingDir, 'dwi',['denoise', 'hist'], ext='png')
            images.extend(Images((dwiDenoisingSnrPng, 'SNR for each volume of the denoised DWI'),
                                 (dwiDenoisingHistPng, 'Noise histogram for the denoised DWI'),
                                )
                         )

        maskCcPng = self.getImage(self.workingDir, 'aparc_aseg',['253','mask','2x2x2'], ext='png')
        maskNoisePng = self.getImage(self.workingDir, 'anat', 'mask_noise', ext='png')
        images.extend(Images((maskCcPng, 'Corpus callosum mask to compute SNR'),
                             (maskNoisePng, 'Noise mask to compute SNR'),
                            )
                     )

        return images
