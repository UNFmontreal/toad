from lib.generictask import GenericTask
import dipy
import nibabel
import numpy

__author__ = 'desmat'

class HardiDipy(GenericTask):


    def __init__(self, subject):
        """A preset format, used as a starting point for developing a toad task

        Simply copy and rename this file:  cp xxxxx.template yourtaskname.py into the tasks folder.
            XX is simply a 2 digit number that represent the order the tasks will be executed.
            yourtaskname is any name at your convenience. the name must be lowercase
        Change the class name Template for Yourtaskname. Note the first letter of the name should be capitalized

        A directory called XX-yourtaskname will be create into the subject dir. A local variable self.workingDir will
        be initialize to that directory

        Args:
            subject: a Subject instance inherit by the subjectmanager.

        """

        GenericTask.__init__(self, subject, 'preprocessing', 'preparation', 'eddy', 'masking')
        """Inherit from a generic Task.

        Args:
            subject: Subject instance inherit by the subjectmanager.

            Note that you may supply additional arguments to generic tasks.
            Exemple: if you provide Task.__init__(self, subject, foo, bar ...)
            toad will create an variable fooDir and barDir and then create an alias 'dependDir'
            that will point to the first additionnal argurments fooDir.

        """


    def implement(self):
        """Placeholder for the business logic implementation

        """
        """
        dwi = self.getImage(self.dependDir, 'dwi', 'upsample')
        mask = self.getImage(self.maskingDir, 'anat', ['extended', 'mask'])

        #Look first if there is eddy b encoding files produces
        bValFile = self.getImage(self.eddyDir, 'grad', None, 'bval')
        bVecFile = self.getImage(self.eddyDir, 'grad', None, 'bvec')

        if not bValFile:
            bValFile = self.getImage(self.preparationDir,'grad', None, 'bval')

        if not bVecFile:
            bVecFile = self.getImage(self.preparationDir,'grad', None, 'bvec')

        self.__produceFodf(dwi, bValFile, bVecFile, mask)
        """
        pass

    def __produceFodf(self, source, bValFile, bVecFile, mask):
        self.info("Starting tensors creation from dipy on {}".format(source))
        target = self.buildName(source, "dipy")

        dwiImage = nibabel.load(source)
        maskImage = nibabel.load(mask)

        dwiData  = dwiImage.get_data()
        dwiData = dipy.segment.mask.applymask(dwiData, maskImage)

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
                                                                  mask=dwiData,
                                                                  return_sh=True,
                                                                  return_odf=False,
                                                                  normalize_peaks=True,
                                                                  npeaks=5,
                                                                  parallel=True,
                                                                  nbr_processes=int(self.getNTreads))

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
        """Validate if all requirements have been met prior to launch the task

        Returns:
            True if all requirement are meet, False otherwise
        """
        return True


    def isDirty(self):
        """Validate if this tasks need to be submit during the execution

        Returns:
            True if any expected file or resource is missing, False otherwise
        """
        return True
