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
        bValFile = self.getImage(self.dependDir, 'grad', None, 'bval')
        bVecFile = self.getImage(self.dependDir, 'grad', None, 'bvec')
        mask = self.getImage(self.maskingDir, 'anat', ['extended', 'mask'])

        self.__produceTensors(dwi, bValFile, bVecFile, mask)


    def __produceTensors(self, source, bValFile, bVecFile, mask):
        self.info("Starting tensors creation from dipy on {}".format(source))
        target = self.buildName(source, "dipy")
        dwiImage = nibabel.load(source)
        maskImage = nibabel.load(mask)
        maskData = maskImage.get_data()
        dwiData  = dwiImage.get_data()
        dwiData = dipy.segment.mask.applymask(dwiData, maskData)

        gradientTable = dipy.core.gradients.gradient_table(numpy.loadtxt(bValFile), numpy.loadtxt(bVecFile))

        model = dipy.reconst.dti.TensorModel(gradientTable)
        fit = model.fit(dwiData)
        tensorsValues = dipy.reconst.dti.lower_triangular(fit.quadratic_form)
        correctOrder = [0,1,3,2,4,5]
        tensorsValuesReordered = tensorsValues[:,:,:,correctOrder]
        tensorsImage = nibabel.Nifti1Image(tensorsValuesReordered.astype(numpy.float32), dwiImage.get_affine())
        nibabel.save(tensorsImage, target)

        fa = dipy.reconst.dti.fractional_anisotropy(fit.evals)
        fa[numpy.isnan(fa)] = 0


        faImage = nibabel.Nifti1Image(fa.astype(numpy.float32), dwiImage.get_affine())
        nibabel.save(faImage, self.buildName(target, "fa"))

        md = dipy.reconst.dti.mean_diffusivity(fit.evals)
        nibabel.save(nibabel.Nifti1Image(md.astype(numpy.float32), dwiImage.get_affine()), self.buildName(target, "md"))

        #@TODO implement values and tendors creations
        [values, vectors] = dipy.reconst.dti.decompose_tensor(tensorsValuesReordered)

        faColor = numpy.clip(fa, 0, 1)
        rgb = dipy.reconst.dti.color_fa(faColor, fit.evecs)
        nibabel.save(nibabel.Nifti1Image(numpy.array(255 * rgb, 'uint8'), dwiImage.get_affine()), self.buildName(target, "rgb"))

        self.info("End tensor and metrics creation from dipy, resulting file is {} ".format(target))
        return target


    def meetRequirement(self):
        images = {"upsampled diffusion":self.getImage(self.dependDir, 'dwi', 'upsample'),
                  "gradient value bval encoding file":  self.getImage(self.dependDir, 'grad', None, 'bval'),
                  "gradient vector bvec encoding file":  self.getImage(self.dependDir, 'grad', None, 'bvec'),
                  'ultimate extended mask':  self.getImage(self.maskingDir, 'anat', ['extended', 'mask'])}

        return self.isSomeImagesMissing(images)


    def isDirty(self):
        return True
        #@Impelement that
        #images ={"dipy tensor": self.getImage(self.workingDir, "dwi", "dipy")}
        #return self.isSomeImagesMissing(images)

        #@TODO see with Arnaud for that feature
        #if not self.getImage(self.workingDir, 'dwi', ['dipy', 'mask']):
        #    self.info("No dipy tensor mask found in directory {}"{}elf.workingDir)
        #    result = True
