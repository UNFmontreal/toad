# -*- coding: utf-8 -*-
from core.generictask import GenericTask
from lib import mriutil
from lib.images import Images
import numpy

__author__ = 'desmat'

class TractographyMrtrix(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'upsampling', 'hardimrtrix', 'masking', 'registration','qa')

    def implement(self):

        act = self.getImage(self.maskingDir, "aparc_aseg", ["register", "act"])
        #seed_gmwmi = self.getImage(self.maskingDir, "aparc_aseg", "5tt2gmwmi")
        seed_gmwmi = self.getImage(self.registrationDir, "tt5", "resample")
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
        tckDetConnectomeNormalize = self.__normalizeConnectome(tckDetConnectome, self.buildName(tckDetConnectome, 'normalize', 'csv'))
        mriutil.plotConnectome(tckDetConnectomeNormalize, self.buildName(tckDetConnectomeNormalize, None, "png"))

        tckDetRoi = self.__tckedit(tckDet, mask253, self.buildName(tckDet, 'roi','tck'))
        tckDetRoiTrk = mriutil.tck2trk(tckDetRoi, anatBrainResample , self.buildName(tckDetRoi, None, 'trk'))


        tckProb = self.__tckgenTensor(dwi, self.buildName(dwi, 'tensor_prob', 'tck'), mask, act, seed_gmwmi, bFile, 'Tensor_Prob')
        tckProbConnectome = self.__tck2connectome(tckProb, brodmann, self.buildName(tckProb, 'connectome', 'csv'))
        tckProbConnectomeNormalize = self.__normalizeConnectome(tckProbConnectome, self.buildName(tckProbConnectome, 'normalize', 'csv'))
        mriutil.plotConnectome(tckProbConnectomeNormalize, self.buildName(tckProbConnectomeNormalize, None, "png"))

        tckProbRoi = self.__tckedit(tckProb, mask253, self.buildName(tckProb, 'roi','tck'))
        tckProbRoiTrk = mriutil.tck2trk(tckProbRoi, anatBrainResample , self.buildName(tckProbRoi, None, 'trk'))

        #HARDI part
        csd =  self.getImage(self.hardimrtrixDir,'dwi','csd')
        hardiTck = self.__tckgenHardi(csd, self.buildName(csd, 'hardi_prob', 'tck'), act)
        hardiTckConnectome = self.__tck2connectome(hardiTck, brodmann, self.buildName(hardiTck, 'connectome', 'csv'))
        hardiTckConnectomeNormalize = self.__normalizeConnectome(hardiTckConnectome, self.buildName(hardiTckConnectome, 'normalize', 'csv'))
        mriutil.plotConnectome(hardiTckConnectomeNormalize, self.buildName(hardiTckConnectomeNormalize, None, "png"))

        hardiTckRoi = self.__tckedit(hardiTck, mask253, self.buildName(hardiTck, 'roi','tck'))
        tckgenRoiTrk = mriutil.tck2trk(hardiTckRoi, anatBrainResample , self.buildName(hardiTckRoi, None, 'trk'))


        tcksift = self.__tcksift(hardiTck, csd)
        tcksiftConnectome = self.__tck2connectome(tcksift, brodmann, self.buildName(tcksift, 'connectome', 'csv'))
        tcksiftConnectomeNormalize = self.__normalizeConnectome(tcksiftConnectome, self.buildName(tcksiftConnectome, 'normalize', 'csv'))

        mriutil.plotConnectome(tcksiftConnectomeNormalize, self.buildName(tcksiftConnectomeNormalize, None, "png"))
        tcksiftRoi = self.__tckedit(tcksift, mask253, self.buildName(tcksift, 'roi', 'tck'))
        tcksiftRoiTrk = mriutil.tck2trk(tcksiftRoi, anatBrainResample , self.buildName(tcksiftRoi, None, 'trk'))

        #create PNG
        if self.get('general', 'vtk_available'):
            mriutil.createVtkPng(tckDetRoiTrk, anatBrainResample, mask253)
            mriutil.createVtkPng(tckProbRoiTrk, anatBrainResample, mask253)
            mriutil.createVtkPng(tckgenRoiTrk, anatBrainResample, mask253)
            mriutil.createVtkPng(tcksiftRoiTrk, anatBrainResample, mask253)


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


    def __tcksift(self, source, csd):
        """ filter a whole-brain fibre-tracking data set such that the streamline densities match the FOD lobe integral.

        Args:
            source: the input track file.
            csd: input image containing the spherical harmonics of the fibre orientation distributions

        Returns:
            The resulting output filtered tracks file

        """
        tmp = self.buildName(source, "tmp", "tck")
        target = self.buildName(source, 'tcksift','.tck')
        self.info("Starting tcksift creation from mrtrix on {}".format(source))

        cmd = "tcksift {} {} {} -nthreads {} -quiet".format(source, csd, tmp, self.getNTreadsMrtrix())
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
        cmd = "tck2connectome {} {} {} -quiet -zero_diagonal -nthreads {}".format(source, nodes, tmp, self.getNTreadsMrtrix() )

        self.launchCommand(cmd)
        return self.rename(tmp, target)


    def __normalizeConnectome(self, source, target):
        """ generate a connectome matrix which each row is normalize

            if you sum each element of a given lines the result will equal 1.00

        Args:
            source: a input .csv file containing edge weights. see __tck2connectome
            target: the output .csv file containing normalize results

        Returns:
            The resulting .cvs file name

        """
        matrix = numpy.genfromtxt(source, delimiter=' ')
        matrix = numpy.add(matrix, numpy.matrix.transpose(matrix))

        with numpy.errstate(invalid='ignore'):
            for index, row in enumerate(matrix):
                    matrix[index] = numpy.divide(row, row.sum())

        matrix[numpy.isnan(matrix)] = 0.0
        numpy.savetxt(target, matrix, delimiter=' ', fmt='%0.4f')
        return target

    def isIgnore(self):
        if self.get("ignore"):
            return True

        elif self.get('hardimrtrix', 'ignore'):
            self.warning('This task depend on hardi mrtrix task that is set to ignore.')
            return True

        return False


    def meetRequirement(self):
        #@TODO add brain mask and 5tt as requierement
        images = Images((self.getImage(self.dependDir,'dwi','upsample'), 'upsampled diffusion weighted'),
                  (self.getImage(self.dependDir, 'grad', None, 'b'), '.b gradient encoding file'),
                  #(self.getImage(self.maskingDir, "aparc_aseg", ["register", "act"]), 'resampled anatomically constrained tractography'),
                  #(self.getImage(self.maskingDir, "aparc_aseg", "5tt2gmwmi"), 'seeding streamlines 5tt2gmwmi'),
                  (self.getImage(self.registrationDir, "brodmann", "resample"), 'resampled brodmann area'),
                  (self.getImage(self.maskingDir, 'aparc_aseg',['253','mask']), 'area 253 from aparc_aseg'),
                  (self.getImage(self.maskingDir, 'aparc_aseg',['1024','mask']), 'area 1024 from aparc_aseg'),
                  (self.getImage(self.registrationDir,'anat', ['brain', 'resample']), 'anatomical brain resampled'))
                  #(self.getImage(self.maskingDir, 'anat',['resample', 'extended','mask']), 'ultimate extended mask'))

        return images.isAllImagesExists()


    def isDirty(self, result = False):

        images = Images((self.getImage(self.workingDir, 'dwi', 'tensor_det', 'tck'), "deterministic tensor connectome matrix from a streamlines"),
                  (self.getImage(self.workingDir, 'dwi', ['tensor_det', 'connectome', 'normalize'], 'csv'), "normalize deterministic tensor connectome matrix from a streamlines csv"),
                  (self.getImage(self.workingDir, 'dwi', 'tensor_prob', 'tck'), "probabilistic tensor connectome matrix from a streamlines"),
                  (self.getImage(self.workingDir, 'dwi', ['tensor_prob', 'connectome', 'normalize'], 'csv'), "normalize probabilistic tensor connectome matrix from a streamlines csv"),
                  (self.getImage(self.workingDir, 'dwi', 'hardi_prob', 'tck'), "tckgen hardi probabilistic streamlines tractography"),
                  (self.getImage(self.workingDir, 'dwi', 'tcksift', 'tck'), 'tcksift'),
                  (self.getImage(self.workingDir, 'dwi', ['tcksift', 'connectome', 'normalize'], 'csv'), 'normalize connectome matrix from a tcksift csv'))

        return images.isSomeImagesMissing()


    def qaSupplier(self):


        tensorDetPng = self.getImage(self.workingDir, 'dwi', ['tensor_det', 'roi'], 'png')
        tensorDetPlot = self.getImage(self.workingDir, 'dwi', ['tensor_det', 'connectome', 'normalize'], 'png')
        tensorProbPng = self.getImage(self.workingDir, 'dwi', ['tensor_prob', 'roi'], 'png')
        tensorProbPlot = self.getImage(self.workingDir, 'dwi', ['tensor_prob', 'connectome', 'normalize'], 'png')
        hardiProbPng = self.getImage(self.workingDir, 'dwi', ['hardi_prob', 'roi'], 'png')
        hardiProbPlot = self.getImage(self.workingDir, 'dwi', ['hardi_prob', 'connectome', 'normalize'], 'png')
        tcksiftPng = self.getImage(self.workingDir, 'dwi', ['tcksift', 'roi'], 'png')
        tcksiftPlot = self.getImage(self.workingDir, 'dwi', ['tcksift', 'connectome', 'normalize'], 'png')

        images = Images((tensorDetPng, 'fiber crossing aparc_aseg area 253 from a deterministic tensor streamlines'),
                       (tensorDetPlot,'normalize connectome matrix from a deterministic tensor streamlines'),
                       (tensorProbPng, 'fiber crossing aparc_aseg area 253 from a probabilistic tensor streamlines'),
                       (tensorProbPlot,'normalize connectome matrix from a probabilistic tensor streamlines'),
                       (hardiProbPng, 'fiber crossing aparc_aseg area 253 from a probabilistic hardi streamlines'),
                       (hardiProbPlot, 'normalize connectome matrix from a probabilistic hardi streamlines'),
                       (tcksiftPng, 'fiber crossing aparc_aseg area 253 from a probabilistic tensor streamlines'),
                       (tcksiftPlot, 'tcksift'))
        return images
