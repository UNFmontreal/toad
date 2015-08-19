from core.generictask import GenericTask
from lib.images import Images
from lib import mriutil

__author__ = 'desmat'

class Results(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'upsampling', 'registration')


    def implement(self):

        structs = {'dwi': self.getImage(self.upsamplingDir, 'dwi'),
                    'bVals': self.getImage(self.upsamplingDir, 'grad', None, 'bvals'),
                    'bVecs': self.getImage(self.upsamplingDir, 'grad', None, 'bvecs'),
                    'bEnc': self.getImage(self.upsamplingDir, 'grad', None, 'benc'),
                    'anat': self.getImage(self.registrationDir, 'anat', ['freesurfer', 'resample']),
                    'mask': self.getImage(self.registrationDir, 'mask', 'resample'),
                    'brodmann': self.getImage(self.registrationDir, 'brodmann', 'resample')}


        for prefix, image in structs.iteritems():
           mriutil.copy(image, self.workingDir,  self.buildName(self.subject.getName(), prefix))

        softwares = ['mrtrix', 'dipy', 'fsl']
        prefixs = ['fa','ad','rd','md']
        for software in softwares:
            for metric in prefixs:
                source = self.getImage(getattr("tensor{}Dir".format(software), "dwi", prefixs))
                target = self.buildName(self.subject.getName(), [prefix, software])
                print "source is = ", source
                print "target is = ", target
                mriutil.copy(source, self.workingDir, target)

        for prefix in ['nufo', 'gfa', 'rgb']:
            source = self.getImage(getattr("tensordipy", "dwi", prefix))
            target = self.buildName(self.subject.getName(), [prefix, 'dipy'])
            mriutil.copy(source, self.workingDir, target)


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
        return True