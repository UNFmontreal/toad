from lib.generictask import GenericTask
from lib import util
import os


__author__ = 'desmat'

class Denoising(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'eddy', 'preparation' )


    def implement(self):

        if self.get("algorithm") is "None":
            self.info("Skipping denoising process")
        else:
            dwi = self.getImage(self.dependDir, "dwi", 'eddy')
            if not dwi:
                dwi = self.getImage(self.preparationDir, "dwi")

            target = self.buildName(dwi, "denoise")
            tmp = self.buildName(dwi, "tmp")
            scriptName = self.__createLpcaScript(dwi, tmp)
            self.__launchMatlabExecution(scriptName)
            self.info("rename {} to {}".format(tmp, target))
            os.rename(tmp, target)


    def __createLpcaScript(self, source, target):

        scriptName = os.path.join(self.workingDir, "{}.m".format(self.get("script_name")))
        self.info("Creating denoising script {}".format(scriptName))
        tags={ 'source': source, 'target':target,
               'workingDir': self.workingDir,
               'beta': self.get('beta'),
               'rician': self.get('rician'),
               'nbthreads': self.getNTreads()}

        if self.get("algorithm") == "aonlm":
            template = self.parseTemplate(tags, os.path.join(self.toadDir, "templates/files/denoise_aonlm.tpl"))
        else:
            template = self.parseTemplate(tags, os.path.join(self.toadDir, "templates/files/denoise_lpca.tpl"))

        util.createScript(scriptName, template)
        return scriptName


    def __launchMatlabExecution(self, pyscript):

        self.info("Launch DWIDenoisingLPCA from matlab.")
        self.launchMatlabCommand(pyscript, self.isSingleThread())


    def isIgnore(self):
        return self.get("algorithm") is "None"


    def meetRequirement(self, result = True):

        if self.isSomeImagesMissing({'eddy corrected': self.getImage(self.dependDir, "dwi", 'eddy')}):
            dwi = self.getImage(self.preparationDir, "dwi")
            if self.isSomeImagesMissing({'diffusion weighted': dwi}):
                result = False
            else:
                self.info("Will take {} image instead".format(dwi))

        return result


    def isDirty(self, result = False):
        dict = {'denoised': self.getImage(self.workingDir, "dwi", 'denoise')}
        return self.isSomeImagesMissing(dict)


