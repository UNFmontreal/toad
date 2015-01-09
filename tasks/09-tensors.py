# -*- coding: utf-8 -*-
from lib.generictask import GenericTask
import dipy.core.gradients, dipy.reconst.dti
import numpy, nibabel

__author__ = 'desmat'

#@TODO apply masking on proper images
class Tensors(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preprocessing', 'preparation', 'eddy', 'masking')


    def implement(self):

        dwi = self.getImage(self.dependDir,'dwi','upsample')

        bFile = self.getImage(self.eddyDir, 'grad',  None, 'b')
        bValFile = self.getImage(self.eddyDir, 'grad', None, 'bval')
        bVecFile = self.getImage(self.eddyDir, 'grad', None, 'bvec')

        mask = self.getImage(self.maskingDir, 'anat',['extended', 'mask'])

        if (not bFile) or (not bValFile) or (not bVecFile):
            bFile = self.getImage(self.preparationDir, 'grad', None, 'b')
            bValFile = self.getImage(self.preparationDir, 'grad', None, 'bval')
            bVecFile = self.getImage(self.preparationDir, 'grad', None, 'bvec')

        anatBrainWMResampleMask = self.getImage(self.maskingDir, 'anat', ['brain', 'wm', 'resample', 'mask'])

        #tensorsMrtrix = self.__tensorsMrtrix(dwi, bFile, mask)
        tensorsDipy = self.__tensorsDipy(dwi, bFile, bVecFile)

        #self.info("Masking mrtrix tensors image with the white matter, brain extracted, resampled, high resolution mask.")
        #self.masking(tensorsMrtrix, anatBrainWMResampleMask)
        #@TODO clarify masking situation


    # convert diffusion-weighted images to tensor images.
    def __tensorsMrtrix(self, source, encodingFile, mask=None):
        self.info("Starting DWI2Tensor from mrtrix")

        tmp =  self.buildName(source, "tmp")
        target = self.buildName(source, "mrtrix")
        cmd = "dwi2tensor {} {} -grad {} -nthreads {} -quiet ".format(source, tmp, encodingFile, self.getNTreadsMrtrix())
        if mask is not None:
            cmd += "-mask {}".format(mask)

        self.launchCommand(cmd)
        return self.rename(tmp, target)


    def __tensorsDipy(self, source, bValFile, bVecFile):
        self.info("Starting tensors creation from dipy on {}".format(source))
        target = self.buildName(source, "dipy")

        dwiImage = nibabel.load(source)
        dwiData  = dwiImage.get_data()
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
        bFile = self.getImage(self.eddyDir, 'grad', None, 'b')
        bValFile = self.getImage(self.eddyDir, 'grad', None, 'bval')
        bVecFile = self.getImage(self.eddyDir, 'grad', None, 'bvec')

        if (not bFile) or (not bValFile) or (not bVecFile):

            if not self.getImage(self.preparationDir, 'grad', None, 'b'):
                self.info("Mrtrix gradient encoding file is missing in directory {}".format(self.preparationDir))
                result = False

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

        images ={"mrtrix tensor": self.getImage(self.workingDir, "dwi", "mrtrix"),
                 "dipy tensor": self.getImage(self.workingDir, "dwi", "dipy")}
        return self.isSomeImagesMissing(images)

        #@TODO see with Arnaud for that feature
        #if not self.getImage(self.workingDir, 'dwi', ['dipy', 'mask']):
        #    self.info("No dipy tensor mask found in directory {}"{}elf.workingDir)
        #    result = True
