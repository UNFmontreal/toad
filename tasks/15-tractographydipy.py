from core.generictask import GenericTask
from lib.images import Images
from lib import mriutil
import nibabel, numpy
from dipy.tracking.local import ActTissueClassifier, LocalTracking
from dipy.direction import DeterministicMaximumDirectionGetter
from dipy.data import default_sphere
from dipy.io.trackvis import save_trk
import matplotlib
matplotlib.use('Agg')

__author__ = 'desmat'

class TractographyDipy(GenericTask):

    def __init__(self, subject):

        GenericTask.__init__(self, subject, "masking", "hardimrtrix")


    def implement(self):

        act = self.getImage(self.maskingDir, "aparc_aseg", ['resample', 'act'])
        csd = self.getImage(self.hardimrtrixDir, "dwi", 'csd')
        """
        actImage = nibabel.load(act)
        csdImage = nibabel.load(csd)

        actData = actImage.get_data()

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

        #concatenate grey and kernel information from act
        includeData  = numpy.logical_or(actData[:,:,:,0], actData[:,:,:,1])
        includeImage = nibabel.Nifti1Image(includeData.astype(numpy.float32), actImage.get_affine())
        nibabel.save(includeImage, self.buildName(act, "include"))
        excludeData = actData[:,:,:,3] #csf
        csdData = csdImage.get_data()

        classifier = ActTissueClassifier(includeData, excludeData)
	
	figure = matplotlib.figure()
	matplotlib.subplot(121)
	matplotlib.xticks([])
	matplotlib.yticks([])
	matplotlib.imshow(includeData[:, :, actData.shape[2] / 2].T, cmap='gray', origin='lower',
		   interpolation='nearest')
	matplotlib.subplot(122)
	matplotlib.xticks([])
	matplotlib.yticks([])
	matplotlib.imshow(excludeData[:, :, actData.shape[2] / 2].T, cmap='gray', origin='lower',
		   interpolation='nearest')
	figure.tight_layout()
	figure.savefig('act_maps.png')
        
        print "includeImage.get_affine()=", includeImage.get_affine()
        print "csdImage.get_affine()=",csdImage.get_affine()
        deterministicGetter = DeterministicMaximumDirectionGetter.from_shcoeff(csdData,
                                                      max_angle=30.,
                                                      sphere=default_sphere)


        validStreamlinesActClassifier = LocalTracking(deterministicGetter,
                                                         classifier,
                                                         actData[:,:,:,2], #white matter
                                                         csdImage.get_affine(),
                                                         step_size=.5,
                                                         return_all=False)


     	print validStreamlinesActClassifier.maxlen
        print validStreamlinesActClassifier.direction_getter
        print validStreamlinesActClassifier.tissue_classifier
        print validStreamlinesActClassifier.step_size
        print validStreamlinesActClassifier.fixed
        print validStreamlinesActClassifier.max_cross
        print validStreamlinesActClassifier._voxel_size
        #@TODO find a souton for label
        save_trk("deterministic_act_classifier_valid.trk",
                 validStreamlinesActClassifier,
                 csdImage.get_affine(),
                 includeData.shape)

        """
    def isIgnore(self):
        return self.get("ignore").lower() in "true"


    def meetRequirement(self):
        return Images((self.getImage(self.maskingDir, "aparc_aseg", ["resample", "act"]), 'resampled anatomically constrained tractography'),
                      (self.getImage(self.hardimrtrixDir, "dwi", 'csd'), 'constrained spherical deconvolution'))\
            .isAllImagesExists()

    def isDirty(self):
        return True
