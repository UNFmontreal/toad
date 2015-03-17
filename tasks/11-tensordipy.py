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
        GenericTask.__init__(self, subject, 'preprocessing', 'masking')


    def implement(self):

        dwi = self.getImage(self.dependDir, 'dwi', 'upsample')
        bValsFile = self.getImage(self.dependDir, 'grad', None, 'bvals')
        bVecsFile = self.getImage(self.dependDir, 'grad', None, 'bvecs')
        mask = self.getImage(self.maskingDir, 'anat', ['resample', 'extended', 'mask'])

        self.__produceTensors(dwi, bValsFile, bVecsFile, mask)


    def __produceTensors(self, source, bValsFile, bVecsFile, mask):
        self.info("Starting tensors creation from dipy on {}".format(source))
        target = self.buildName(source, "tensor")
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
        nibabel.save(tensorsImage, target)

        nibabel.save(nibabel.Nifti1Image(fit.fa.astype(numpy.float32), dwiImage.get_affine()), self.buildName(target, "fa"))
        nibabel.save(nibabel.Nifti1Image(fit.ad.astype(numpy.float32), dwiImage.get_affine()), self.buildName(target, "ad"))
        nibabel.save(nibabel.Nifti1Image(fit.rd.astype(numpy.float32), dwiImage.get_affine()), self.buildName(target, "rd"))
        nibabel.save(nibabel.Nifti1Image(fit.md.astype(numpy.float32), dwiImage.get_affine()), self.buildName(target, "md"))
        nibabel.save(nibabel.Nifti1Image(fit.evecs[0].astype(numpy.float32), dwiImage.get_affine()), self.buildName(target, "v1"))
        nibabel.save(nibabel.Nifti1Image(fit.evecs[1].astype(numpy.float32), dwiImage.get_affine()), self.buildName(target, "v2"))
        nibabel.save(nibabel.Nifti1Image(fit.evecs[2].astype(numpy.float32), dwiImage.get_affine()), self.buildName(target, "v3"))
        #nibabel.save(nibabel.Nifti1Image(fit.adc(dipy.data.get_sphere('symmetric724')).astype(numpy.float32),
        #                                 dwiImage.get_affine()), self.buildName(target, "adc"))

        faColor = numpy.clip(fit.fa, 0, 1)
        rgb = dipy.reconst.dti.color_fa(faColor, fit.evecs)
        nibabel.save(nibabel.Nifti1Image(numpy.array(255 * rgb, 'uint8'), dwiImage.get_affine()), self.buildName(target, "rgb"))

        self.info("End tensor and metrics creation from dipy, resulting file is {} ".format(target))
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

