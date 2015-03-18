import glob
import os

import numpy
import matplotlib
import mpl_toolkits

from core.generictask import GenericTask
from lib.images import Images
from lib import util, mriutil

matplotlib.use('Agg')


__author__ = 'desmat'


class Eddy(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preparation')


    def implement(self):

        dwi = self.getImage(self.dependDir, 'dwi')
        b0AP= self.getImage(self.dependDir, 'b0AP')
        b0PA= self.getImage(self.dependDir, 'b0PA')
        bEnc=  self.getImage(self.dependDir, 'grad',  None, 'b')
        bVals=  self.getImage(self.dependDir, 'grad',  None, 'bvals')
        bVecs=  self.getImage(self.dependDir, 'grad',  None, 'bvecs')

        #extract b0 image from the dwi
        b0 = os.path.join(self.workingDir, os.path.basename(dwi).replace(self.config.get("prefix", 'dwi'), self.config.get("prefix", 'b0')))
        self.info(mriutil.extractFirstB0FromDwi(dwi, b0, bVals))

        #make sure all the images have the same voxel size and dimension scale between them
        self.__validateSizeAndDimension([dwi, b0, b0AP, b0PA])

        #Generate a missing b0 image if we could. --> 0 = P>>A, 1 = A>>P
        if self.get("phase_enc_dir") == "0" and b0PA and b0AP is False:
            b0AP = b0

        if self.get("phase_enc_dir") == "1" and b0AP and b0PA is False :
            b0PA = b0

        [dwi, b0, b0AP, b0PA] = self.__oddImagesWithEvenNumberOfSlices([dwi, b0, b0AP, b0PA])

        if b0AP is False or b0PA is False:
            topupBaseName = None
            mask = self.__bet(b0)

        else:

            #concatenate B0 image together

            if self.get("phase_enc_dir") == "0":
                b0Image = self.__concatenateB0(b0PA, b0AP,
                                os.path.join(self.workingDir, self.get('b0s_filename')))

            elif self.get("phase_enc_dir") == "1":
                 b0Image = self.__concatenateB0(b0AP, b0PA,
                                os.path.join(self.workingDir, self.get('b0s_filename')))

            #create the acquisition parameter file
            acqpTopup = self.__createAcquisitionParameterFile('topup')

            #Lauch topup on concatenate B0 image
            [topupBaseName, topupImage] = self.__topup(b0Image, acqpTopup, self.get('b02b0_filename'))
            meanTopup = self.__fslmathsTmean(os.path.join(self.workingDir, topupImage))
            mask = self.__bet(meanTopup)


        #create the acquisition parameter file for eddy
        acqpEddy = self.__createAcquisitionParameterFile('eddy')

        #create an index file
        indexFile = self.__createIndexFile(mriutil.getNbDirectionsFromDWI(dwi))

        outputEddyImage = self.__correctionEddy2(dwi,
                                    mask, topupBaseName, indexFile, acqpEddy, bVecs, bVals)

        #@TODO remove the glob and use getimage
        eddyParameterFiles = glob.glob("{}/*.eddy_parameters".format(self.workingDir))
        if len(eddyParameterFiles)>0:
            self.info("Apply eddy movement correction to gradient encodings directions")
            bCorrected = mriutil.applyGradientCorrection(bEnc, eddyParameterFiles.pop(0), self.buildName(outputEddyImage, None, 'b'))
            self.info(mriutil.mrtrixToFslEncoding(outputEddyImage,
                                        bCorrected,
                                        self.buildName(outputEddyImage, None, 'bvecs'),
                                        self.buildName(outputEddyImage, None, 'bvals')))


    def __oddImagesWithEvenNumberOfSlices(self, sources):
        """return a list of images that will count a odd number of slices in z direction

            If an even number of slices is found, the upper volume will be remove

        Args:
            sources: a list of images

        Returns:
             the same list but with images modified

        """
        for i, source in enumerate(sources):
            if source:
                zDims = int(mriutil.getMriDimensions(source)[2])
                if zDims%2 == 1:
                    sources[i]= self.__extractZSlices(source, "0:{}".format(zDims-2))
        return sources


    def __extractZSlices(self, source, slices):
        """Extract slices along the Z axes from an image

        Args:
            source: The input image
            slices:  A list of slices, starting at 0

        Returns:
             The name of the resulting image
        """
        tmp =  self.buildName(source, "tmp")
        target = self.buildName(source, "subset")
        cmd = "mrconvert {} {} -coord +2 {} -nthreads {} -quiet".format(source, tmp, slices, self.getNTreadsMrtrix())
        self.launchCommand(cmd)
        return self.rename(tmp, target)


    def __concatenateB0(self, source1, source2, target):
        """Concatenate two images along the axis 3

        Args:
            source1: The first image
            source2:  The second image
            target: The name of the resulting image

        Returns:
             The name of the resulting image
        """
        cmd = "mrcat {} {} {} -axis 3 -nthreads {} -quiet".format(source1, source2, target, self.getNTreadsMrtrix())
        self.launchCommand(cmd)
        return target


    def __createAcquisitionParameterFile(self, type):
        """Create the acquire parameter (--acqp) file for topup or eddy

        For topup, the image will concatenate b0AP first then b0PA
            #A>>P, 0 -1 0
            #P>>A, 0 1 0
            #R>>L, 1 0 0
            #L>>R, -1 0 0
        Args:
            type: algorithm this file is create for. Valid value are: topup, eddy

        Returns:
            the acquisition parameter file name

        """
        try:
            phaseEncDir = int(self.get('phase_enc_dir'))
        except ValueError:
            self.error("Cannot determine the phase encoding direction")

        try:
            echoSpacing = float(self.get('echo_spacing'))
            epiFactor = int(self.get('epi_factor'))
            factor = (epiFactor-1) * (echoSpacing/1000)

        except ValueError:
            self.warning("Cannot find suitable Echo Spacing value, will use a factor of 0.1")
            factor = "0.1"

        if type=='topup':
            parameter='acqp_topup'
            text = "0 1 0 {}\n0 -1 0 {}\n".format(factor, factor)

        elif type=='eddy':
            parameter='acqp_eddy'
            text = "0 1 0 {}\n".format(factor)

        else:
            self.error("Type must be of value: topup or eddy")
            return False

        target = os.path.join(self.workingDir, self.get(parameter))
        if not util.createScript(target, text):
            self.error("Unable to create script {}".format(target))

        return target


    def __createIndexFile(self, dimensions):
        """Create the file that will contain the index

        Args:
            dimensions: the number of direction into the B0 images

        Returns:
            The resulting file name
        """
        target = os.path.join(self.workingDir, self.get( 'index_filename'))
        self.info("Creating index file {}".format(target))
        text = ""
        for i in range(0,dimensions):
            text+="1 "

        util.createScript(target, text)
        return target


    def __validateSizeAndDimension(self, sources):

        names = []
        dims = []
        sizes = []

        for source in sources:
            if source:
                names.append(source)
                dimensions = mriutil.getMriDimensions(source)
                if len(dimensions) == 4:
                    dims.append([dimensions[0], dimensions[1], dimensions[2]])
                else:
                    dims.append(dimensions)
                    sizes.append(mriutil.getMriVoxelSize(source))

        if not dims[1:] == dims[:-1]:
            self.error("Dimension for each scale mismatch found between images: {}".format(", ".join(names)))

        if not sizes[1:] == sizes[:-1]:
            self.error("Voxel size mismatch found between images: {}".format(", ".join(names)))


    def __topup(self, source, acqp, b02b0File):

        self.info("Launch topup from fsl.\n")
        baseName = os.path.join(self.workingDir, self.get('topup_results_base_name'))
        output = os.path.join(self.workingDir, self.get('topup_results_output'))

        cmd = "topup --imain={} --datain={} --config={} --out={}  --iout={}"\
              .format(source, acqp, b02b0File, baseName, output)
        self.launchCommand(cmd)
        return [baseName, output]


    def __fslmathsTmean(self, source):

        target = source.replace(".nii", "_tmean.nii")
        self.info(mriutil.fslmaths(source, target, 'Tmean'))
        return target


    def __bet(self, source):

        self.info("Launch brain extraction from fsl")
        tmp = self.buildName(source, "tmp")
        target = self.buildName(source, "brain")

        cmd = "bet {} {} -m".format(source, tmp)
        self.launchCommand(cmd)
        self.rename(tmp, target)

        self.info("Finish brain extraction from fsl")
        return target


    def __correctionEddy2(self, source, mask, topup, index, acqp, bVecs, bVals):
        """Performs eddy correction on a dwi file.

        Args:
            source:	File containing all the images to estimate distortions for
            mask:	Mask to indicate brain
            topup:  Base name for output files from topup
            index:	File containing indices for all volumes in --imain into --acqp and --topup
            acqp:	File containing acquisition parameters
            bvecs:	File containing the b-vectors for all volumes in --imain
            bvals:	File containing the b-values for all volumes in --imain

        Returns:
            The resulting file name

        """
        self.info("Launch eddy correction from fsl")
        tmp = self.buildName(source, "tmp")
        target = self.buildName(source, "eddy")
        cmd = "eddy --imain={} --mask={} --index={} --acqp={} --bvecs={} --bvals={} --out={} "\
              .format(source, mask, index, acqp, bVecs, bVals, tmp)

        if topup is not None:
            cmd += " --topup={}".format(topup)

        self.getNTreadsEddy()
        self.launchCommand(cmd, None, None, 5*60*60)
        return self.rename(tmp, target)



    def __plotMvt(self, eddypm, translationOutput, rotationOutput):
        """

        """
        parameters = numpy.loadtxt(eddypm)

        Vsize = len(parameters)
        vols = range(0,Vsize-1)

        translations = parameters[1:Vsize,0:3]

        rotations = parameters[1:Vsize,3:6]
        rotations = rotations / numpy.pi * 180

        plotdata = [
            (translations,'translation (mm)',translationOutput),
            (rotations,'rotation (degree)',rotationOutput)
            ]

        for data, ylabel, pngoutput in plotdata:
            matplotlib.pyplot.clf()
            px, = matplotlib.pyplot.plot(vols, data[:,0])
            py, = matplotlib.pyplot.plot(vols, data[:,1])
            pz, = matplotlib.pyplot.plot(vols, data[:,2])
            matplotlib.pyplot.xlabel('DWI volumes')
            matplotlib.pyplot.xlim([0,Vsize+10])
            matplotlib.pyplot.ylabel(ylabel)
            matplotlib.pyplot.legend([px, py, pz], ['x', 'y', 'z'])
            matplotlib.pyplot.savefig(pngoutput)


    def __plotVectors(self, rawBvecs, eddyBvecs, target):
        """

        """
        gifId = self.idGenerator()
        fig = matplotlib.pyplot.figure()
        ax = mpl_toolkits.mplot3d.Axes3D(fig)

        bVec1 = numpy.loadtxt(rawBvecs)
        bVec0= -bVec1

        graphParam = [(80, 'b', 'o', bVec0), (80, 'r', 'o', bVec1)]

        if eddyBvecs:
            bVecs2 = numpy.loadtxt(eddyBvecs)
            graphParam.append((20, 'k', '+', bVecs2))

        for s, c, m, bv in graphParam:
            x = bv[0,1:]
            y = bv[1,1:]
            z = bv[2,1:]
            ax.scatter(x, y, z, s=s, c=c, marker=m)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_xlim([-1,1])
        ax.set_ylim([-1,1])
        ax.set_zlim([-1,1])
        matplotlib.pyplot.axis('off')

        cmd = 'convert '
        for ii in xrange(0,360,2):
            ax.view_init(elev=10., azim=ii)
            matplotlib.pyplot.savefig(gifId+str(ii)+'.png')
            cmd += '-delay 10 ' + gifId + str(ii) + '.png '
        cmd += target
        self.launchCommand(cmd)
        cmd = 'rm ' + gifId + '*'
        self.launchCommand(cmd)


    def isIgnore(self):
        return self.get("ignore").lower() in "true"


    def meetRequirement(self):

        images = Images((self.getImage(self.dependDir, 'dwi'), 'diffusion weighted'),
                  (self.getImage(self.dependDir, 'grad', None, 'bvals'), 'gradient .bvals encoding file'),
                  (self.getImage(self.dependDir, 'grad', None, 'bvecs'), 'gradient .bvecs encoding file'),
                  (self.getImage(self.dependDir, 'grad', None, 'b'), 'gradient .b encoding file'))
        return images.isAllImagesExists()


    def isDirty(self):
        images = Images((self.getImage(self.workingDir, 'dwi', 'eddy'), 'diffusion weighted eddy corrected'),
                  (self.getImage(self.workingDir, 'grad', 'eddy', 'bvals'), 'gradient .bvals encoding file'),
                  (self.getImage(self.workingDir, 'grad', 'eddy', 'bvecs'), 'gradient .bvecs encoding file'),
                  (self.getImage(self.workingDir, 'grad', 'eddy', 'b'), 'gradient .b encoding file'))
        return images.isSomeImagesMissing()


    """
    def qaSupplier(self):
        eddy = self.getImage(self.workingDir, "dwi", 'eddy')
        eddyGif = self.nifti4dtoGif(eddy)
        import glob
        fixs = glob.glob("{}/*_temporary.nii*.eddy_parameters".format(self.workingDir))
        for fix in fixs:
            eddy_parameters = fix 
        translation_tg = 'translation.png'
        rotation_tg = 'rotation.png'
        self.__plotMvt(eddy_parameters, translation_tg, rotation_tg)
        
        rawBvec = self.getImage(self.dependDir, 'grad', None, 'bvec')
        eddyBvec = self.getImage(self.workingDir, 'grad', 'eddy', 'bvec')
        bvecs_tg = 'bvecs.gif'
        self.__plotVectors(rawBvec, eddyBvec, bvecs_tg)
        
        images = [(eddyGif,'DWI eddy'),
                  (translation_tg,'Translation correction by eddy'),
                  (rotation_tg,'Rotation correction by eddy'),
                  (bvecs_tg,'Gradients vectors on the unitary sphere. Red : raw bvec | Blue : opposite bvec | Black + : movement corrected bvec')]
        return images
    """
