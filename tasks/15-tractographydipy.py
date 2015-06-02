from core.generictask import GenericTask
from lib.images import Images
import nibabel, numpy
from dipy.tracking.local import ActTissueClassifier, LocalTracking
from dipy.direction import DeterministicMaximumDirectionGetter, ProbabilisticDirectionGetter
from lib import mriutil
from dipy.data import default_sphere
from dipy.io.trackvis import save_trk
from dipy.tracking import utils
import matplotlib
matplotlib.use('Agg')

__author__ = 'desmat'

class TractographyDipy(GenericTask):

    def __init__(self, subject):

        GenericTask.__init__(self, subject, "masking", "registration", "hardidipy")


    def implement(self):

        act = self.getImage(self.maskingDir, "aparc_aseg", ['resample', 'act'])
        csd = self.getImage(self.hardidipyDir, "dwi", 'csd')
        mask253 = self.getImage(self.maskingDir, 'aparc_aseg',['253','mask'])
        anatBrainResample = self.getImage(self.registrationDir,'anat', ['brain', 'resample'])

        actImage = nibabel.load(act)
        csdImage = nibabel.load(csd)

        actData = actImage.get_data()

        #concatenate grey and kernel information from act
        includeData  = numpy.logical_or(actData[:,:,:,0], actData[:,:,:,1])
        includeImage = nibabel.Nifti1Image(includeData.astype(numpy.float32), actImage.get_affine())
        nibabel.save(includeImage, self.buildName(act, "include"))
        excludeData = actData[:,:,:,3]

        step_det = self.config.getfloat('tractographydipy', 'step_det')
        step_prob = self.config.getfloat('tractographydipy', 'step_prob')
        density = self.config.getint('tractographydipy', 'density')

        csdData = csdImage.get_data()
        classifier = ActTissueClassifier(includeData, excludeData)

        deterministicGetter = DeterministicMaximumDirectionGetter.from_shcoeff(csdData,
                                                      max_angle=30.,
                                                      sphere=default_sphere)

        probabilisticGetter = ProbabilisticDirectionGetter.from_shcoeff(csdData,
                                                      max_angle=30.,
                                                      sphere=default_sphere)

        seeds = utils.seeds_from_mask(actData[:,:,:,2], density=density, affine=actImage.get_affine())

        deterministicValidStreamlinesActClassifier = LocalTracking(deterministicGetter,
                                                         classifier,
                                                         seeds,
                                                         csdImage.get_affine(),
                                                         step_size=step_det,
                                                         return_all=False)

        probabilisticValidStreamlinesActClassifier = LocalTracking(probabilisticGetter,
                                                         classifier,
                                                         seeds,
                                                         csdImage.get_affine(),
                                                         step_size=step_prob,
                                                         return_all=False)


        tckDet = self.buildName(csd, 'hardi_det', 'trk')
        tckProb = self.buildName(csd, 'hardi_prob', 'trk')

        save_trk(tckDet,
                 deterministicValidStreamlinesActClassifier,
                 csdImage.get_affine(),
                 includeData.shape)


        tckDetRoi = self.__tckedit(tckDet, mask253, self.buildName(tckDet, 'roi','tck'))
        tckDetRoiTrk = mriutil.tck2trk(tckDetRoi, anatBrainResample , self.buildName(tckDetRoi, None, 'trk'))

        save_trk(tckProb,
                 probabilisticValidStreamlinesActClassifier,
                 csdImage.get_affine(),
                 includeData.shape)
        tckProbRoi = self.__tckedit(tckProb, mask253, self.buildName(tckProb, 'roi','tck'))
        tckProbRoiTrk = mriutil.tck2trk(tckProbRoi, anatBrainResample , self.buildName(tckProbRoi, None, 'trk'))

        #create PNG
        if self.config.getboolean('general', 'vtk_available'):
            mriutil.createVtkPng(tckDetRoiTrk, anatBrainResample, mask253)
            mriutil.createVtkPng(tckProbRoiTrk, anatBrainResample, mask253)


    def __tckedit(self, source, roi, target, downsample= "2"):
        """ perform various editing operations on track files.

        Args:
            source: the input track file(s)
            roi:    specify an inclusion region of interest, as either a binary mask image, or as a sphere
                    using 4 comma-separared values (x,y,z,radius)
            target: the output track file
            downsample: increase the density of points along the length of the streamline by some factor

        Returns:
            the output track file
        """
        self.info("Starting tckedit creation from mrtrix on {}".format(source))
        tmp = self.buildName(source, "tmp", "tck")
        mriutil.tckedit(source, roi, tmp, downsample)
        return self.rename(tmp, target)


    def isIgnore(self):
        return self.get("ignore").lower() in "true"


    def meetRequirement(self):
        images = Images((self.getImage(self.maskingDir, "aparc_aseg", ["resample", "act"]), 'resampled anatomically constrained tractography'),
                      (self.getImage(self.hardidipyDir, "dwi", 'csd'), 'constrained spherical deconvolution'))
        return images.isAllImagesExists()


    def isDirty(self):
        images = Images((self.getImage(self.workingDir, 'dwi', 'hardi_det', 'tck'), "deterministic streamlines act classifier"),
                  (self.getImage(self.workingDir, 'dwi', 'hardi_prob', 'tck'), "probabilistic streamlines act classifier"))
        return images.isSomeImagesMissing()


    def qaSupplier(self):

        hardiDetPng = self.getImage(self.workingDir, 'dwi', ['hardi_det', 'roi'], 'png')
        hardiProbPng = self.getImage(self.workingDir, 'dwi', ['hardi_prob', 'roi'], 'png')
        images = Images((hardiDetPng, 'fiber crossing aparc_aseg area 253 from a deterministic tensor streamlines'),
                       (hardiProbPng, 'fiber crossing aparc_aseg area 253 from a probabilistic tensor streamlines'))

        return images