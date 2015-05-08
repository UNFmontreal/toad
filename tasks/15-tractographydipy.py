from core.generictask import GenericTask
from lib.images import Images
from lib import mriutil
import nibabel, numpy
from dipy.tracking.local import ActTissueClassifier, LocalTracking
from dipy.direction import DeterministicMaximumDirectionGetter
from dipy.data import default_sphere
from dipy.io.trackvis import save_trk

__author__ = 'desmat'

class TractographyDipy(GenericTask):

    def __init__(self, subject):

        GenericTask.__init__(self, subject, "masking", "hardimrtrix")


    def implement(self):

        act = self.getImage(self.maskingDir, "aparc_aseg", ['resample', 'act'])
        csd = self.getImage(self.hardimrtrixDir, "dwi", 'csd')

        actImage = nibabel.load(act)
        csdImage = nibabel.load(csd)

        actImage = actImage.get_data()
        print actImage.shape
        self.quit()

        #gm = self.buildName(act, "gm")
        #kernel = self.buildName(act, "kernel")
        #wm = self.buildName(act, "wm")
        #csf = self.buildName(act, "csf") #exclude

        #for area, target in { 0: gm, 1: kernel, 2: wm , 3: csf}.iteritems():
        #    self.info(mriutil.extractSubVolume(act, target, 3, area, self.getNTreadsMrtrix()))

        #include = self.buildName(act, "include")
        #self.info("Add {} and {} images together in order to create input image"
        #          .format(gm, kernel))

        #self.info(mriutil.fslmaths(gm, include, 'add', kernel))
        #self.__createMask(extended)

        #includeImage = nibabel.load(include)
        #excludeImage = nibabel.load(csf)
        #csdImage = nibabel.load(csd)


        #includeData  = includeImage.get_data()
        #excludeData = excludeImage.get_data()
        csdData = csdImage.get_data()

        classifier = ActTissueClassifier(includeData, excludeData)
        classifierImage = nibabel.Nifti1Image(classifier.astype(numpy.float32), includeData.get_affine())
        nibabel.save(classifierImage, self.buildName(act, "classifier"))


        deterministicGetter = DeterministicMaximumDirectionGetter.from_shcoeff(csdImage.shm_coeff,
                                                      max_angle=30.,
                                                      sphere=default_sphere)


        validStreamlinesActClassifier = LocalTracking(deterministicGetter,
                                                         classifier,
                                                         wm,
                                                         includeData.get_affine(),
                                                         step_size=.5,
                                                         return_all=False)

        #@TODO find a souton for label
        save_trk("deterministic_act_classifier_valid.trk",
                 validStreamlinesActClassifier,
                 includeData.get_affine(),
                 includeData.shape)


    def isIgnore(self):
        return self.get("ignore").lower() in "true"


    def meetRequirement(self):
        return Images(self.getImage(self.workingDir, "aparc_aseg", ["resample", "act"]), 'resampled anatomically constrained tractography',
                      self.getImage(self.hardimrtrixDir, "dwi", 'csd'), 'constrained spherical deconvolution')\
            .isSomeImagesMissing()

    def isDirty(self):
        return True
