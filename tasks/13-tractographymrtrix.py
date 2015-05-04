# -*- coding: utf-8 -*-
from core.generictask import GenericTask
from lib import mriutil
from lib.images import Images


__author__ = 'desmat'

class TractographyMrtrix(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preprocessing', 'hardimrtrix', 'masking', 'registration','qa')

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
         
        #tensor part
        tckDet = self.__tckgenTensor(dwi, self.buildName(dwi, 'tensor_det', 'tck'), mask, act, seed_gmwmi, bFile, 'Tensor_Det')
        tckDetConnectome = self.__tck2connectome(tckDet, brodmann, self.buildName(tckDet, 'connectome', 'csv'))
        mriutil.plotConnectome(tckDetConnectome, self.buildName(tckDetConnectome, None, "png"))
        tckDetRoi = self.__tckedit(tckDet, mask253, self.buildName(tckDet, 'roi','tck'))
        tckDetRoiTrk = mriutil.tck2trk(tckDetRoi, anatBrainResample , self.buildName(tckDetRoi, None, 'trk'))


        tckProb = self.__tckgenTensor(dwi, self.buildName(dwi, 'tensor_prob', 'tck'), mask, act, seed_gmwmi, bFile, 'Tensor_Prob')
        tckProbConnectome = self.__tck2connectome(tckProb, brodmann, self.buildName(tckProb, 'connectome', 'csv'))
        mriutil.plotConnectome(tckProbConnectome, self.buildName(tckProbConnectome, None, "png"))
        tckProbRoi = self.__tckedit(tckProb, mask253, self.buildName(tckProb, 'roi','tck'))
        tckProbRoiTrk = mriutil.tck2trk(tckProbRoi, anatBrainResample , self.buildName(tckProbRoi, None, 'trk'))

        #HARDI part
        fod =  self.getImage(self.hardimrtrixDir,'dwi','fod')
        hardiTck = self.__tckgenHardi(fod, self.buildName(fod, 'hardi_prob', 'tck'), act)
        hardiTckConnectome = self.__tck2connectome(hardiTck, brodmann, self.buildName(hardiTck, 'connectome', 'csv'))
        mriutil.plotConnectome(hardiTckConnectome, self.buildName(hardiTckConnectome, None, "png"))
        hardiTckRoi = self.__tckedit(hardiTck, mask253, self.buildName(hardiTck, 'roi','tck'))
        tckgenRoiTrk = mriutil.tck2trk(hardiTckRoi, anatBrainResample , self.buildName(hardiTckRoi, None, 'trk'))


        tcksift = self.__tcksift(hardiTck, fod)
        tcksiftConnectome = self.__tck2connectome(tcksift, brodmann, self.buildName(tcksift, 'connectome', 'csv'))
        mriutil.plotConnectome(tcksiftConnectome, self.buildName(tcksiftConnectome, None, "png"))                
        tcksiftRoi = self.__tckedit(tcksift, mask253, self.buildName(tcksift, 'roi', 'tck'))
        tcksiftRoiTrk = mriutil.tck2trk(tcksiftRoi, anatBrainResample , self.buildName(tcksiftRoi, None, 'trk'))

        #create PNG
        if self.config.getboolean('general', 'vtk_available'):
            mriutil.createVtkPng(tckDetRoiTrk, anatBrainResample, mask253)
            mriutil.createVtkPng(tckProbRoiTrk, anatBrainResample, mask253)
            mriutil.createVtkPng(tckgenRoiTrk, anatBrainResample, mask253)
            mriutil.createVtkPng(tcksiftRoiTrk, anatBrainResample, mask253)


    def __tckedit(self, source, include, target, downsample= "2"):

        self.info("Starting tckedit creation from mrtrix on {}".format(source))

        tmp = self.buildName(source, "tmp", "tck")        
        cmd = "tckedit {} {} -downsample {} -quiet ".format(source, tmp, downsample)

        if isinstance(include, basestring):
            cmd += " -include {}".format(include)
        else:
            for element in include:
                cmd += " -include {}".format(element)
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


    def __tckgenHardi(self, source, target, act = None, bFile = None, algorithm = "iFOD2"):
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
            target: the output file name
            bFile: specify the diffusion-weighted gradient scheme used in the acquisition.
            mask: specify a masking region of interest, as a binary mask image.
            act: use the Anatomically-Constrained Tractography framework during tracking
            algorithm: the tractography algorithm to use. default: iFOD2

        Returns:
            The resulting streamlines tractography filename generated
        """

        self.info("Starting tckgen creation from mrtrix on {}".format(source))
        tmp = self.buildName(source, "tmp", "tck")
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

        images = Images((self.getImage(self.workingDir, 'dwi', 'tensor_det', 'tck'), "deterministic tensor connectome matrix from a streamlines"),
                  (self.getImage(self.workingDir, 'dwi', ['tensor_det', 'connectome' ], 'csv'), "deterministic tensor connectome matrix from a streamlines csv"),
                  (self.getImage(self.workingDir, 'dwi', 'tensor_prob', 'tck'), "probabilistic tensor connectome matrix from a streamlines"),
                  (self.getImage(self.workingDir, 'dwi', ['tensor_prob','connectome'], 'csv'), "probabilistic tensor connectome matrix from a streamlines csv"),
                  (self.getImage(self.workingDir, 'dwi', 'hardi_prob', 'tck'), "tckgen hardi probabilistic streamlines tractography"),
                  (self.getImage(self.workingDir, 'dwi', 'tcksift', 'tck'), 'tcksift'),
                  (self.getImage(self.workingDir, 'dwi', ['tcksift', 'connectome'], 'csv'), 'connectome matrix from a tcksift csv'))

        print 'Dirty =', images
        return images.isSomeImagesMissing()


    def qaSupplier(self):


        tensorDetPng = self.getImage(self.workingDir, 'dwi', ['tensor_det', 'roi'], 'png')
        tensorDetPlot = self.getImage(self.workingDir, 'dwi', ['tensor_det', 'connectome'], 'png')
        tensorProbPng = self.getImage(self.workingDir, 'dwi', ['tensor_prob', 'roi'], 'png')
        tensorProbPlot = self.getImage(self.workingDir, 'dwi', ['tensor_prob', 'connectome'], 'png')
        hardiProbPng = self.getImage(self.workingDir, 'dwi', ['hardi_prob', 'roi'], 'png')
        hardiProbPlot = self.getImage(self.workingDir, 'dwi', ['hardi_prob', 'connectome'], 'png')
        tcksiftPng = self.getImage(self.workingDir, 'dwi', ['tcksift', 'roi'], 'png')
        tcksiftPlot = self.getImage(self.workingDir, 'dwi', ['tcksift', 'connectome'], 'png')

        images = Images((tensorDetPng, 'fiber crossing aparc_aseg area 253 from a deterministic tensor streamlines'),
                       (tensorDetPlot,'Connectome matrix from a deterministic tensor streamlines'),
                       (tensorProbPng, 'fiber crossing aparc_aseg area 253 from a probabilistic tensor streamlines'),
                       (tensorProbPlot,'Connectome matrix from a probabilistic tensor streamlines'),
                       (hardiProbPng, 'fiber crossing aparc_aseg area 253 from a probabilistic hardi streamlines'),
                       (hardiProbPlot, 'Connectome matrix from a probabilistic hardi streamlines'),
                       (tcksiftPng, 'fiber crossing aparc_aseg area 253 from a probabilistic tensor streamlines'),
                       (tcksiftPlot, 'tcksift'))
        print images
        return images
