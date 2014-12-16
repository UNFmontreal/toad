# -*- coding: utf-8 -*-
from lib.tractography import Tractography
from lib.generictask import GenericTask

__author__ = 'desmat'

class TensorsTractography(GenericTask, Tractography):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'tensors', 'masking', 'unwarping', 'preprocessing', 'preparation', 'registration')


    def implement(self):
        act = self.getImage(self.maskingDir, "aparc_aseg", ["resample", "act"])
        seed_gmwmi = self.getImage(self.maskingDir, "aparc_aseg", "5tt2gmwmi")
        brodmann = self.getImage(self.registrationDir, "brodmann", "resample")

        dwi = self.getImage(self.preprocessingDir, 'dwi', 'upsample')
        bFile = self.getImage(self.unwarpingDir, 'grad', None, 'b')
        if not bFile:
            bFile = self.getImage(self.preparationDir, 'grad', None, 'b')

        mask = self.getImage(self.maskingDir, 'anat', ['extended','mask'])

        tckDet = self.tckgen(dwi, self.buildName(dwi, 'tckgen_det', 'tck'), mask, act, seed_gmwmi, bFile, 'Tensor_Det')
        tckProb = self.tckgen(dwi, self.buildName(dwi, 'tckgen_prob', 'tck'), mask, act, seed_gmwmi, bFile, 'Tensor_Prob')

        self.tck2connectome(tckDet, brodmann, self.buildName(dwi, 'tckgen_det', 'csv'))
        self.tck2connectome(tckProb, brodmann, self.buildName(dwi, 'tckgen_prob', 'csv'))


    def meetRequirement(self, result = True):


        if self.isSomeImagesMissing({'.b gradient encoding file': self.getImage(self.unwarpingDir, 'grad', None, 'b')}):
            if self.isSomeImagesMissing({'.b gradient encoding file': self.getImage(self.preparationDir, 'grad', None, 'b')}):
                result = False

        images = {'upsampled diffusion weighted':self.getImage(self.preprocessingDir,'dwi','upsample'),
                    'resampled anatomically constrained tractography':self.getImage(self.maskingDir, "aparc_aseg", ["resample", "act"]),
                    'seeding streamlines 5tt2gmwmi' :self.getImage(self.maskingDir, "aparc_aseg", "5tt2gmwmi"),
                    'resampled brodmann area':self.getImage(self.registrationDir, "brodmann", "resample"),
                    'ultimate extended mask': self.getImage(self.maskingDir, 'anat',['extended','mask'])}

        if self.isSomeImagesMissing(images):
            result = False

        return result


    def isDirty(self, result = False):

        images = {"deterministic connectome matrix from a streamlines": self.getImage(self.workingDir, 'dwi', 'tckgen_det', 'tck'),
                  "deterministic connectome matrix from a streamlines csv ": self.getImage(self.workingDir, 'dwi', 'tckgen_det', 'csv')}

        return self.isSomeImagesMissing(images)
