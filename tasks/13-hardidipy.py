import dipy
import dipy.direction
import dipy.reconst.csdeconv
import nibabel
import numpy

from core.generictask import GenericTask
from lib.images import Images

__author__ = 'desmat'

class HardiDipy(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preprocessing', 'masking')


    def implement(self):

        dwi = self.getImage(self.dependDir, 'dwi', 'upsample')
        mask = self.getImage(self.maskingDir, 'anat', ['resample', 'extended', 'mask'])

        #Look first if there is eddy b encoding files produces
        bValsFile = self.getImage(self.dependDir, 'grad', None, 'bvals')
        bVecsFile = self.getImage(self.dependDir, 'grad', None, 'bvecs')
        self.__produceMetrics(dwi, bValsFile, bVecsFile, mask)


    def __produceMetrics(self, source, bValsFile, bVecsFile, mask):
        self.info("Starting tensors creation from dipy on {}".format(source))

        dwiImage = nibabel.load(source)
        maskImage = nibabel.load(mask)

        dwiData  = dwiImage.get_data()
        maskData = maskImage.get_data()
        dwiData = dipy.segment.mask.applymask(dwiData, maskData)

        gradientTable = dipy.core.gradients.gradient_table(numpy.loadtxt(bValsFile), numpy.loadtxt(bVecsFile))
        sphere = dipy.data.get_sphere(self.get("triangulated_spheres"))

        response, ratio = dipy.reconst.csdeconv.auto_response(gradientTable, dwiData, roi_radius=10, fa_thr=0.7)
        csdModel = dipy.reconst.csdeconv.ConstrainedSphericalDeconvModel(gradientTable, response)
        self.info('Start fODF computation')

        csdPeaks = dipy.direction.peaks_from_model(model=csdModel,
                                                                  data=dwiData,
                                                                  sphere=sphere,
                                                                  relative_peak_threshold=.5,
                                                                  min_separation_angle=25,
                                                                  mask=maskData,
                                                                  return_sh=True,
                                                                  return_odf=False,
                                                                  normalize_peaks=True,
                                                                  npeaks=5,
                                                                  parallel=True,
                                                                  nbr_processes=int(self.getNTreads()))

        #CSD
        target = self.buildName(source,'csd')
        csdCoeff = csdPeaks.shm_coeff
        csdCoeffImage = nibabel.Nifti1Image(csdCoeff.astype(numpy.float32), dwiImage.get_affine())
        nibabel.save(csdCoeffImage, target)


        #GFA
        target = self.buildName(source,'gfa')
        gfa = csdPeaks.gfa
        gfa[numpy.isnan(gfa)] = 0
        csdCoeffImage = nibabel.Nifti1Image(gfa.astype(numpy.float32), dwiImage.get_affine())
        nibabel.save(csdCoeffImage, target)


        #NUFO
        target = self.buildName(source, 'nufo')
        nuDirs = gfa
        for x in range(gfa.shape[0]):
            for y in range(gfa.shape[1]):
                for z in range(gfa.shape[2]):
                    nuDirs[x,y,z] = numpy.count_nonzero(csdPeaks.peak_dirs[x,y,z]!=0)/3

        numDirsImage = nibabel.Nifti1Image(nuDirs.astype(numpy.float32), dwiImage.get_affine())
        nibabel.save(numDirsImage, target)


    def isIgnore(self):
        return self.get("ignore").lower() in "true"


    def meetRequirement(self):
        images = Images((self.getImage(self.dependDir, 'dwi', 'upsample'), "upsampled diffusion"),
                  (self.getImage(self.dependDir, 'grad', None, 'bvals'), "gradient value bvals encoding file"),
                  (self.getImage(self.dependDir, 'grad', None, 'bvecs'), "gradient vector bvecs encoding file"),
                  (self.getImage(self.maskingDir, 'anat', ['resample', 'extended', 'mask']), 'ultimate extended mask'))
        return images.isAllImagesExists()


    def isDirty(self):
        images = Images((self.getImage(self.workingDir, 'dwi', 'csd'), "constrained spherical deconvolution"),
                  (self.getImage(self.workingDir,'dwi', 'gfa'), "generalised Fractional Anisotropy"),
                  (self.getImage(self.workingDir,'dwi', 'nufo'), 'nufo'))
        return images.isSomeImagesMissing()
