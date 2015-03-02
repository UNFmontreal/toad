from lib.generictask import GenericTask
import dipy
import dipy.direction
import dipy.reconst.csdeconv
import nibabel
import numpy

__author__ = 'desmat'

class HardiDipy(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preprocessing', 'masking')


    def implement(self):

        dwi = self.getImage(self.dependDir, 'dwi', 'upsample')
        mask = self.getImage(self.maskingDir, 'anat', ['resample', 'extended', 'mask'])

        #Look first if there is eddy b encoding files produces
        bValFile = self.getImage(self.dependDir, 'grad', None, 'bval')
        bVecFile = self.getImage(self.dependDir, 'grad', None, 'bvec')
        self.__produceHardiMetric(dwi, bValFile, bVecFile, mask)


    def __produceHardiMetric(self, source, bValFile, bVecFile, mask):
        self.info("Starting tensors creation from dipy on {}".format(source))
        #target = self.buildName(source, "dipy")

        dwiImage = nibabel.load(source)
        maskImage = nibabel.load(mask)

        dwiData  = dwiImage.get_data()
        maskData = maskImage.get_data()
        dwiData = dipy.segment.mask.applymask(dwiData, maskData)

        gradientTable = dipy.core.gradients.gradient_table(numpy.loadtxt(bValFile), numpy.loadtxt(bVecFile))
        sphere = dipy.data.get_sphere('symmetric724')

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
        target = self.buildName(source,'nufo')
        nuDirs = gfa
        for x in range(gfa.shape[0]):
            for y in range(gfa.shape[1]):
                for z in range(gfa.shape[2]):
                    nuDirs[x,y,z] = numpy.count_nonzero(csdPeaks.peak_dirs[x,y,z]!=0)/3

        numDirsImage = nibabel.Nifti1Image(nuDirs.astype(numpy.float32), dwiImage.get_affine())
        nibabel.save(numDirsImage, target)


    def meetRequirement(self):
        images = {"upsampled diffusion":self.getImage(self.dependDir, 'dwi', 'upsample'),
                  "gradient value bval encoding file":  self.getImage(self.dependDir, 'grad', None, 'bval'),
                  "gradient vector bvec encoding file":  self.getImage(self.dependDir, 'grad', None, 'bvec'),
                  'ultimate extended mask':  self.getImage(self.maskingDir, 'anat', ['resample', 'extended', 'mask'])}
        return self.isAllImagesExists(images)


    def isDirty(self):
        images = {"csd": self.getImage(self.workingDir, 'dwi', 'csd'),
                  "generalised Fractional Anisotropy": self.getImage(self.workingDir,'dwi', 'gfa'),
                  'nufo': self.getImage(self.workingDir,'dwi', 'nufo')}
        return self.isSomeImagesMissing(images)
