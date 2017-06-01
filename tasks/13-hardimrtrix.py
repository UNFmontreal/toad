# -*- coding: utf-8 -*-
from core.toad.generictask import GenericTask
from lib.images import Images
from lib.mriutil import getlmax, getBValues
import  tempfile
from os import rmdir
from os.path import exists
from ast import literal_eval

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class HardiMrtrix(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'upsampling', 'registration', 'masking', 'qa')

    def implement(self):

        dwi = self.getUpsamplingImage('dwi', 'upsample')
        bFile = self.getUpsamplingImage('grad', None, 'b') 
        mask = self.getRegistrationImage('mask', 'resample')
        wmMask = self.getMaskingImage('tt5', ['resample','wm', 'mask'])
        fivett = self.getRegistrationImage('tt5', 'resample')
        tmpDir = tempfile.mkdtemp(prefix='tmp', dir=self.workingDir)
        self.set('lmax', getlmax(dwi))
        self.set('dwi_BValues', getBValues(dwi, bFile))

        if len(getBValues(dwi, bFile))==2:
            try:
                outputDwi2Response = self.__dwi2response(dwi, wmMask, bFile, tmpDir)
            except:
                rmdir(tmpDir)

            if exists(tmpDir):
                rmdir(tmpDir)

            fodImage = self.__dwi2fod(dwi, outputDwi2Response, mask, bFile, self.buildName(dwi, "csd"))

            fixelPeak = self.__fod2fixel(fodImage, mask, 'peak', self.buildName(dwi, "fixel_peak", 'msf'))
            self.__fod2fixel(fodImage, mask, 'afd', self.buildName(dwi, "afd", 'msf'))
        else:
            try:
                outputDwi2Response = self.__dwi2response(dwi, mask, bFile, tmpDir, fivett)
            except:
                rmdir(tmpDir)

            if exists(tmpDir):
                rmdir(tmpDir)

            fodImage = self.__dwi2fod(dwi, outputDwi2Response, mask, bFile, "", True)

            fixelPeak = self.__fod2fixel(fodImage[0], mask, 'peak', self.buildName(dwi, "fixel_peak", 'msf'))
            self.__fod2fixel(fodImage[0], mask, 'afd', self.buildName(dwi, "afd", 'msf'))

        self.__fixelPeak2nufo(fixelPeak, mask, self.buildName(dwi, 'nufo'))

    def __dwi2response(self, source, mask, bFile, tmpDir, tt5=False):

        target = self.buildName(source, None, 'txt')
        tmp = self.buildName(source, "tmp",'txt')

        self.info("Starting dwi2response creation from mrtrix on {}".format(source))

        if not tt5:
            if self.get('algorithmResponseFunction') == 'tournier':
                cmd = "dwi2response -nthreads {} -tempdir {} -quiet tournier -mask {} -grad {} {} {}"\
                    .format(self.getNTreadsMrtrix(), tmpDir, mask, bFile, source, tmp)
            else:
                self.info("This algorithm {} has not been implemented. If you want to use it please send us a message"\
                    .format(self.get('algorithmResponseFunction')))

            self.launchCommand(cmd)
            return self.rename(tmp, target)
        else:
            tmpWM = self.buildName(source, "tmpWM",'txt')
            tmpGM = self.buildName(source, "tmpGM",'txt')
            tmpCSF = self.buildName(source, "tmpCSF",'txt')

            targetWM = self.buildName(source, "wm", 'txt')
            targetGM = self.buildName(source, "gm", 'txt')
            targetCSF = self.buildName(source, "csf", 'txt')

            cmd = "dwi2response -nthreads {} -tempdir {} -quiet msmt_5tt -mask {} -grad {} {} {} {} {} {}"\
                    .format(self.getNTreadsMrtrix(), tmpDir, mask, bFile, source, tt5, tmpWM, tmpGM, tmpCSF )

            self.launchCommand(cmd)
            return [self.rename(tmpWM, targetWM), self.rename(tmpGM, targetGM), self.rename(tmpCSF, targetCSF)]


    def __dwi2fod(self, source, dwi2response, mask, bFile, target, tt5=False):

        #Single shell
        if not tt5:
            self.info("Starting dwi2fod creation using csd from mrtrix on {}".format(source))

            tmp = self.buildName(source, "tmp")
            cmd = "dwi2fod csd {} {} {} -mask {} -grad {} -nthreads {} -quiet"\
                .format(source, dwi2response, tmp, mask, bFile, self.getNTreadsMrtrix())
            self.launchCommand(cmd)

            return self.rename(tmp, target)
        else:# MultiShellMultiTissue
            tmpWM = self.buildName(source, "tmpWM")
            targetWM = self.buildName(source, "wm")
            tmpGM = self.buildName(source, "tmpGM")
            targetGM = self.buildName(source, "gm")
            tmpCSF = self.buildName(source, "tmpCSF")
            targetCSF = self.buildName(source, "csf")

            self.info("Starting dwi2fod creation using msmt_csd from mrtrix on {}".format(source))
            cmd = "dwi2fod msmt_csd -mask {} -grad {} -nthreads {} -quiet {} {} {} {} {} {} {}"\
                .format(mask, bFile, self.getNTreadsMrtrix(), source, dwi2response[0], tmpWM, dwi2response[1], tmpGM, dwi2response[2], tmpCSF)
            self.launchCommand(cmd)

            return [self.rename(tmpWM, targetWM), self.rename(tmpGM, targetGM), self.rename(tmpCSF, targetCSF)]


    def __fod2fixel(self, source, mask, metric, target):
        """Produce fixel metric from a csd image

        Args:

            source: the source image

        Return:
            the fixel peak image
        """
        tmp = self.buildName(source, "tmp", "msf")
        self.info("Starting fod2fixel creation {} from mrtrix on {}".format(metric, source))
        cmd = "fod2fixel -mask {} {} -{} {} -force -nthreads {} -quiet".format(mask, source, metric, tmp, self.getNTreadsMrtrix())
        self.launchCommand(cmd)
        return self.rename(tmp, target)

    def __fixelPeak2nufo(self, source, mask, target):
        tmp = self.buildName(source, "tmp","nii.gz")
        cmd = "fixel2voxel {} count {} -nthreads {} -quiet".format(source, tmp,  self.getNTreadsMrtrix())
        self.launchCommand(cmd)
        return self.rename(tmp, target)

    def isIgnore(self):
        return self.get("ignore")


    def meetRequirement(self):
        return Images((self.getUpsamplingImage('dwi','upsample'), 'diffusion weighted'),
                  (self.getUpsamplingImage('grad', None, 'b'), "gradient encoding b file"),
                  (self.getMaskingImage('tt5', ['resample', 'wm', 'mask']), 'white matter segmented mask'),
                  (self.getRegistrationImage('mask', 'resample'), 'brain mask'))


    def isDirty(self):
        dwi = self.getUpsamplingImage('dwi', 'upsample')
        bFile = self.getUpsamplingImage('grad', None, 'b')
        if len(getBValues(dwi, bFile))>2: # MutliShells
            return Images((self.getImage('dwi', 'nufo'), 'Number of Fibers Orientations'),
                      (self.getImage('dwi', 'afd', 'msf'), 'Apparent Fiber Density'),
                      (self.getImage('dwi', 'fixel_peak', 'msf'), 'fixel peak image'),
                      (self.getImage('dwi', 'wm', 'txt'), "wm response function estimation text file"),
                      (self.getImage('dwi', 'gm', 'txt'), "gm response function estimation text file"),
                      (self.getImage('dwi', 'csf', 'txt'), "csf response function estimation text file"),
                      (self.getImage('dwi', 'wm'), "constrained spherical deconvolution"),
                      (self.getImage('dwi', 'gm'), "gm image"),
                      (self.getImage('dwi', 'csf'), "csf image"))
        else:
            return Images((self.getImage('dwi', 'nufo'), 'Number of Fibers Orientations'),
                      (self.getImage('dwi', 'afd', 'msf'), 'Apparent Fiber Density'),
                      (self.getImage('dwi', 'fixel_peak', 'msf'), 'fixel peak image'),
                      (self.getImage('dwi', None, 'txt'), "response function estimation text file"),
                      (self.getImage('dwi', 'csd'), "constrained spherical deconvolution"))

    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        qaImages = Images()
        softwareName = 'mrtrix'

        #Get images
        mask = self.getRegistrationImage('mask', 'resample')

        #Build qa images
        tags = (
            ('nufo', 5, 'nufo'),
            ('afd', 5,'afd')
            )

        for postfix, vmax, description in tags:
            image = self.getImage('dwi', postfix)
            if image:
                imageQa = self.plot3dVolume(
                        image, fov=mask, vmax=vmax,
                        colorbar=True, postfix=softwareName)
                qaImages.append((imageQa, description))

        return qaImages
