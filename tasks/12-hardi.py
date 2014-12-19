from lib.generictask import GenericTask
from lib.logger import Logger
from lib import util
import os

__author__ = 'desmat'

class Hardi(GenericTask, Logger):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preprocessing', 'preparation', 'eddyDir', 'masking')


    def implement(self):

        dwi = self.getImage(self.dependDir,'dwi', 'upsample')
        bFile = self.getImage(self.eddyDir, 'grad', None, 'b')
        if not bFile:
            bFile = self.getImage(self.preparationDir, 'grad', None, 'b')

        maskDwi2Response = self.getImage(self.maskingDir, 'aparc_aseg', ['act','wm','mask'])
        outputDwi2Response = self.__dwi2response(dwi, maskDwi2Response, bFile)

        maskDwi2fod =  self.getImage(self.maskingDir, 'anat',['extended', 'mask'])
        fodImage = self.__dwi2fod(dwi, outputDwi2Response, maskDwi2fod, bFile)


    def __dwi2response(self, source, mask, bFile):

        target = self.buildName(source, None,'txt')
        tmp = self.buildName(source, "tmp",'txt')

        self.info("Starting dwi2response creation from mrtrix on {}".format(source))
        cmd = "dwi2response {} {} -mask {} -grad {} -nthreads {} -quiet"\
            .format(source, tmp, mask, bFile, self.getNTreadsMrtrix())
        self.launchCommand(cmd)
        self.info("renaming {} to {}".format(tmp, target))
        os.rename(tmp, target)

        return target


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


    def meetRequirement(self, result = True):

        images = {'diffusion weighted': self.getImage(self.dependDir,'dwi','upsample'),
                  'white matter segmented mask': self.getImage(self.maskingDir, 'aparc_aseg', ['act','wm','mask']),
                  'ultimate extended mask': self.getImage(self.maskingDir, 'anat', ['extended', 'mask'])}

        if self.isSomeImagesMissing(images):
            result = False

        if self.isSomeImagesMissing({'.b gradient encoding file': self.getImage(self.eddyDir, 'grad', None, 'b')}):
            if self.isSomeImagesMissing({'.b gradient encoding file': self.getImage(self.preparationDir, 'grad', None, 'b')}):
                result = False

        return result


    def isDirty(self, result = False):

        images = {"response function estimation text file": self.getImage(self.workingDir, 'dwi', None, 'txt'),
                  "fibre orientation distribution estimation": self.getImage(self.workingDir, 'dwi', 'fod')}

        return self.isSomeImagesMissing(images)

