from generic.generictask import GenericTask
from modules import util
import os


__author__ = 'desmat'

class Denoising(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'unwarping', 'preparation' )


    def implement(self):

        if self.get("algorithm") is "None":
            self.info("Skipping denoising process")
        else:
            dwi = self.getImage(self.dependDir, "dwi", 'unwarp')
            if not dwi:
                dwi = self.getImage(self.preparationDir, "dwi")

            target = self.getTarget(dwi, "denoise")
            tmp = self.getTarget(dwi, "tmp")
            scriptName = self.__createLpcaScript(dwi, tmp)
            self.__launchMatlabExecution(scriptName)
            self.info("rename {} to {}".format(tmp, target))
            os.rename(tmp, target)


    def __createLpcaScript(self, source, target):

        scriptName = os.path.join(self.workingDir, "{}.m".format(self.get("script_name")))
        self.info("Creating lpca script {}".format(scriptName))
        #@TODO debug switch self.getNTreads()
        tags={ 'source': source, 'target':target, 'workingDir': self.workingDir, 'nbthreads':"1"}
        template = self.parseTemplate(tags, os.path.join(self.toadDir, "templates/files/denoise.tpl"))
        util.createScript(scriptName, template)
        return scriptName


    def __launchMatlabExecution(self, pyscript):

        self.info("Launch DWIDenoisingLPCA from matlab.")
        self.launchMatlabCommand(pyscript, self.isSingleThread())


    def isIgnore(self):
        return self.get("algorithm") is "None"


    def meetRequirement(self, result = True):

        if self.isSomeImagesMissing({'unwarped': self.getImage(self.dependDir, "dwi", 'unwarp')}):
            dwi = self.getImage(self.preparationDir, "dwi")
            if self.isSomeImagesMissing({'diffusion weighted': dwi}):
                result = False
            else:
                self.info("Will take {} image instead".format(dwi))

        return result


    def isDirty(self, result = False):
        dict = {'denoised': self.getImage(self.workingDir, "dwi", 'denoise')}
        return self.isSomeImagesMissing(dict)


