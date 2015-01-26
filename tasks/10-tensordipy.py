from lib.generictask import GenericTask
import dipy.core.gradients, dipy.reconst.dti
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

        GenericTask.__init__(self, subject, 'preprocessing', 'preparation', 'eddy', 'masking')
        """Inherit from a generic Task.

        Args:
            subject: Subject instance inherit by the subjectmanager.

            Note that you may supply additional arguments to generic tasks.
            Exemple: if you provide Task.__init__(self, subject, foo, bar ...)
            toad will create an variable fooDir and barDir and then create an alias 'dependDir'
            that will point to the first additionnal argurments fooDir.

        """

    def implement(self):

        dwi = self.getImage(self.dependDir, 'dwi', 'upsample')

        mask = self.getImage(self.maskingDir, 'anat', ['extended', 'mask'])

        #Look first if there is eddy b encoding files produces
        bValFile = self.getImage(self.eddyDir, 'grad', None, 'bval')
        bVecFile = self.getImage(self.eddyDir, 'grad', None, 'bvec')

        if not bValFile:
            bValFile = self.getImage(self.preparationDir,'grad', None, 'bval')

        if not bVecFile:
            bVecFile = self.getImage(self.preparationDir,'grad', None, 'bvec')

        self.__produceTensors(dwi, bValFile, bVecFile, mask)


    def __produceTensors(self, source, bValFile, bVecFile, mask):
        self.info("Starting tensors creation from dipy on {}".format(source))
        target = self.buildName(source, "dipy")

        dwiImage = nibabel.load(source)
        maskImage = nibabel.load(mask)

        dwiData  = dwiImage.get_data()
        dwiData = dipy.segment.mask.applymask(dwiData, maskImage)

        gradientTable = dipy.core.gradients.gradient_table(numpy.loadtxt(bValFile), numpy.loadtxt(bVecFile))

        model = dipy.reconst.dti.TensorModel(gradientTable)
        fit = model.fit(dwiData)
        tensorsValues = dipy.reconst.dti.lower_triangular(fit.quadratic_form)
        correctOrder = [0,1,3,2,4,5]
        tensorsValuesReordered = tensorsValues[:,:,:,correctOrder]
        tensorsImage = nibabel.Nifti1Image(tensorsValuesReordered.astype(numpy.float32), dwiImage.get_affine())
        nibabel.save(tensorsImage, target)
        self.info("End tensor creation from dipy, resulting file is {} ".format(target))
        return target


    def meetRequirement(self, result = True):

        #Look first if there is eddy b encoding files produces
        bValFile = self.getImage(self.eddyDir, 'grad', None, 'bval')
        bVecFile = self.getImage(self.eddyDir, 'grad', None, 'bvec')

        if (not bValFile) or (not bVecFile):

            if not self.getImage(self.preparationDir,'grad', None, 'bval'):
                self.info("Dipy .bval gradient encoding file is missing in directory {}".format(self.preparationDir))
                result = False

            if not self.getImage(self.preparationDir,'grad', None, 'bvec'):
                self.info("Dipy .bvec gradient encoding file is missing in directory {}".format(self.preparationDir))
                result = False

        if not self.getImage(self.dependDir, 'dwi', 'upsample'):
            self.info("Cannot find any DWI image in {} directory".format(self.dependDir))
            result = False

        if not self.getImage(self.maskingDir, 'anat', ['extended', 'mask']):
            self.info("Cannot find any ultimate extended mask {} directory".format(self.maskingDir))
            result = False

        return result


    def isDirty(self):

        images ={"dipy tensor": self.getImage(self.workingDir, "dwi", "dipy")}
        return self.isSomeImagesMissing(images)

        #@TODO see with Arnaud for that feature
        #if not self.getImage(self.workingDir, 'dwi', ['dipy', 'mask']):
        #    self.info("No dipy tensor mask found in directory {}"{}elf.workingDir)
        #    result = True
