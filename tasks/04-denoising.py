from lib.generictask import GenericTask
from lib import util, mriutil
import dipy.denoise.nlmeans
import numpy
import nibabel
import os

__author__ = 'desmat'

class Denoising(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'eddy', 'preparation', 'fieldmap')


    def implement(self):

        if self.get("algorithm").lower() in "none":
            self.info("Skipping denoising process")
        else:
            dwi = self.__getDwiImage()
            target = self.buildName(dwi, "denoise")
            if self.get("algorithm") == "nlmeans":
                if not self.config.getboolean("eddy", "ignore"):
                    bVal=  self.getImage(self.eddyDir, 'grad',  None, 'bval')
                else:
                    bVal=  self.getImage(self.preparationDir, 'grad',  None, 'bval')
                b0Index = mriutil.getFirstB0IndexFromDwi(bVal)

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
                scriptName = self.__createLpcaScript(dwiUncompress, tmp)
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


    def __createLpcaScript(self, source, target):

        scriptName = os.path.join(self.workingDir, "{}.m".format(self.get("script_name")))
        self.info("Creating denoising script {}".format(scriptName))
        tags={ 'source': source, 'target':target,
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


    def qaSupplier(self):
        denoise = self.getImage(self.workingDir, "dwi", 'denoise')
        self.nifti4dtoGif(denoise)


    def meetRequirement(self, result = True):
        if self.isSomeImagesMissing({'fieldmap': self.getImage(self.fieldmapDir, "dwi", 'unwarp')}) and \
                self.isSomeImagesMissing({'eddy corrected': self.getImage(self.dependDir, "dwi", 'eddy')}) and \
                self.isSomeImagesMissing({'diffusion weighted': self.getImage(self.preparationDir, "dwi")}):
            result = False
            self.warning("No suitable dwi image found for denoising task")
        return result


    def isDirty(self, result = False):
        dict = {'denoised': self.getImage(self.workingDir, "dwi", 'denoise')}
        return self.isSomeImagesMissing(dict)
