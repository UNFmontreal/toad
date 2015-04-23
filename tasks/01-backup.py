import shutil
import glob
import os

from core.generictask import GenericTask
from lib.images import Images
from lib import mriutil

__author__ = 'desmat'

class Backup(GenericTask):


    def __init__(self, subject):
        self.subjectDir = subject.getDir()
        GenericTask.__init__(self, subject)
        self.setCleanupBeforeImplement(False)


    def implement(self):
        self.info("Build directories structure for subject: {}".format(os.path.basename(self.workingDir)))
        #@TODO add description to that struct
        images = Images((self.getImage(self.subjectDir, 'anat'), ""),
                       (self.getImage(self.subjectDir, 'dwi'), ""),
                       (self.getImage(self.subjectDir, 'mag',), ""),
                       (self.getImage(self.subjectDir, 'phase'), ""),
                       (self.getImage(self.subjectDir, 'aparc_aseg'), ""),
                       (self.getImage(self.subjectDir, 'anat', 'freesurfer'), ""),
                       (self.getImage(self.subjectDir, 'lh_ribbon'), ""),
                       (self.getImage(self.subjectDir, 'rh_ribbon'), ""),
                       (self.getImage(self.subjectDir, 'brodmann'), ""),
                       (self.getImage(self.subjectDir, 'b0_ap'), ""),
                       (self.getImage(self.subjectDir, 'b0_pa'), ""),
                       (self.getImage(self.subjectDir, 'grad', None, 'b'), ""),
                       (self.getImage(self.subjectDir, 'grad', None, 'bvals'), ""),
                       (self.getImage(self.subjectDir, 'grad', None, 'bvecs'), ""),
                       (self.getImage(self.subjectDir, 'config', None, 'cfg'), ""))

        for image, description in images.getData():
            if image:
                self.info("Found {} image: moving it to {} directory".format(description, image, self.workingDir))
                shutil.move(image, self.workingDir)

        directories = [directory for directory in os.listdir(".") if os.path.isdir(self.subjectDir)]
        for directory in directories:
            if mriutil.isAfreesurferStructure(directory):
                self.info("{} seem\'s a valid freesurfer structure: moving it to {} directory".format(directory, self.workingDir))
                shutil.move(directory, self.workingDir)


    def meetRequirement(self):
        return True


    def isDirty(self):
        return Images((self.getImage(self.workingDir, 'dwi'),'high resolution')).isSomeImagesMissing()
        #@TODO bvals bvecs may be optionnal
        #images = {'gradient .bvals encoding file': self.getImage(self.workingDir, 'grad', None, 'bvals'),
        #          'gradient .bvecs encoding file': self.getImage(self.workingDir, 'grad', None, 'bvecs'),
        #          'gradient .b encoding file': self.getImage(self.workingDir, 'grad', None, 'b'),
        #          'high resolution': self.getImage(self.workingDir, 'anat'),
        #          'diffusion weighted': self.getImage(self.workingDir, 'dwi')}


    def cleanup(self):
        if os.path.exists(self.workingDir):
            sources = glob.glob("{}/*".format(self.workingDir))
            for source in sources:
                if os.path.islink(source):
                    os.unlink(source)
                else:
                    shutil.move(source, self.subjectDir)
            os.rmdir(self.workingDir)
