import dipy.core.gradients
import dipy.reconst.dti
import dipy.segment.mask
import dipy.reconst.dti
import numpy
import nibabel

from core.generictask import GenericTask
from lib.images import Images

__author__ = 'desmat'

class TensorDipy(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preprocessing', 'masking', 'qa', 'preparation', 'registration')


    def implement(self):

        dwi = self.getImage(self.dependDir, 'dwi', 'upsample')
        bValsFile = self.getImage(self.dependDir, 'grad', None, 'bvals')
        bVecsFile = self.getImage(self.dependDir, 'grad', None, 'bvecs')
        mask = self.getImage(self.maskingDir, 'anat', ['resample', 'extended', 'mask'])

        fit = self.__produceTensors(dwi, bValsFile, bVecsFile, mask)

        #QA
        maskCc = self.__computeCcMask(dwi, mask, fit)
        b0 = self.getImage(self.dependDir, 'b0','upsample')
        brain = self.getImage(self.registrationDir, 'anat', ['brain', 'resample'])
        dwiRaw = self.getImage(self.preparationDir, 'dwi')
 
        maskCcPng = self.buildName(maskCc, None, 'png')
        dwiSnrPng = self.buildName(dwi, 'snr', 'png')
        dwiHistPng = self.buildName(dwi, 'hist', 'png')
        dwiRawSnrPng = self.buildName(dwiRaw, 'snr', 'png')
        dwiRawHistPng = self.buildName(dwiRaw, 'hist', 'png')

        self.slicerPng(b0, maskCcPng, maskOverlay=maskCc)
        self.noiseAnalysis(dwi, brain, maskCc, dwiSnrPng, dwiHistPng)#, targetMaskNoise='maskNoise.png')
        #self.noise(dwiRaw, maskCC, dwiRawSnrPng, dwiRawHistPng)


    def __produceTensors(self, source, bValsFile, bVecsFile, mask):
        self.info("Starting tensors creation from dipy on {}".format(source))
        dwiImage = nibabel.load(source)
        maskImage = nibabel.load(mask)
        maskData = maskImage.get_data()
        dwiData  = dwiImage.get_data()
        dwiData = dipy.segment.mask.applymask(dwiData, maskData)

        gradientTable = dipy.core.gradients.gradient_table(numpy.loadtxt(bValsFile), numpy.loadtxt(bVecsFile))

        model = dipy.reconst.dti.TensorModel(gradientTable)
        fit = model.fit(dwiData)
        tensorsValues = dipy.reconst.dti.lower_triangular(fit.quadratic_form)
        correctOrder = [0,1,3,2,4,5]
        tensorsValuesReordered = tensorsValues[:,:,:,correctOrder]
        tensorsImage = nibabel.Nifti1Image(tensorsValuesReordered.astype(numpy.float32), dwiImage.get_affine())
        nibabel.save(tensorsImage, self.buildName(source, "tensor"))

        nibabel.save(nibabel.Nifti1Image(fit.fa.astype(numpy.float32), dwiImage.get_affine()), self.buildName(source, "fa"))
        nibabel.save(nibabel.Nifti1Image(fit.ad.astype(numpy.float32), dwiImage.get_affine()), self.buildName(source, "ad"))
        nibabel.save(nibabel.Nifti1Image(fit.rd.astype(numpy.float32), dwiImage.get_affine()), self.buildName(source, "rd"))
        nibabel.save(nibabel.Nifti1Image(fit.md.astype(numpy.float32), dwiImage.get_affine()), self.buildName(source, "md"))
        nibabel.save(nibabel.Nifti1Image(fit.evecs[0].astype(numpy.float32), dwiImage.get_affine()), self.buildName(source, "v1"))
        nibabel.save(nibabel.Nifti1Image(fit.evecs[1].astype(numpy.float32), dwiImage.get_affine()), self.buildName(source, "v2"))
        nibabel.save(nibabel.Nifti1Image(fit.evecs[2].astype(numpy.float32), dwiImage.get_affine()), self.buildName(source, "v3"))
        #nibabel.save(nibabel.Nifti1Image(fit.adc(dipy.data.get_sphere('symmetric724')).astype(numpy.float32),
        #                                 dwiImage.get_affine()), self.buildName(target, "adc"))

        faColor = numpy.clip(fit.fa, 0, 1)
        rgb = dipy.reconst.dti.color_fa(faColor, fit.evecs)
        nibabel.save(nibabel.Nifti1Image(numpy.array(255 * rgb, 'uint8'), dwiImage.get_affine()), self.buildName(source, "tensor_rgb"))

        self.info("End tensor and metrics creation from dipy, resulting file is {} ".format(fit))
        return fit


    def __computeCcMask(self, source, mask, fit):
        """
        """
        dwiImage = nibabel.load(source)
        dwiData = dwiImage.get_data()

        maskImage = nibabel.load(mask)
        maskData = maskImage.get_data()

        CC_box = numpy.zeros_like(dwiData[..., 0])
        mins, maxs = dipy.segment.mask.bounding_box(maskData)
        mins = numpy.array(mins)
        maxs = numpy.array(maxs)
        diff = (maxs - mins) // 4
        bounds_min = mins + diff
        bounds_max = maxs - diff
        CC_box[bounds_min[0]:bounds_max[0],
               bounds_min[1]:bounds_max[1],
               bounds_min[2]:bounds_max[2]] = 1
        threshold = (0.6, 1, 0, 0.1, 0, 0.1)
        mask_cc_part, cfa = dipy.segment.mask.segment_from_cfa(fit, CC_box, threshold, return_cfa=True)

        target = self.buildName(source, 'maskccpart')

        nibabel.save(nibabel.Nifti1Image(mask_cc_part.astype(numpy.int), dwiImage.get_affine()), target)

        return target



    def meetRequirement(self):
        images = Images((self.getImage(self.dependDir, 'dwi', 'upsample'), "upsampled diffusion"),
                  (self.getImage(self.dependDir, 'grad', None, 'bvals'), "gradient value bvals encoding file"),
                  (self.getImage(self.dependDir, 'grad', None, 'bvecs'), "gradient vector bvecs encoding file"),
                  (self.getImage(self.maskingDir, 'anat', ['resample', 'extended', 'mask']), 'ultimate extended mask'))
        return images.isAllImagesExists()


    def isDirty(self):
        images = Images((self.getImage(self.workingDir, "dwi", "tensor"), "dipy tensor"),
                     (self.getImage(self.workingDir, 'dwi', 'v1'), "selected eigenvector 1"),
                     (self.getImage(self.workingDir, 'dwi', 'v2'), "selected eigenvector 2"),
                     (self.getImage(self.workingDir, 'dwi', 'v3'), "selected eigenvector 3"),
                     (self.getImage(self.workingDir, 'dwi', 'fa'), "fractional anisotropy"),
                     (self.getImage(self.workingDir, 'dwi', 'md'), "mean diffusivity MD"),
                     (self.getImage(self.workingDir, 'dwi', 'ad'), "selected eigenvalue(s) AD"),
                     (self.getImage(self.workingDir, 'dwi', 'rd'), "selected eigenvalue(s) RD"))
                 #"apparent diffusion coefficient" : self.getImage(self.workingDir, 'dwi', 'adc')}
        return images.isSomeImagesMissing()

    def qaSupplier(self):

        maskCcPng = self.getImage(self.workingDir, 'dwi', 'maskccpart', ext='png')
        dwiSnrPng = self.getImage(self.workingDir, 'dwi', 'snr', ext='png')
        dwiHistPng = self.getImage(self.workingDir, 'dwi', 'hist', ext='png')
        #dwiRawSnrPng = self.getImage(self.workingDir, 'dwi', 'snr', ext='png')
        #dwiRawHistPng = self.getImage(self.workingDir, 'dwi', 'hist', ext='png')

        images =  Images((maskCcPng, 'Corpus callosum mask to compute SNR'),
                         (dwiSnrPng, 'SNR'),
                         (dwiHistPng, 'Noise Histogramme'),
                         #('maskNoise.png', 'Noise Mask')
                         #(dwiRawSnrPng, 'SNR from dwi of preparationDir'),
                         #(dwiRawHistPng, 'Noise Histogramme from dwi of preparationDir'),
                        )
        return images
