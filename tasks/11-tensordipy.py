from lib.generictask import GenericTask
import dipy.core.gradients, dipy.reconst.dti, dipy.segment.mask, dipy.reconst.dti
import numpy, nibabel

__author__ = 'desmat'

class TensorDipy(GenericTask):


    def __init__(self, subject):
        """A preset format, used as a starting point for developing a toad task

        Simply copy and rename this file:  cp xxxxx.template yourtaskname.py into the tasks folder.
            XX is simply a 2 digit number that represent the order the tasks will be executed.
            yourtaskname is any name at your convenience. the name must be lowercase
        Change the class name Template for Yourtaskname. Note the first letter of the name should be capitalized

        A directory called XX-yourtaskname will be create into the subject dir. A local variable self.workingDir will
        be initialize to that directory

        Args:
            subject: a Subject instance inherit by the subjectmanager.

        """

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
        images = {"upsampled diffusion":self.getImage(self.dependDir, 'dwi', 'upsample'),
                  "gradient value bvals encoding file":  self.getImage(self.dependDir, 'grad', None, 'bvals'),
                  "gradient vector bvecs encoding file":  self.getImage(self.dependDir, 'grad', None, 'bvecs'),
                  'ultimate extended mask':  self.getImage(self.maskingDir, 'anat', ['resample', 'extended', 'mask'])}
        return self.isAllImagesExists(images)


    def isDirty(self):
        images ={"dipy tensor": self.getImage(self.workingDir, "dwi", "tensor"),
                    "selected eigenvector 1" : self.getImage(self.workingDir, 'dwi', 'v1'),
                    "selected eigenvector 2" : self.getImage(self.workingDir, 'dwi', 'v2'),
                    "selected eigenvector 3" : self.getImage(self.workingDir, 'dwi', 'v3'),
                    "fractional anisotropy" : self.getImage(self.workingDir, 'dwi', 'fa'),
                    "mean diffusivity MD" : self.getImage(self.workingDir, 'dwi', 'md'),
                    "selected eigenvalue(s) AD" : self.getImage(self.workingDir, 'dwi', 'ad'),
                    "selected eigenvalue(s) RD" : self.getImage(self.workingDir, 'dwi', 'rd')}
                    #"apparent diffusion coefficient" : self.getImage(self.workingDir, 'dwi', 'adc')}
        return self.isSomeImagesMissing(images)

