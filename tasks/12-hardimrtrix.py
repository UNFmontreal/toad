import os

from core.generictask import GenericTask
from lib.images import Images

__author__ = 'desmat'

class HardiMrtrix(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preprocessing', 'masking')


    def implement(self):

        #@TODO produce "Generalised Fractional Anisotropy": self.getImage(self.workingDir,'dwi','gfa'),
        dwi = self.getImage(self.dependDir,'dwi', 'upsample')
        bFile = self.getImage(self.dependDir, 'grad', None, 'b')

        maskDwi2Response = self.getImage(self.maskingDir, 'aparc_aseg', ['resample', 'act', 'wm', 'mask'])
        outputDwi2Response = self.__dwi2response(dwi, maskDwi2Response, bFile)

        maskDwi2csd =  self.getImage(self.maskingDir, 'anat',['resample', 'extended', 'mask'])
        csdImage = self.__dwi2csd(dwi, outputDwi2Response, maskDwi2csd, bFile, self.buildName(dwi, "csd"))

        mask = self.getImage(self.maskingDir, 'anat', ['resample', 'extended','mask'])
        fixelPeak = self.__csd2fixelPeak(csdImage, mask, self.buildName(dwi, "fixel_peak", 'msf'))
        self.__fixelPeak2nufo(fixelPeak, mask, self.buildName(dwi, 'nufo'))


    def __dwi2response(self, source, mask, bFile):

        target = self.buildName(source, None, 'txt')
        tmp = self.buildName(source, "tmp",'txt')

        self.info("Starting dwi2response creation from mrtrix on {}".format(source))
        cmd = "dwi2response {} {} -mask {} -grad {} -nthreads {} -quiet"\
            .format(source, tmp, mask, bFile, self.getNTreadsMrtrix())
        self.launchCommand(cmd)
        return self.rename(tmp, target)


    def __dwi2csd(self, source, dwi2response, mask, bFile, target):

        self.info("Starting dwi2fod creation for csd from mrtrix on {}".format(source))

        tmp = self.buildName(source, "tmp")
        cmd = "dwi2fod {} {} {} -mask {} -grad {} -nthreads {} -quiet"\
            .format(source, dwi2response, tmp, mask, bFile, self.getNTreadsMrtrix())
        self.launchCommand(cmd)

        self.info("renaming {} to {}".format(tmp, target))
        return self.rename(tmp, target)


    def __csd2fixelPeak(self, source, mask, target):
        """Produce fixel and nufo image from an csd image

        Args:
            source: the source image

        Return:
            the fixel peak image

        """
        tmp = self.buildName(source, "tmp", "msf")
        self.info("Starting fod2fixel creation from mrtrix on {}".format(source))
        cmd = "fod2fixel {} -peak {} -force -nthreads {} -quiet".format(source, tmp, self.getNTreadsMrtrix())
        self.launchCommand(cmd)
        self.info("renaming {} to {}".format(tmp, target))
        return self.rename(tmp, target)


    def __fixelPeak2nufo(self, source, mask, target):
        tmp = self.buildName(source, "tmp","nii.gz")
        cmd = "fixel2voxel {} count {} -nthreads {} -quiet".format(source, tmp,  self.getNTreadsMrtrix())
        self.launchCommand(cmd)
        return self.rename(tmp, target)
        

    def isIgnore(self):
        return self.get("ignore").lower() in "true"


    def meetRequirement(self):

        images = Images((self.getImage(self.dependDir,'dwi','upsample'), 'diffusion weighted'),
                  (self.getImage(self.dependDir, 'grad', None, 'b'), "gradient encoding b file"),
                  (self.getImage(self.maskingDir, 'aparc_aseg', ['resample', 'act', 'wm', 'mask']), 'white matter segmented mask'),
                  (self.getImage(self.maskingDir, 'anat', ['resample', 'extended', 'mask']), 'ultimate extended mask'))
        return images.isAllImagesExists()


    def isDirty(self):

        images = Images((self.getImage(self.workingDir, 'dwi', None, 'txt'), "response function estimation text file"),
                  (self.getImage(self.workingDir, 'dwi', 'csd'), "fibre orientation distribution estimation"),
                  (self.getImage(self.workingDir,'dwi', 'nufo'), 'nufo'),
                  (self.getImage(self.workingDir,'dwi', 'fixel_peak', 'msf'), 'fixel peak image'))
        return images.isSomeImagesMissing()
