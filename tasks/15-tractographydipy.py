from core.generictask import GenericTask
from lib.images import Images
from lib import mriutil
import nibabel, numpy
from dipy.tracking.local import ActTissueClassifier, LocalTracking
from dipy.direction import DeterministicMaximumDirectionGetter, ProbabilisticDirectionGetter

from dipy.data import default_sphere
from dipy.io.trackvis import save_trk
from dipy.tracking import utils
import matplotlib
matplotlib.use('Agg')

__author__ = 'desmat'

class TractographyDipy(GenericTask):

    def __init__(self, subject):

        GenericTask.__init__(self, subject, "masking", "hardidipy")


    def implement(self):

        act = self.getImage(self.maskingDir, "aparc_aseg", ['resample', 'act'])
        csd = self.getImage(self.hardidipyDir, "dwi", 'csd')

        actImage = nibabel.load(act)
        csdImage = nibabel.load(csd)

        actData = actImage.get_data()

        #concatenate grey and kernel information from act
        includeData  = numpy.logical_or(actData[:,:,:,0], actData[:,:,:,1])
        includeImage = nibabel.Nifti1Image(includeData.astype(numpy.float32), actImage.get_affine())
        nibabel.save(includeImage, self.buildName(act, "include"))
        excludeData = actData[:,:,:,3] #csf


        csdData = csdImage.get_data()
        classifier = ActTissueClassifier(includeData, excludeData)

        deterministicGetter = DeterministicMaximumDirectionGetter.from_shcoeff(csdData,
                                                      max_angle=30.,
                                                      sphere=default_sphere)

        probabilisticGetter = ProbabilisticDirectionGetter.from_shcoeff(csdData,
                                                      max_angle=30.,
                                                      sphere=default_sphere)

        seeds = utils.seeds_from_mask(actData[:,:,:,2], density=1, affine=actImage.get_affine())

        deterministicValidStreamlinesActClassifier = LocalTracking(deterministicGetter,
                                                         classifier,
                                                         seeds, #white matter
                                                         csdImage.get_affine(),
                                                         step_size=.5,
                                                         return_all=False)

        probabilisticValidStreamlinesActClassifier = LocalTracking(probabilisticGetter,
                                                         classifier,
                                                         seeds, #white matter
                                                         csdImage.get_affine(),
                                                         step_size=.5,
                                                         return_all=False)


        save_trk("deterministic_act_classifier_valid.trk",
                 deterministicValidStreamlinesActClassifier,
                 csdImage.get_affine(),
                 includeData.shape)

        save_trk("probabilistic_act_classifier_valid.trk",
                 probabilisticValidStreamlinesActClassifier,
                 csdImage.get_affine(),
                 includeData.shape)

    def isIgnore(self):
        return self.get("ignore").lower() in "true"


    def meetRequirement(self):
        return Images((self.getImage(self.maskingDir, "aparc_aseg", ["resample", "act"]), 'resampled anatomically constrained tractography'),
                      (self.getImage(self.hardidipyDir, "dwi", 'csd'), 'constrained spherical deconvolution'))\
            .isAllImagesExists()

    def isDirty(self):
        return True
