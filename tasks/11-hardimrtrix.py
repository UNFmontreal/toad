from lib.generictask import GenericTask
from lib.logger import Logger
from lib import util
import os

__author__ = 'desmat'

class HardiMrtrix(GenericTask, Logger):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preprocessing', 'masking')


    def implement(self):

        #@TODO produce "Generalised Fractional Anisotropy": self.getImage(self.workingDir,'dwi','gfa'),

        dwi = self.getImage(self.dependDir,'dwi', 'upsample')
        bFile = self.getImage(self.dependDir, 'grad', None, 'b')

        maskDwi2Response = self.getImage(self.maskingDir, 'aparc_aseg', ['resample', 'act', 'wm', 'mask'])
        outputDwi2Response = self.__dwi2response(dwi, maskDwi2Response, bFile)

        maskDwi2fod =  self.getImage(self.maskingDir, 'anat',['resample', 'extended', 'mask'])
        fodImage = self.__dwi2fod(dwi, outputDwi2Response, maskDwi2fod, bFile)

        mask = self.getImage(self.maskingDir, 'anat', ['resample', 'extended','mask'])
        self.__fod2metrics(fodImage, mask)


    def __dwi2response(self, source, mask, bFile):

        target = self.buildName(source, None,'txt')
        tmp = self.buildName(source, "tmp",'txt')

        self.info("Starting dwi2response creation from mrtrix on {}".format(source))
        cmd = "dwi2response {} {} -mask {} -grad {} -nthreads {} -quiet"\
            .format(source, tmp, mask, bFile, self.getNTreadsMrtrix())
        self.launchCommand(cmd)
        return self.rename(tmp, target)


    def __dwi2fod(self, source, dwi2response, mask, bFile):

        tmp = self.buildName(source, "tmp")
        target = self.buildName(source, "fod")

        self.info("Starting dwi2fod creation from mrtrix on {}".format(source))

        cmd = "dwi2fod {} {} {} -mask {} -grad {} -nthreads {} -quiet"\
            .format(source, dwi2response, tmp, mask, bFile, self.getNTreadsMrtrix())
        self.launchCommand(cmd)

        self.info("renaming {} to {}".format(tmp, target))
        os.rename(tmp, target)

        return target


    def __fod2metrics(self, source, mask=None):
        """Produce fixel and nufo image from an fod

        Args:
            source: the source image

        Return:
            the nufo image

        """

        tmp = self.buildName(source, "tmp")
        fixelTarget = self.buildName(source,"fixel_peak", 'msf')
        nufoImage = self.buildName(source, 'nufo')

        self.info("Starting fod2fixel creation from mrtrix on {}".format(source))
        cmd = "fod2fixel {} -peak {} -force -nthreads {} -quiet".format(source, fixelTarget, self.getNTreadsMrtrix())
        self.launchCommand(cmd)


        cmd = "fixel2voxel {} count {} -nthreads {} -quiet".format(fixelTarget, tmp,  self.getNTreadsMrtrix())
        self.launchCommand(cmd)
        return self.rename(tmp, nufoImage)


    def meetRequirement(self):

        images = {'diffusion weighted': self.getImage(self.dependDir,'dwi','upsample'),
                  "gradient encoding b file":  self.getImage(self.dependDir, 'grad', None, 'b'),
                  'white matter segmented mask': self.getImage(self.maskingDir, 'aparc_aseg', ['resample', 'act', 'wm', 'mask']),
                  'ultimate extended mask': self.getImage(self.maskingDir, 'anat', ['resample', 'extended', 'mask'])}
        return self.isAllImagesExists(images)


    def isDirty(self, result = False):

        images = {"response function estimation text file": self.getImage(self.workingDir, 'dwi', None, 'txt'),
                  "fibre orientation distribution estimation": self.getImage(self.workingDir, 'dwi', 'fod'),
                  'nufo': self.getImage(self.workingDir,'dwi','nufo'),
                  'fixel peak image': self.getImage(self.workingDir,'dwi', 'fixel_peak', 'msf')}

        return self.isSomeImagesMissing(images)
