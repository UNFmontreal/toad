# -*- coding: utf-8 -*-
from core.toad.generictask import GenericTask
from lib.images import Images
from lib import util

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class Outputs(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'upsampling', 'registration', 'tensormrtrix', 'tensordipy', 'tensorfsl',
             'hardidipy', 'hardimrtrix', 'tractographymrtrix', 'tractquerier', 'tractfiltering', 'tractometry')
        self.__finished = False

    def implement(self):

        structs = {'dwi': self.getUpsamplingImage('dwi'),
                    'anat': self.getRegistrationImage('anat', ['freesurfer', 'resample']),
                    'mask': self.getRegistrationImage('mask', 'resample')}

        for postfix, image in structs.iteritems():
           util.copy(image, self.workingDir,  self.buildName(self.subject.getName(), postfix, 'nii.gz'))

        for extension in ['bvals', 'bvecs', 'benc']:
            util.copy(self.getUpsamplingImage('grad', None, extension),
                      self.workingDir,
                      self.buildName(self.subject.getName(), None, extension))

        self.__copyMetrics(['mrtrix', 'dipy', 'fsl'], ['fa','ad','rd','md'], 'tensor')
        self.__copyMetrics(['mrtrix', 'dipy'], ['nufo','csd','gfa'], 'hardi')

        self.createMethoHtml()

        self.__finished = True

    def __copyMetrics(self, softwares, postfixs, method):
        for software in softwares:
            for postfix in postfixs:
                source = getattr(self, "get{}{}Image".format(method, software))("dwi", postfix)
                target = self.buildName(self.subject.getName(), [software, postfix], 'nii.gz')
                util.copy(source, self.workingDir, target)


    def meetRequirement(self):
        images = Images((self.getUpsamplingImage('dwi'), 'diffusion weighted'),
                        (self.getUpsamplingImage('grad', None, 'bvals'),'gradient .bvals encoding file'),
                        (self.getUpsamplingImage('grad', None, 'bvecs'),'gradient .bvecs encoding file'),
                        (self.getUpsamplingImage('grad', None, 'benc'),'gradient .b encoding file'),
                        (self.getRegistrationImage('anat', ['freesurfer', 'resample']), 'freesurfer anatomical resample'),
                        (self.getRegistrationImage('mask', 'resample'), 'freesurfer mask resample'))

        #@TODO Add all metrics dependencies

        return images


    def isDirty(self):
        return not self.__finished

    def isIgnore(self):
        return self.get("ignore")

