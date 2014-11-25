from generic.generictask import GenericTask

__author__ = 'desmat'

class TensorsMetric(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'tensors', 'masking')


    def implement(self):
        tensorsMrtrix = self.getImage(self.dependDir, 'dwi', 'mrtrix')
        mask = self.getImage(self.maskingDir, 'anat',['extended','mask'])
        self.__metricMrtrix(tensorsMrtrix, mask)


    def __metricMrtrix(self, source, mask = None):

        self.info("Launch tensor2metric from mrtrix.\n")
        adc = self.getTarget(source, "adc")
        fa = self.getTarget(source, "fa")
        vector = self.getTarget(source, "vector")
        adImage = self.getTarget(source, "value_ad")
        rdImage = self.getTarget(source, "value_rd")
        value2 = self.getTarget(source, "value2")
        value3 = self.getTarget(source, "value3")
        modulate = self.get('modulate')

        cmd1 = "tensor2metric %s -adc %s -fa %s -num 1 -vector %s -value %s -modulate %s -nthreads %s -quiet "%(source, adc, fa, vector, adImage , modulate, self.getNTreadsMrtrix())
        cmd2 = "tensor2metric %s -num 2 -value %s -modulate %s -nthreads %s -quiet "%(source, value2, modulate, self.getNTreadsMrtrix())
        cmd3 = "tensor2metric %s -num 3 -value %s -modulate %s -nthreads %s -quiet "%(source, value3, modulate, self.getNTreadsMrtrix())

        for cmd in [cmd1, cmd2, cmd3]:
            if mask is not None:
                cmd += "-mask %s "%mask
            self.launchCommand(cmd)

        cmd = "mrmath %s %s mean %s -nthreads %s -quiet "%(value2, value3, rdImage, self.getNTreadsMrtrix())
        self.launchCommand(cmd)


    def meetRequirement(self):

        images = {"mrtrix tensor": self.getImage(self.dependDir, 'dwi', 'mrtrix'),
                  "ultimate extended mask": self.getImage(self.maskingDir, 'anat',['extended','mask'])}
        return self.isAllImagesExists(images)


    def isDirty(self):

        images = {"mean apparent diffusion coefficient (ADC)" : self.getImage(self.workingDir, 'dwi', 'adc'),
                    "selected eigenvector(s)" : self.getImage(self.workingDir, 'dwi', 'vector'),
                    "fractional anisotropy" : self.getImage(self.workingDir, 'dwi', 'fa'),
                    "selected eigenvalue(s) AD" : self.getImage(self.workingDir, 'dwi', 'value_ad'),
                    "selected eigenvalue(s) RD" : self.getImage(self.workingDir, 'dwi', 'value_rd')}

        return self.isSomeImagesMissing(images)
