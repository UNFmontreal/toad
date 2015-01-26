from lib.generictask import GenericTask
from lib import util
import shutil, os

__author__ = 'desmat'

class Denoising(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'eddy', 'preparation', 'fieldmap')


    def implement(self):

        if self.get("algorithm") is "None":
            self.info("Skipping denoising process")
        else:
            dwi = self.getImage(self.fieldmapDir, "dwi", 'unwarp')
            if not dwi:
                dwi = self.getImage(self.dependDir, "dwi", 'eddy')
                if not dwi:
                    dwi = self.getImage(self.preparationDir, "dwi")

            dwiUncompress = self.uncompressImage(dwi)
            tmp = self.buildName(dwiUncompress, "tmp", 'nii')
            scriptName = self.__createLpcaScript(dwiUncompress, tmp)
            self.__launchMatlabExecution(scriptName)

            self.info("compressing {} image".format(tmp))
            tmpCompress = util.gzip(tmp)

            target = self.buildName(dwi, "denoise")
            self.rename(tmpCompress, target)

            if self.getBoolean("cleanup"):
                self.info("Removing redundant image {}".format(dwiUncompress))
                os.remove(dwiUncompress)


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
        return self.get("algorithm") is "None"


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


