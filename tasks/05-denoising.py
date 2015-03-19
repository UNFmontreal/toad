import os

import dipy.denoise.nlmeans
import numpy
import nibabel

from core.generictask import GenericTask
from lib.images import Images
from lib import util, mriutil


__author__ = 'desmat'

class Denoising(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'eddy', 'preparation', 'fieldmap', 'qa')


    def implement(self):
        if self.get("algorithm").lower() in "none":
            self.info("Skipping denoising process")
        else:
            dwi = self.__getDwiImage()
            target = self.buildName(dwi, "denoise")
            if self.get("algorithm") == "nlmeans":
                if not self.config.getboolean("eddy", "ignore"):
                    bVals=  self.getImage(self.eddyDir, 'grad',  None, 'bvals')
                else:
                    bVals=  self.getImage(self.preparationDir, 'grad',  None, 'bvals')
                b0Index = mriutil.getFirstB0IndexFromDwi(bVals)

                try:
                    threshold = int(self.get("nlmeans_mask_threshold"))
                except ValueError:
                    threshold = 80

                dwiImage = nibabel.load(dwi)
                dwiData  = dwiImage.get_data()
                mask = dwiData[..., b0Index] > threshold
                b0Data = dwiData[..., b0Index]
                sigma = numpy.std(b0Data[~mask])
                denoisingData = dipy.denoise.nlmeans.nlmeans(dwiData, sigma, mask)
                nibabel.save(nibabel.Nifti1Image(denoisingData.astype(numpy.float32), dwiImage.get_affine()), target)

            else:
                dwi = self.__getDwiImage()
                dwiUncompress = self.uncompressImage(dwi)

                tmp = self.buildName(dwiUncompress, "tmp", 'nii')
                scriptName = self.__createMatlabScript(dwiUncompress, tmp)
                self.__launchMatlabExecution(scriptName)

                self.info("compressing {} image".format(tmp))
                tmpCompress = util.gzip(tmp)
                self.rename(tmpCompress, target)

                if self.getBoolean("cleanup"):
                    self.info("Removing redundant image {}".format(dwiUncompress))
                    os.remove(dwiUncompress)


    def __getDwiImage(self):
        if self.getImage(self.fieldmapDir, "dwi", 'unwarp'):
            return self.getImage(self.fieldmapDir, "dwi", 'unwarp')
        elif self.getImage(self.dependDir, "dwi", 'eddy'):
            return self.getImage(self.dependDir, "dwi", 'eddy')
        else:
            return self.getImage(self.preparationDir, "dwi")


    def __createMatlabScript(self, source, target):

        scriptName = os.path.join(self.workingDir, "{}.m".format(self.get("script_name")))
        self.info("Creating denoising script {}".format(scriptName))
        tags={ 'source': source,
               'target': target,
               'workingDir': self.workingDir,
               'beta': self.get('beta'),
               'rician': self.get('rician'),
               'nbthreads': self.getNTreadsDenoise()}

        if self.get("algorithm") == "aonlm":
            template = self.parseTemplate(tags, os.path.join(self.toadDir, "templates/files/denoise_aonlm.tpl"))
        else:
            template = self.parseTemplate(tags, os.path.join(self.toadDir, "templates/files/denoise_lpca.tpl"))

        util.createScript(scriptName, template)
        return scriptName


    def __launchMatlabExecution(self, pyscript):

        self.info("Launch DWIDenoisingLPCA from matlab.")
        self.launchMatlabCommand(pyscript)


    def isIgnore(self):
        return self.get("algorithm").lower() in "none"


    def meetRequirement(self, result = True):
        images = Images((self.getImage(self.fieldmapDir, "dwi", 'unwarp'), 'fieldmap'),
                       (self.getImage(self.dependDir, "dwi", 'eddy'), 'eddy corrected'),
                       (self.getImage(self.preparationDir, "dwi"), 'diffusion weighted'))
        if images.isNoImagesExists():
            result = False
            self.warning("No suitable dwi image found for denoising task")
        return result


    def isDirty(self):
        image = Images((self.getImage(self.workingDir, "dwi", 'denoise'), 'denoised'))
        return image.isSomeImagesMissing()


    def qaSupplier(self):
        denoise = self.getImage(self.workingDir, "dwi", 'denoise')
        denoiseGif = self.nifti4dtoGif(denoise)
        images = Images((denoiseGif,'Denoised diffusion image'))
        return images
