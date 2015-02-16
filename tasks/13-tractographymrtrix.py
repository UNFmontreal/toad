# -*- coding: utf-8 -*-
from lib.generictask import GenericTask

__author__ = 'desmat'

class TractographyMrtrix(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preprocessing', 'hardimrtrix', 'masking', 'registration')


    def implement(self):

        act = self.getImage(self.maskingDir, "aparc_aseg", ["register", "act"])
        seed_gmwmi = self.getImage(self.maskingDir, "aparc_aseg", "5tt2gmwmi")
        brodmann = self.getImage(self.registrationDir, "brodmann", "resample")

        dwi = self.getImage(self.dependDir, 'dwi', 'upsample')

        bFile = self.getImage(self.dependDir, 'grad', None, 'b')
        mask = self.getImage(self.maskingDir, 'anat', ['extended','mask'])

        tckDet = self.__tckgenTensor(dwi, self.buildName(dwi, 'tckgen_det', 'tck'), mask, act, seed_gmwmi, bFile, 'Tensor_Det')
        tckProb = self.__tckgenTensor(dwi, self.buildName(dwi, 'tckgen_prob', 'tck'), mask, act, seed_gmwmi, bFile, 'Tensor_Prob')

        self.__tck2connectome(tckDet, brodmann, self.buildName(dwi, 'tckgen_det', 'csv'))
        self.__tck2connectome(tckProb, brodmann, self.buildName(dwi, 'tckgen_prob', 'csv'))


        #HARDI part
        dwi2fod =  self.getImage(self.hardimrtrixDir,'dwi','fod')

        tckgen = self.__tckgenHardi(dwi2fod, act)
        self.__tck2connectome(tckgen, brodmann, self.buildName(dwi2fod, 'tckgen_prob', 'csv'))
        self.__tcksift(tckgen, dwi2fod)


    def __tckgenTensor(self, source, target, mask = None, act = None , seed_gmwmi = None, bFile = None, algorithm = "iFOD2"):
        """ perform streamlines tractography.

             the image containing the source data. The type of data
             depends on the algorithm used:
             - FACT: the directions file (each triplet of volumes is
             the X,Y,Z direction of a fibre population).
             - iFOD1/2 & SD_Stream: the SH image resulting from CSD.
             - Nulldist & SeedTest: any image (will not be used).
             - TensorDet / TensorProb: the DWI image.

        Args:
            source: the image containing the source data.
            target: the output file containing the tracks generated.
            bFile: specify the diffusion-weighted gradient scheme used in the acquisition.
            mask: specify a masking region of interest, as a binary mask image.
            act: use the Anatomically-Constrained Tractography framework during tracking
            seed_gmwmi: seed from the grey matter - white matter interface (only valid if using ACT framework)
            algorithm: the tractography algorithm to use. default: iFOD2

        Returns:
            The resulting streamlines tractography filename generated

        """
        self.info("Starting tckgen creation from mrtrix on {}".format(source))
        tmp = self.buildName(source, "tmp", "tck")
        cmd = "tckgen {} {}  -mask {} -act {} -seed_gmwmi {} -number {} -algorithm {} -nthreads {} -quiet"\
            .format(source, tmp, mask,  act, seed_gmwmi, self.get('number_tracks'), algorithm, self.getNTreadsMrtrix())

        if bFile is not None:
            cmd += " -grad {}".format(bFile)

        self.launchCommand(cmd)
        return self.rename(tmp, target)



    def __tck2connectome(self, source, nodes, target):
        """ generate a connectome matrix from a streamlines file and a node parcellation image

        Args:
            source: the input track file
            nodes: the input parcellation image
            target: the output .csv file containing edge weights

        Returns:
            The resulting .cvs file name

        """
        self.info("Starting tck2connectome from mrtrix on {}".format(source))
        tmp = self.buildName(source, "tmp", "csv")
        cmd = "tck2connectome {} {} {} -quiet -nthreads {}".format(source, nodes, tmp, self.getNTreadsMrtrix() )

        self.launchCommand(cmd)
        return self.rename(tmp, target)


    def __tckgenHardi(self, source, act = None, bFile = None, algorithm = "iFOD2"):
        """
         perform streamlines tractography.

             the image containing the source data. The type of data
             depends on the algorithm used:
             - FACT: the directions file (each triplet of volumes is
             the X,Y,Z direction of a fibre population).
             - iFOD1/2 & SD_Stream: the SH image resulting from CSD.
             - Nulldist & SeedTest: any image (will not be used).
             - TensorDet / TensorProb: the DWI image.

        Args:
            source: the image containing the source data.
            bFile: specify the diffusion-weighted gradient scheme used in the acquisition.
            mask: specify a masking region of interest, as a binary mask image.
            act: use the Anatomically-Constrained Tractography framework during tracking
            algorithm: the tractography algorithm to use. default: iFOD2

        Returns:
            The resulting streamlines tractography filename generated
        """

        self.info("Starting tckgen creation from mrtrix on {}".format(source))
        tmp = self.buildName(source, "tmp", "tck")
        target = self.buildName(source, 'tckgen','.tck')
        cmd = "tckgen {} {} -act {} -seed_dynamic {} -step {} -maxlength {} -number {} -algorithm {} -backtrack -nthreads {} -quiet"\
            .format(source, tmp, act, source, self.get('step'), self.get('maxlength'), self.get( 'number_tracks'), algorithm, self.getNTreadsMrtrix())

        if bFile is not None:
            cmd += " -grad {}".format(bFile)

        self.launchCommand(cmd)
        return self.rename(tmp, target)


    def __tcksift(self, source, dwi2fod):
        """ filter a whole-brain fibre-tracking data set such that the streamline densities match the FOD lobe integral.

        Args:
            source: the input track file.
            dwi2fod: input image containing the spherical harmonics of the fibre orientation distributions

        Returns:
            The resulting output filtered tracks file

        """
        tmp = self.buildName(source, "tmp", "tck")
        target = self.buildName(source, 'tcksift','.tck')
        self.info("Starting tcksift creation from mrtrix on {}".format(source))

        cmd = "tcksift {} {} {} -nthreads {} -quiet".format(source, dwi2fod, tmp, self.getNTreadsMrtrix())
        self.launchCommand(cmd)

        return self.rename(tmp, target)


    def meetRequirement(self):

        images = {'upsampled diffusion weighted':self.getImage(self.dependDir,'dwi','upsample'),
                    '.b gradient encoding file': self.getImage(self.dependDir, 'grad', None, 'b'),
                    'resampled anatomically constrained tractography':self.getImage(self.maskingDir, "aparc_aseg", ["register", "act"]),
                    'seeding streamlines 5tt2gmwmi' :self.getImage(self.maskingDir, "aparc_aseg", "5tt2gmwmi"),
                    'resampled brodmann area':self.getImage(self.registrationDir, "brodmann", "resample"),
                    'ultimate extended mask': self.getImage(self.maskingDir, 'anat',['extended','mask'])}

        return self.isAllImagesExists(images)


    def isDirty(self, result = False):

        images = {"deterministic connectome matrix from a streamlines": self.getImage(self.workingDir, 'dwi', 'tckgen_det', 'tck'),
                  "deterministic connectome matrix from a streamlines csv ": self.getImage(self.workingDir, 'dwi', 'tckgen_det', 'csv'),
                  "probabilistic connectome matrix from a streamlines": self.getImage(self.workingDir, 'dwi', 'tckgen_prob', 'tck'),
                  "probabilistic connectome matrix from a streamlines csv ": self.getImage(self.workingDir, 'dwi', 'tckgen_prob', 'csv'),
                  "tckgen streamlines tractography": self.getImage(self.workingDir, 'dwi', 'tckgen', 'tck'),
                  'tcksift': self.getImage(self.workingDir, 'dwi', 'tcksift', 'tck')}
        return self.isSomeImagesMissing(images)
