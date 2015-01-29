# -*- coding: utf-8 -*-
from lib.generictask import GenericTask

__author__ = 'desmat'

class TensorMrtrix(GenericTask):


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


        tensorsMrtrix = self.__produceTensors(dwi, bFile, mask)

        print 'tensor=',tensorsMrtrix
        self.__metricMrtrix(tensorsMrtrix, mask)


    # convert diffusion-weighted images to tensor images.
    def __produceTensors(self, source, encodingFile, mask=None):
        self.info("Starting DWI2Tensor from mrtrix")

        tmp =  self.buildName(source, "tmp")
        target = self.buildName(source, "mrtrix")
        cmd = "dwi2tensor {} {} -grad {} -nthreads {} -quiet ".format(source, tmp, encodingFile, self.getNTreadsMrtrix())
        if mask is not None:
            cmd += "-mask {}".format(mask)

        self.launchCommand(cmd)
        return self.rename(tmp, target)


    def __metricMrtrix(self, source, mask = None):
        print "source = ", source
        self.info("Launch tensor2metric from mrtrix.\n")
        adc = self.buildName(source, "adc")
        fa = self.buildName(source, "fa")
        vector = self.buildName(source, "vector")
        adImage = self.buildName(source, "value_ad")
        rdImage = self.buildName(source, "value_rd")
        value2 = self.buildName(source, "value2")
        value3 = self.buildName(source, "value3")
        modulate = self.get('modulate')

        cmd1 = "tensor2metric {} -adc {} -fa {} -num 1 -vector {} -value {} -modulate {} -nthreads {} -quiet "\
            .format(source, adc, fa, vector, adImage , modulate, self.getNTreadsMrtrix())
        cmd2 = "tensor2metric {} -num 2 -value {} -modulate {} -nthreads {} -quiet "\
            .format(source, value2, modulate, self.getNTreadsMrtrix())
        cmd3 = "tensor2metric {} -num 3 -value {} -modulate {} -nthreads {} -quiet "\
            .format(source, value3, modulate, self.getNTreadsMrtrix())

        for cmd in [cmd1, cmd2, cmd3]:
            if mask is not None:
                cmd += "-mask {} ".format(mask)
            self.launchCommand(cmd)

        cmd = "mrmath {} {} mean {} -nthreads {} -quiet ".format(value2, value3, rdImage, self.getNTreadsMrtrix())
        self.launchCommand(cmd)


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
                    "mean apparent diffusion coefficient (ADC)" : self.getImage(self.workingDir, 'dwi', 'adc'),
                    "selected eigenvector(s)" : self.getImage(self.workingDir, 'dwi', 'vector'),
                    "fractional anisotropy" : self.getImage(self.workingDir, 'dwi', 'fa'),
                    "selected eigenvalue(s) AD" : self.getImage(self.workingDir, 'dwi', 'value_ad'),
                    "selected eigenvalue(s) RD" : self.getImage(self.workingDir, 'dwi', 'value_rd')}
        return self.isSomeImagesMissing(images)
