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
        GenericTask.__init__(self, subject, 'preparation', 'parcellation', 'eddy',
                                            'denoising', 'registration', 'masking', 'qa')


    def implement(self):
        dwiNative = self.getImage(self.preparationDir, 'dwi')

        #Extract b0 from dwiNative
        bVals= self.getImage(self.preparationDir, 'grad', None, 'bvals')
        if not bVals:
            bVals= self.getImage(self.eddyDir, 'grad', None, 'bvals')
        b0Basename = os.path.basename(dwiNative).replace(self.get('prefix', 'dwi'), self.get('prefix', 'b0'))
        b0 = os.path.join(self.workingDir, b0Basename)
        self.info(mriutil.extractFirstB0FromDwi(dwiNative, b0, bVals))

        #Brain in native space
        #brainResample = self.getImage(self.registrationDir, 'anat', ['brain', 'resample'])
        #brainNative = self.__resampling(brainResample, b0)

        maskBrain = self.getImage(self.registrationDir, 'mask', 'resample')

        #Noise mask computation
        #dwiNativeNoiseMask = self.__computeNoiseMask(brainNative)

        #Corpus Callosum mask computation
        #aparcAseg = self.getImage(self.registrationDir, 'aparc_aseg', 'resample')
        #self.info(mriutil.mrcalc(aparcAseg, '253', self.buildName('aparc_aseg', ['253', 'mask'], 'nii.gz')))
        cCResample = self.getImage(self.maskingDir, 'aparc_aseg', ['253', 'mask'])
        dwiNativeCcMask = self.__resampling(cCResample, b0)


    def __getUnwarpImage(self):
        dwi = self.getImage(self.eddyDir, 'dwi', 'unwarp')
        if not dwi:
            dwi = self.getImage(self.eddyDir, 'dwi', 'eddy')
        return dwi


    def __computeNoiseMask(self, brain):
        target = self.buildName(brain, 'noisemask')
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
        target = self.buildName(source, 'native')
        #if len(voxelSize.strip().split(" "))!=3:
        #    self.warning("Voxel size not specified correctly during upsampling")

        #cmd = "mri_convert -voxsize {} --input_volume {} --output_volume {}".format(voxelSize, source, target)
        cmd = "mrtransform -oversample 2,2,2 -template {} {} {} -quiet".format(template, source, target)
        self.launchCommand(cmd)
        return target


    def __oddEvenNumberOfSlices(self, *args):
        """return a list of images that will count a odd number of slices in z direction

            If an even number of slices is found, the upper volume will be remove

        Args:
            *args: a list of images

        Returns:
             a list of images stripped

        """
        output = []
        for image in args:
            if image:
                try:
                    zDims = int(mriutil.getMriDimensions(image)[2])
                    if zDims%2 == 1:
                        target = self.buildName(image, "subset")
                        mriutil.extractSubVolume(image, target, '+2',"0:{}".format(zDims-2), self.getNTreadsMrtrix())
                        output.append(target)
                    else:
                        output.append(image)
                except ValueError:
                    output.append(image)
            else:
                output.append(False)
        return output


    def meetRequirement(self):
        """Validate if all requirements have been met prior to launch the task

        Returns:
            True if all requirement are meet, False otherwise
        """
        return Images((self.getImage(self.preparationDir, 'dwi'), 'diffusion weighted'),
                        (self.getImage(self.registrationDir, 'mask', 'resample'), 'brain mask'),
                        (self.getImage(self.maskingDir, 'aparc_aseg',['253','mask']), 'Corpus Callusum mask from masking task'))


    def isDirty(self):
        """Validate if this tasks need to be submit during the execution

        Returns:
            True if any expected file or resource is missing, False otherwise
        """
        #return Images((self.getImage(self.workingDir, 'dwi', ['native', 'snr'], ext='png'), 'SNR of the raw DWI'),
        #                (self.getImage(self.workingDir, 'dwi', ['native', 'hist'], ext='png'), 'Noise histogram for the raw DWI'),
        #               )
	return False
    """
    def qaSupplier(self):
        dwiNative = self.getImage(self.preparationDir, 'dwi')
        dwiUnwarp = self.__getUnwarpImage()
        dwiDenoising = self.getImage(self.denoisingDir, 'dwi', 'denoise')
        dwiNativeNoiseMask = self.getImage(self.workingDir, 'anat', 'noisemask')
        dwiNativeCcMask = self.getImage(self.workingDir, 'aparc_aseg', 'native')
        b0 = self.getImage(self.workingDir, 'b0')

        dwiNativeSnrPng = self.buildName(dwiNative, ['native', 'snr'], 'png')
        dwiNativeHistPng = self.buildName(dwiNative, ['native', 'hist'], 'png')
        self.noiseAnalysis(dwiNative, dwiNativeNoiseMask, dwiNativeCcMask, dwiNativeSnrPng, dwiNativeHistPng)
        images = Images((dwiNativeSnrPng, 'SNR for each volume of the native DWI image'),
                        (dwiNativeHistPng, 'Noise histogram for the native DWI image'))

        if dwiUnwarp:
            dwiUnwarpNoiseMask, dwiUnwarpCcMask = self.__oddEvenNumberOfSlices(dwiNativeNoiseMask, dwiNativeCcMask)
            dwiUnwarpSnrPng = self.buildName(dwiUnwarp, 'snr', 'png')
            dwiUnwarpHistPng = self.buildName(dwiUnwarp, 'hist', 'png')
            self.noiseAnalysis(dwiUnwarp, dwiUnwarpNoiseMask, dwiUnwarpCcMask, dwiUnwarpSnrPng, dwiUnwarpHistPng)
            images.extend(Images((dwiUnwarpSnrPng, 'SNR for each volume of the unwarped DWI'),
                                 (dwiUnwarpHistPng, 'Noise histogram for the unwarped DWI')))

        if dwiDenoising:
            dwiDenoisingNoiseMask, dwiDenoisingCcMask = self.__oddEvenNumberOfSlices(dwiNativeNoiseMask, dwiNativeCcMask)
            dwiDenoisingSnrPng = self.buildName(dwiDenoising, 'snr', 'png')
            dwiDenoisingHistPng = self.buildName(dwiDenoising, 'hist', 'png')
            self.noiseAnalysis(dwiDenoising, dwiDenoisingNoiseMask, dwiDenoisingCcMask, dwiDenoisingSnrPng, dwiDenoisingHistPng)
            images.extend(Images((dwiDenoisingSnrPng, 'SNR for each volume of the denoised DWI'),
                                 (dwiDenoisingHistPng, 'Noise histogram for the denoised DWI')))

        maskNoisePng = self.buildName(dwiNativeNoiseMask, None, 'png')
        maskCcPng = self.buildName(dwiNativeCcMask, None, 'png')
        self.slicerPng(b0, maskCcPng, maskOverlay=dwiNativeCcMask, boundaries=dwiNativeCcMask)
        self.slicerPng(b0, maskNoisePng, maskOverlay=dwiNativeNoiseMask, boundaries=dwiNativeNoiseMask, vmax=100)
        images.extend(Images((maskCcPng, 'Corpus callosum mask to compute SNR'),
                             (maskNoisePng, 'Noise mask to compute SNR')))

        return images
    """
