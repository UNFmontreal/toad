# -*- coding: utf-8 -*-
from core.generictask import GenericTask
from lib import mriutil
from lib.images import Images


__author__ = 'desmat'

class TractographyMrtrix(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preprocessing', 'hardimrtrix', 'masking', 'registration')


    def implement(self):

        act = self.getImage(self.maskingDir, "aparc_aseg", ["register", "act"])
        seed_gmwmi = self.getImage(self.maskingDir, "aparc_aseg", "5tt2gmwmi")
        brodmann = self.getImage(self.registrationDir, "brodmann", "resample")
        anatBrainResample = self.getImage(self.registrationDir,'anat', ['brain', 'resample'])

        mask253 = self.getImage(self.maskingDir, 'aparc_aseg',['253','mask'])
        mask1024= self.getImage(self.maskingDir, 'aparc_aseg',['1024','mask'])

        dwi = self.getImage(self.dependDir, 'dwi', 'upsample')

        bFile = self.getImage(self.dependDir, 'grad', None, 'b')
        mask = self.getImage(self.maskingDir, 'anat', ['resample', 'extended','mask'])

        tckDet = self.__tckgenTensor(dwi, self.buildName(dwi, 'tckgen_det', 'tck'), mask, act, seed_gmwmi, bFile, 'Tensor_Det')
        tckDetRoi = self.__tckedit(tckDet, [mask253,mask1024 ], self.buildName(tckDet, 'roi','tck'))
        tckDetRoiTrk = mriutil.tck2trk(tckDetRoi, anatBrainResample , self.buildName(dwi, tckDetRoi, 'trk'))
        mriutil.createPng(tckDetRoiTrk, anatBrainResample, mask253)

        tckProb = self.__tckgenTensor(dwi, self.buildName(dwi, 'tckgen_prob', 'tck'), mask, act, seed_gmwmi, bFile, 'Tensor_Prob')
        tckDetProb = self.__tckedit(tckProb, [mask253,mask1024 ], self.buildName(tckProb, 'roi','tck'))
        tckDetProbTrk = mriutil.tck2trk(tckDetProb, anatBrainResample , self.buildName(dwi, tckDetProb, 'trk'))
        mriutil.createPng(tckDetProbTrk, anatBrainResample, mask253)

        self.__tck2connectome(tckDet, brodmann, self.buildName(dwi, 'tckgen_det', 'csv'))
        self.__tck2connectome(tckProb, brodmann, self.buildName(dwi, 'tckgen_prob', 'csv'))

        #HARDI part
        dwi2fod =  self.getImage(self.hardimrtrixDir,'dwi','fod')

        tckgen = self.__tckgenHardi(dwi2fod, act)
        tckgenRoi = self.__tckedit(tckgen, [mask253, mask1024], self.buildName(tckgen, 'roi','tck'))
        tckgenRoiTrk = mriutil.tck2trk(tckgenRoi, anatBrainResample , self.buildName(dwi, tckgenRoi, 'trk'))
        mriutil.createPng(tckgenRoiTrk, anatBrainResample, mask253)


        self.__tck2connectome(tckgen, brodmann, self.buildName(dwi2fod, 'tckgen_prob', 'csv'))
        tcksift = self.__tcksift(tckgen, dwi2fod)
        tcksiftRoi = self.__tckedit(tcksift, [mask253, mask1024], self.buildName(tcksift, 'roi','tck'))
        tcksiftRoiTrk = mriutil.tck2trk(tcksiftRoi, anatBrainResample , self.buildName(dwi, tcksiftRoi, 'trk'))
        tcksiftRoiTrk = mriutil.createPng(tckgenRoiTrk, anatBrainResample, mask253)


    def __tckedit(self, source, include, target, downsample= "2"):

        self.info("Starting tckedit creation from mrtrix on {}".format(source))
        cmd = "tckedit {} {} -downsample {} -quiet ".format(source, target, downsample)
        tmp = self.buildName(source, "tmp", "tck")

        if isinstance(include, basestring):
            cmd += "-include {}".format(include)
        else:
            for element in include:
                cmd += "-include {}".format(element)
        self.launchCommand(cmd)
        return self.rename(tmp, target)



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

        images = Images((self.getImage(self.dependDir,'dwi','upsample'), 'upsampled diffusion weighted'),
                  (self.getImage(self.dependDir, 'grad', None, 'b'), '.b gradient encoding file'),
                  (self.getImage(self.maskingDir, "aparc_aseg", ["register", "act"]), 'resampled anatomically constrained tractography'),
                  (self.getImage(self.maskingDir, "aparc_aseg", "5tt2gmwmi"), 'seeding streamlines 5tt2gmwmi'),
                  (self.getImage(self.registrationDir, "brodmann", "resample"), 'resampled brodmann area'),
                  (self.getImage(self.maskingDir, 'aparc_aseg',['253','mask']), 'area 253 from aparc_aseg'),
                  (self.getImage(self.maskingDir, 'aparc_aseg',['1024','mask']), 'area 1024 from aparc_aseg'),
                  (self.getImage(self.registrationDir,'anat', ['brain', 'resample']), 'anatomical brain resampled'),
                  (self.getImage(self.maskingDir, 'anat',['resample', 'extended','mask']), 'ultimate extended mask'))

        return images.isAllImagesExists()


    def isDirty(self, result = False):

        images = Images((self.getImage(self.workingDir, 'dwi', 'tckgen_det', 'tck'), "deterministic connectome matrix from a streamlines"),
                  (self.getImage(self.workingDir, 'dwi', 'tckgen_det', 'csv'), "deterministic connectome matrix from a streamlines csv"),
                  (self.getImage(self.workingDir, 'dwi', 'tckgen_prob', 'tck'), "probabilistic connectome matrix from a streamlines"),
                  (self.getImage(self.workingDir, 'dwi', 'tckgen_prob', 'csv'), "probabilistic connectome matrix from a streamlines csv"),
                  (self.getImage(self.workingDir, 'dwi', 'tckgen', 'tck'), "tckgen streamlines tractography"),
                  (self.getImage(self.workingDir, 'dwi', 'tcksift', 'tck'), 'tcksift'))
        return images.isSomeImagesMissing()


    def qaSupplier(self):

        tckgenDet = self.getImage(self.workingDir, 'dwi', 'tckgen_det', 'csv')
        tckgenProb = self.getImage(self.workingDir, 'dwi', 'tckgen_prob', 'csv')
        fodProb = self.getImage(self.workingDir, 'dwi', ['fod', 'tckgen_prob'], 'csv')

        tckgenDetPlot = mriutil.plotConnectome(tckgenDet, self.buildName(tckgenDet, None, "png"))
        tckgenProbPlot = mriutil.plotConnectome(tckgenProb, self.buildName(tckgenProb, None, "png"))
        fodProbPlot = mriutil.plotConnectome(fodProb, self.buildName(fodProb, None, "png"))



        images = Images((tckgenDetPlot, 'Connectome matrix from a deterministic streamlines'),
                       (tckgenProbPlot,'Connectome matrix from a probabilistic streamlines'),
                       (fodProbPlot, 'Connectome matrix from a fod probabilistic streamlines'))

        print images
        return images