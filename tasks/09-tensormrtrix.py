# -*- coding: utf-8 -*-
from lib.generictask import GenericTask

__author__ = 'desmat'

class TensorMrtrix(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preprocessing', 'masking')


    def implement(self):

        dwi = self.getImage(self.dependDir,'dwi','upsample')
        bFile = self.getImage(self.dependDir, 'grad',  None, 'b')
        mask = self.getImage(self.maskingDir, 'anat',['extended', 'mask'])

        tensorsMrtrix = self.__produceTensors(dwi, bFile, mask)

        print 'tensor=',tensorsMrtrix
        self.__metricMrtrix(tensorsMrtrix, mask)


    # convert diffusion-weighted images to tensor images.
    def __produceTensors(self, source, encodingFile, mask=None):
        self.info("Starting DWI2Tensor from mrtrix")

        tmp =  self.buildName(source, "tmp")
        target = self.buildName(source, "tensor")
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


    def meetRequirement(self):
        images = {"upsampled diffusion":self.getImage(self.dependDir, 'dwi', 'upsample'),
                  "gradient encoding b file":  self.getImage(self.dependDir, 'grad', None, 'b'),
                  'ultimate extended mask':  self.getImage(self.maskingDir, 'anat', ['extended', 'mask'])}
        return self.isSomeImagesMissing(images)


    def isDirty(self):

        images ={"mrtrix tensor": self.getImage(self.workingDir, "dwi", "tensor"),
                    "mean apparent diffusion coefficient (ADC)" : self.getImage(self.workingDir, 'dwi', 'adc'),
                    "selected eigenvector(s)" : self.getImage(self.workingDir, 'dwi', 'vector'),
                    "fractional anisotropy" : self.getImage(self.workingDir, 'dwi', 'fa'),
                    "selected eigenvalue(s) AD" : self.getImage(self.workingDir, 'dwi', 'value_ad'),
                    "selected eigenvalue(s) RD" : self.getImage(self.workingDir, 'dwi', 'value_rd')}
        return self.isSomeImagesMissing(images)
