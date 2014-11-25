# -*- coding: utf-8 -*-
from generic.tractography import Tractography
from generic.generictask import GenericTask

__author__ = 'desmat'

class HardiTractography(GenericTask, Tractography):

    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'hardi', 'registration' ,'masking')


    def implement(self):

        act = self.getImage(self.maskingDir,"aparc_aseg", ["resample","act"])
        seed_gmwmi = self.getImage(self.maskingDir,"aparc_aseg", "5tt2gmwmi")
        brodmann = self.getImage(self.registrationDir, "brodmann", "resample")

        dwi2fod =  self.getImage(self.dependDir,'dwi','fod')
        mask = self.getImage(self.maskingDir, 'anat',['extended','mask'])
        tckgen = self.tckgen(dwi2fod, self.getTarget(dwi2fod, 'tckgen','.tck'), mask, act, seed_gmwmi)
        self.tck2connectome(tckgen, brodmann, self.getTarget(dwi2fod, 'tckgen_det', 'csv'))
        self.tcksift(tckgen, dwi2fod)


    def meetRequirement(self, result = True):

        images = {"constrained spherical deconvolution": self.getImage(self.dependDir, 'dwi', 'fod'),
                  "resampled anatomically constrained tractography": self.getImage(self.maskingDir, "aparc_aseg", ["resample", "act"]),
                  "seeding streamlines 5tt2gmwmi": self.getImage(self.maskingDir, "aparc_aseg","5tt2gmwmi"),
                  'ultimate extended mask': self.getImage(self.maskingDir, 'anat',['extended','mask'])}

        if self.isSomeImagesMissing(images):
            result = False

        return result


    def isDirty(self, result = False):

        images = {"tckgen streamlines tractography": self.getImage(self.workingDir, 'dwi', 'tckgen', 'tck'),
                  'tcksift': self.getImage(self.workingDir, 'dwi', 'tcksift', 'tck')}

        return self.isSomeImagesMissing(images)

