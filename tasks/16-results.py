from core.generictask import GenericTask
from lib.images import Images
from lib import util

__author__ = 'desmat'

class Results(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'upsampling', 'registration', 'tensormrtrix', 'tensordipy', 'tensorfsl', 'hardidipy','hardimrtrix')
        self.__finished = False

    def implement(self):

        structs = {'dwi': self.getImage(self.upsamplingDir, 'dwi'),
                    'anat': self.getImage(self.registrationDir, 'anat', ['freesurfer', 'resample']),
                    'mask': self.getImage(self.registrationDir, 'mask', 'resample'),
                    'brodmann': self.getImage(self.registrationDir, 'brodmann', 'resample')}

        for postfix, image in structs.iteritems():
           util.copy(image, self.workingDir,  self.buildName(self.subject.getName(), postfix,'nii.gz'))

        for extension in ['bvals', 'bvecs', 'benc']:
            util.copy(self.getImage(self.upsamplingDir, 'grad', None, extension), self.workingDir, self.buildName(self.subject.getName(), None, extension))

	self.__copyMetrics(['mrtrix', 'dipy', 'fsl'], ['fa','ad','rd','md'], 'tensor')
        self.__copyMetrics(['mrtrix', 'dipy'], ['nufo','csd','gfa'], 'hardi')
        self.__finished = True

    def __copyMetrics(self, softwares, postfixs, method):
        for software in softwares:
            for postfix in postfixs:
                source = self.getImage(getattr(self, "{}{}Dir".format(method, software)), "dwi", postfix)
                target = self.buildName(self.subject.getName(), [software, postfix], 'nii.gz')
                util.copy(source, self.workingDir, target)



    def meetRequirement(self):
        images = Images((self.getImage(self.upsamplingDir, 'dwi'), 'diffusion weighted'),
                        (self.getImage(self.upsamplingDir, 'grad', None, 'bvals'),'gradient .bvals encoding file'),
                        (self.getImage(self.upsamplingDir, 'grad', None, 'bvecs'),'gradient .bvecs encoding file'),
                        (self.getImage(self.upsamplingDir, 'grad', None, 'benc'),'gradient .b encoding file'),
                        (self.getImage(self.registrationDir, 'anat', ['freesurfer', 'resample']), 'freesurfer anatomical resample'),
                        (self.getImage(self.registrationDir, 'mask', 'resample'), 'freesurfer mask resample'),
                        (self.getImage(self.registrationDir, 'brodmann', 'resample'), 'brodmann atlas resample'))

        #@TODO Add all metrics dependencies
        return images


    def isDirty(self):
        #@TODO implement that
        return not self.__finished
