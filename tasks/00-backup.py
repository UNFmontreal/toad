from lib.generictask import GenericTask
import shutil
import glob
import os

__author__ = 'desmat'

class Backup(GenericTask):


    def __init__(self, subject):
        self.subjectDir = subject.getDir()
        GenericTask.__init__(self, subject)
        self.setCleanupBeforeImplement(False)

    def implement(self):
        self.info("Build directories structure for subject: {}".format(os.path.basename(self.workingDir)))

        images =[self.getImage(self.subjectDir, 'anat'),
                 self.getImage(self.subjectDir, 'dwi'),
                 self.getImage(self.subjectDir, 'mag',),
                 self.getImage(self.subjectDir, 'phase'),
                 self.getImage(self.subjectDir, 'aparc_aseg'),
                 self.getImage(self.subjectDir, 'anat_freesurfer'),
                 self.getImage(self.subjectDir, 'brodmann'),
                 self.getImage(self.subjectDir, 'b0AP'),
                 self.getImage(self.subjectDir, 'b0PA'),
                 self.getImage(self.subjectDir, 'grad', None, 'b'),
                 self.getImage(self.subjectDir, 'grad', None, 'bval'),
                 self.getImage(self.subjectDir, 'grad', None, 'bvec'),
                 self.getImage(self.subjectDir, 'config', None, 'cfg')]

        print "self.subjectDir=",self.subjectDir
        print "images =",images
        for image in images:
            if image:
                self.info("Moving file {} to {} directory".format(image, self.workingDir))
                shutil.move(image, self.workingDir)


    def meetRequirement(self):
        return True


    def isDirty(self):

        images = {'high resolution': self.getImage(self.workingDir, 'anat'), 'diffusion weighted': self.getImage(self.workingDir, 'dwi')}
        #@TODO vbal bvec may be optionnal
        #images = {'gradient .bval encoding file': self.getImage(self.workingDir, 'grad', None, 'bval'),
        #          'gradient .bvec encoding file': self.getImage(self.workingDir, 'grad', None, 'bvec'),
        #          'gradient .b encoding file': self.getImage(self.workingDir, 'grad', None, 'b'),
        #          'high resolution': self.getImage(self.workingDir, 'anat'),
        #          'diffusion weighted': self.getImage(self.workingDir, 'dwi')}
        return self.isSomeImagesMissing(images)


    def cleanup(self):
        if os.path.exists(self.workingDir):
            sources = glob.glob("{}/*".format(self.workingDir))
            for source in sources:
                if os.path.islink(source):
                    os.unlink(source)
                else:
                    shutil.move(source, self.subjectDir)
            os.rmdir(self.workingDir)
