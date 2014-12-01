# -*- coding: utf-8 -*-
from generic.generictask import GenericTask
import os

__author__ = 'desmat'

#@TODO apply masking on proper images
class Tensors(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preprocessing', 'preparation', 'unwarping', 'masking')


    def implement(self):

        dwi = self.getImage(self.dependDir,'dwi','upsample')

        bFile = self.getImage(self.unwarpingDir, 'grad',  None, 'b')
        bValFile = self.getImage(self.unwarpingDir, 'grad', None, 'bval')
        bVecFile = self.getImage(self.unwarpingDir, 'grad', None, 'bvec')

        if (not bFile) or (not bValFile) or (not bVecFile):
            bFile = self.getImage(self.preparationDir, 'grad', None, 'b')
            bValFile = self.getImage(self.preparationDir, 'grad', None, 'bval')
            bVecFile = self.getImage(self.preparationDir, 'grad', None, 'bvec')

        anatBrainWMResampleMask = self.getImage(self.maskingDir, 'anat', ['brain', 'wm', 'resample', 'mask'])

        tensorsMrtrix = self.__tensorsMrtrix(dwi, bFile)

        #self.info("Masking mrtrix tensors image with the white matter, brain extracted, resampled, high resolution mask.")
        #self.masking(tensorsMrtrix, anatBrainWMResampleMask)

        #@TODO activate tensors dipy
        #@TODO clarify masking situation


    # convert diffusion-weighted images to tensor images.
    def __tensorsMrtrix(self, source, encodingFile):
        self.info("Starting DWI2Tensor from mrtrix")

        tmp =  self.getTarget(source, "tmp")
        target = self.getTarget(source, "mrtrix")
        cmd = "dwi2tensor {} {} -grad {} -nthreads {} -quiet".format(source, tmp, encodingFile, self.getNTreadsMrtrix())
        self.launchCommand(cmd)

        self.info("renaming {} to {}".format(tmp, target))
        os.rename(tmp, target)

        return target

    """
    def __tensorsDipy(self, image, bValFile, bVecFile):
        self.info("Starting tensors creation from dipy on {}".formatimage)
        outputFile = os.path.join(self.workingDir, os.path.basename(image.replace(".nii","{}.nii"{}elf.config.get('postfix','dipy'))))

        dwiImage = nibabel.load(image)
        dwiData  = dwiImage.get_data()
        gradientTable = dipy.core.gradients.gradient_table(numpy.loadtxt(bValFile), numpy.loadtxt(bVecFile))

        model = dipy.reconst.dti.TensorModel(gradientTable)
        fit = model.fit(dwiData)
        tensorsValues = dipy.reconst.dti.lower_triangular(fit.quadratic_form)
        correctOrder = [0,1,3,2,4,5]
        tensorsValuesReordered = tensorsValues[:,:,:,correctOrder]
        tensorsImage = nibabel.Nifti1Image(tensorsValuesReordered.astype(numpy.float32), dwiImage.get_affine())
        nibabel.save(tensorsImage, outputFile)
        self.info("End tensor creation from dipy, resulting file is {} ".format(outputFile))
        return outputFile
    """

    def meetRequirement(self, result = True):

        #Look first if there is eddy b encoding files produces
        bFile = self.getImage(self.unwarpingDir, 'grad', None, 'b')
        bValFile = self.getImage(self.unwarpingDir, 'grad', None, 'bval')
        bVecFile = self.getImage(self.unwarpingDir, 'grad', None, 'bvec')

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

        return result


    def isDirty(self):

        images ={"mrtrix tensor": self.getImage(self.workingDir, "dwi", "mrtrix")}
        return self.isSomeImagesMissing(images)



        #@TODO see with Arnaud for that feature
        #if not self.getImage(self.workingDir, 'dwi', ['mrtrix', 'mask']):
        #    self.info("No mrtrix tensor mask found in directory {}"{}elf.workingDir)
        #    result = True

        #if not self.getImage(self.workingDir, 'dwi', 'dipy'):
        #    self.info("No dipy tensor image found in directory {}"{}elf.workingDir)
        #    result = True

        #@TODO see with Arnaud for that feature
        #if not self.getImage(self.workingDir, 'dwi', ['dipy', 'mask']):
        #    self.info("No dipy tensor mask found in directory {}"{}elf.workingDir)
        #    result = True
