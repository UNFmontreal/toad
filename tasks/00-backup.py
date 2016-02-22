# -*- coding: utf-8 -*-
import os
import glob
import shutil

from core.toad.generictask import GenericTask
from lib.images import Images
from lib import mriutil


__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class Backup(GenericTask):


    def __init__(self, subject):
        self.subjectDir = subject.getDir()
        GenericTask.__init__(self, subject)
        self.setCleanupBeforeImplement(False)


    def implement(self):

        self.info("Build directories structure for subject: {}".format(os.path.basename(self.workingDir)))
        #@TODO add description to that struct
        images = Images((self.getSubjectImage('anat'), ""),
                       (self.getSubjectImage('dwi'), ""),
                       (self.getSubjectImage('mag',), ""),
                       (self.getSubjectImage('phase'), ""),
                       (self.getSubjectImage('aparc_aseg'), ""),
                       (self.getSubjectImage('anat', 'freesurfer'), ""),
                       (self.getSubjectImage('lh_ribbon'), ""),
                       (self.getSubjectImage('rh_ribbon'), ""),
                       (self.getSubjectImage('brodmann'), ""),
                       (self.getSubjectImage('b0_ap'), ""),
                       (self.getSubjectImage('b0_pa'), ""),
                       (self.getSubjectImage('grad', None, 'b'), ""),
                       (self.getSubjectImage('grad', None, 'bvals'), ""),
                       (self.getSubjectImage('grad', None, 'bvecs'), ""),
                       (self.getSubjectImage('tq_dict', None, 'qry'), ""),
                       (self.getSubjectImage('queries', None, 'qry'), ""),
                       (self.getSubjectImage('config', None, 'cfg'), ""),)

        for image, description in images.getData():
            if image:
                self.info("Found {} image: moving it to {} directory".format(description, image, self.workingDir))
                shutil.move(image, self.workingDir)

        directories = [os.path.join(self.subjectDir, directory) for directory in os.listdir(self.subjectDir) if os.path.isdir(os.path.join(self.subjectDir, directory))]
        for directory in directories:
            if mriutil.isAfreesurferStructure(directory):
                self.info("{} seem\'s a valid freesurfer structure: moving it to {} directory".format(directory, self.workingDir))
                shutil.move(directory, self.workingDir)


    def meetRequirement(self):
        return True


    def isDirty(self):
        return Images((self.getImage('dwi'),'high resolution'))


    def cleanup(self):
        if os.path.exists(self.workingDir):
            sources = glob.glob("{}/*".format(self.workingDir))
            for source in sources:
                if os.path.islink(source):
                    os.unlink(source)
                else:
                    shutil.move(source, self.subjectDir)
            os.rmdir(self.workingDir)

