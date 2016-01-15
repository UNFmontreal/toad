# -*- coding: utf-8 -*-

import functools
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot
import mpl_toolkits.mplot3d
import nibabel
import numpy
import tempfile
import dipy.data
import dipy.reconst.dti
import dipy.segment.mask
import dipy.viz.colormap
import dipy.viz.fvtk
from lib import util

__author__ = "Christophe Bedetti"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Christophe Bedetti"]


#~~~~~~~~~~~~~~~~~~#
# HELPER functions #
#~~~~~~~~~~~~~~~~~~#

def imageSlicer(image3dData, minNbrSlices, fov=None):
    """Slice a 3D image
    Args:
        image3dData: 3d image as numpy array
        minNbrSlices: minimum number of slices for one dimension
        fov: field of view link image
            Algorithm assume data>0 to be inside the fov
            default=None
    Return:
        tuple of lenght 3 with slices along the 3 axis (x, y, z)
    """
    # Computing image width size knowing minimum number of slices
    widthSize = max(image3dData.shape) * minNbrSlices

    # Determine mins and maxs of the image boundaries
    if fov != None:
        fovData = nibabel.load(fov).get_data()
        mins, maxs = dipy.segment.mask.bounding_box(fovData)
        #image3dMasked = numpy.ma.masked_where(fovData==0, image3dData)
    else:
        mins, maxs = (0, 0, 0), image3dData.shape
        #image3dMasked = image3dData

    # Image to slice
    #@TODO: try to crop the image to show more slices ?
    #image3dCrop = dipy.segment.mask.crop(image3dMasked, mins, maxs)
    #imageToSlice = image3dCrop
    #@TODO: try to mask the image to show more slices ?
    #imageToSlice = image3dMasked
    imageToSlice = image3dData

    # Number of slices in each dimension
    x = widthSize / imageToSlice.shape[1]
    y = widthSize / imageToSlice.shape[0]
    z = widthSize / imageToSlice.shape[0]
    numberOfSlices = (x, y, z)

    # Compute slices indices
    sliceIndices = []
    for minimum, maximum, dimNbrOfSlices in zip(mins, maxs, numberOfSlices):
        rangeSize = maximum - minimum
        start = minimum + rangeSize / dimNbrOfSlices
        stop = maximum
        indices = numpy.linspace(start, stop, dimNbrOfSlices, endpoint=False)
        sliceIndices.append(indices.astype('uint8'))

    # Extract x slices
    xSlices = imageToSlice[sliceIndices[0], :, :]
    xNewShape = (imageToSlice.shape[1] * x, imageToSlice.shape[2])
    xSlices = numpy.reshape(xSlices, xNewShape)

    # Extract y slices
    ySlices = imageToSlice[:, sliceIndices[1], :]
    ySlices = numpy.rollaxis(ySlices, 1)
    yNewShape = (imageToSlice.shape[0] * y, imageToSlice.shape[2])
    ySlices = numpy.reshape(ySlices, yNewShape)

    # Extract z slices
    zSlices = imageToSlice[:, :, sliceIndices[2]]
    zSlices = numpy.rollaxis(zSlices, 2)
    zNewShape = (imageToSlice.shape[0] * z, imageToSlice.shape[1])
    zSlices = numpy.reshape(zSlices, zNewShape)

    return (xSlices, ySlices, zSlices)


def frames2Gif(frames, target, gifSpeed):
    cmd = 'convert -delay {} '.format(str(gifSpeed))
    for frame in frames:
        cmd += '{} '.format(frame.name)
    cmd += target
    util.launchCommand(cmd)


#~~~~~~~~~#
# Classes #
#~~~~~~~~~#

class Plot3dVolume(object):

    def __init__(
            self, source, fov=None, textData=None,
            grid=False, colorbar=False, sourceIsData=False, vmax=None):
        """Slice and plot a 3D image
        Args:
            source : nifti file for the background
            fov: nifti file to know where to slice the image
                Algorithm assume to be inside the fov when data>0
                default=None
            textData : text data to display in the image
                default=None
            grid : add a grid to the image (True or False)
                default=False
            vmax : Define the maximum value for vizualisation
                default=None
            colorbar : add a colorbar to the image
                default=False
            sourceIsData : indicate that the source link is a numpy array
                instead of a link (True or False)
                default=False
        """
        self.width = 14 # Figure height in inches, x100 px with default dpi
        self.minNbrSlices = 7
        self.source = source
        self.fov = fov
        self.textData = textData
        self.grid = grid
        self.colorbar = colorbar
        self.sourceIsData = sourceIsData
        self.imageData = self.initImageData()
        self.vmax = self.initVmax(vmax)
        self.slices = imageSlicer(
                self.imageData, self.minNbrSlices, fov=self.fov)
        self.figsize = self.initFigsize()
        self.imshow = self.initImshow()
        self.edgesSlices = None
        self.segSlices = None
        self.lutFile = None
        self.fig = None
        self.ax = None


    def initImageData(self):
        if self.sourceIsData:
            return self.source
        else:
            return nibabel.load(self.source).get_data()


    def initVmax(self, vmax):
        """
        Initialized vmax
        """
        #@TODO: better result with self.slices ?
        if vmax == None:
            return numpy.percentile(self.imageData, 99)
        else:
            return vmax


    def initFigsize(self):
        """
        Check the size of each slices and compute the right height and width
        of the figure
        Return: tuple with width and a height of the figure in inches
        """
        xShape = self.slices[0].shape
        yShape = self.slices[1].shape
        zShape = self.slices[2].shape
        maxWidthPx = numpy.max([xShape[0], yShape[0], zShape[0]])
        totalHeightPx = xShape[1] + yShape[1] + zShape[1]
        ratio = maxWidthPx / float(totalHeightPx)
        return (self.width, self.width / ratio)


    def initImshow(self):
        """
        Initialized imshow matplotlib function for the background
        """
        return functools.partial(
                matplotlib.pyplot.imshow,
                vmin=0,
                vmax=self.vmax,
                cmap=matplotlib.pyplot.cm.gray)


    def setEdges(self, edges):
        """
        Set edges information (self.edgesSlices)
        Arg:
            edges : a nifti file
        """
        edgesData = nibabel.load(edges).get_data()
        self.edgesSlices = imageSlicer(
                edgesData, self.minNbrSlices, fov=self.fov)


    def setSegOverlay(self, segOverlay, lutFile):
        segData = nibabel.load(segOverlay).get_data()
        self.segSlices = imageSlicer(segData, self.minNbrSlices, fov=self.fov)
        self.lutFile = lutFile


    def showSlices(self):
        self.fig = matplotlib.pyplot.figure()
        for dim in range(3):
            self.ax = matplotlib.pyplot.subplot(3, 1, dim+1)
            self.im = self.imshow(numpy.rot90(self.slices[dim]))
            if self.edgesSlices != None: self.__showEdges(dim)
            if self.segSlices != None: self.__showSeg(dim)
            if self.grid:
                self.__showGrid(dim)
            else:
                self.ax.set_axis_off()
        if self.textData != None: self.__showText()


    def save(self, target, smallSize=False):
        """
            target : link of the output image
        """
        self.showSlices()
        matplotlib.pyplot.subplots_adjust(
                left=0, right=1, bottom=0, top=1, hspace=0.001)
        if smallSize:
            self.fig.set_size_inches([_ / 1.5 for _ in self.figsize])
        else:
            self.fig.set_size_inches(self.figsize)
        if self.colorbar: self.__showColorbar()
        self.fig.savefig(target, facecolor='black')
        matplotlib.pyplot.close()


    def __showEdges(self, dim):
        matplotlib.pyplot.contour(
                numpy.rot90(self.edgesSlices[dim]), [0], colors='r')


    def __showSeg(self, dim):
        lutDataOrigin = numpy.loadtxt(self.lutFile, usecols=(0,1,2,3))
        lutData = numpy.zeros((
            lutDataOrigin[-1,0].astype(numpy.int)+1,
            lutDataOrigin.shape[1]))
        lutData[:,0] = range(0,lutDataOrigin[-1,0].astype(numpy.int)+1,1)
        lutData[lutDataOrigin[:,0].astype(numpy.int),1:] = lutDataOrigin[:,1:]
        lutCmap = matplotlib.colors.ListedColormap(lutData[:,1:]/256)
        norm = matplotlib.colors.BoundaryNorm(lutData[:,0], lutCmap.N)
        segImshow = functools.partial(
                matplotlib.pyplot.imshow, alpha=0.6,
                norm=norm, cmap=lutCmap)
        segSlices = numpy.ma.masked_where(
                self.segSlices[dim] == 0, self.segSlices[dim])
        segImshow(numpy.rot90(segSlices))


    def __showGrid(self, dim):
        step = numpy.floor(max(self.imageData.shape) / 5)
        xAxisTicks = numpy.arange(step, self.slices[dim].shape[0], step)
        yAxisTicks = numpy.arange(step, self.slices[dim].shape[1], step)
        self.ax.xaxis.set_ticks(xAxisTicks)
        self.ax.yaxis.set_ticks(yAxisTicks)
        self.ax.grid(True, color='0.75', linestyle='-', linewidth=1)
        self.ax.set_axisbelow(True)


    def __showText(self):
        self.fig.text(
                0, 0, self.textData,
                verticalalignment='bottom', horizontalalignment='left',
                color='red', fontsize=15)


    def __showColorbar(self):
        #give space for the colorbar
        self.fig.subplots_adjust(right=0.9)
        #description: add_axes([left, bottom, width, height])
        cbar_ax = self.fig.add_axes([0.91, 0.15, 0.01, 0.7])
        cbar = self.fig.colorbar(self.im, cax=cbar_ax)
        #set colorbar to white
        for t in cbar_ax.get_yticklabels():
            t.set_color("w")


class Plot4dVolume(object):

    def __init__(
            self, source, source2=None, gifSpeed=30, vmax=None, fov=None):
        """Create a animated gif from a 4d NIfTI image
        Args:
            source: 4D NIfTI image
            target: outputfile gif name
            gifSpeed: delay between images (tens of ms), default=30
        """
        self.gifSpeed = gifSpeed
        self.fov = fov
        self.imageData = nibabel.load(source).get_data()
        self.vmax = self.initVmax(vmax)
        self.compareVolumes = False
        if source2 != None:
            self.gifSpeed = 100
            self.imageData2 = nibabel.load(source2).get_data()
            self.compareVolumes = True
            # Check if imageData has an odd number of slices
            if not self.imageData.shape[2] % 2 == 0:
                self.imageData = self.imageData[:,:,:-1]


    def initVmax(self, vmax):
        """
        Initialized vmax
        """
        if vmax == None:
            return numpy.percentile(self.imageData, 99)
        else:
            return vmax


    def save(self, target):
        """Generate animated gif with convert from imagemagick
        Args:
            imageList: list of png to convert
            target: output filename
            gifSpeed: delay between images (tens of ms)
        """
        if self.compareVolumes:
            frameList = self.__createCompareFrames()
        else:
            frameList = self.__createFrames()
        frames2Gif(frameList, target, self.gifSpeed)
        for frame in frameList: frame.close


    def __createFrames(self):
        frameList = []
        for num in range(self.imageData.shape[-1]):
            frame = tempfile.NamedTemporaryFile(suffix='.jpg')
            plot = Plot3dVolume(
                    self.imageData[:,:,:,num], vmax=self.vmax,
                    sourceIsData=True, fov=self.fov, grid=True)
            plot.save(frame.name, smallSize=True)
            frameList.append(frame)
        return frameList


    def __createCompareFrames(self):
        frameList = []
        for imageData, textData in (
                [self.imageData, 'before'], [self.imageData2, 'after']):
            frame = tempfile.NamedTemporaryFile(suffix='.jpg')
            volume = imageData[:,:,:,2]
            plot = Plot3dVolume(
                    volume, vmax=self.vmax,
                    sourceIsData=True, fov=self.fov, textData=textData)
            plot.save(frame.name, smallSize=True)
            frameList.append(frame)
        return frameList


def plotMovement(parametersFile, targetTranslations, targetRotations):
    """
    """
    parameters = numpy.loadtxt(parametersFile)
    Vsize = len(parameters)
    vols = range(0,Vsize-1)
    translations = parameters[1:Vsize,0:3]
    rotations = parameters[1:Vsize,3:6]
    rotations = rotations / numpy.pi * 180

    plotdata = [
            (translations,'translation (mm)',targetTranslations),
            (rotations,'rotation (degree)',targetRotations)]

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
    matplotlib.pyplot.close()


def plotVectors(bvecsFile, bvecsCorrected, target):
    """
    """
    fig = matplotlib.pyplot.figure(figsize=(4,4))
    ax = mpl_toolkits.mplot3d.Axes3D(fig)
    matplotlib.pyplot.subplots_adjust(
            left=0, right=1, bottom=0, top=1, hspace=0.001)

    bvecs = numpy.loadtxt(bvecsFile)
    bvecsOpp= -bvecs

    graphParam = [(80, 'b', 'o', bvecsOpp), (80, 'r', 'o', bvecs)]

    if bvecsCorrected:
        bvecsCorr = numpy.loadtxt(bvecsCorrected)
        graphParam.append((20, 'k', '+', bvecsCorr))

    for s, c, marker, bvec in graphParam:
        x = bvec[0,1:]
        y = bvec[1,1:]
        z = bvec[2,1:]
        ax.scatter(x, y, z, s=s, c=c, marker=marker)

    lim = .7
    ax.set_xlim([-lim,lim])
    ax.set_ylim([-lim,lim])
    ax.set_zlim([-lim,lim])
    ax.set_axis_off()

    frameList = []
    for num in range(0,360,3):
        frame = tempfile.NamedTemporaryFile(suffix='.jpg')
        ax.view_init(elev=10., azim=num)
        matplotlib.pyplot.savefig(frame.name)
        frameList.append(frame)

    #matplotlib.pyplot.close()
    #matplotlib.rcdefaults()

    frames2Gif(frameList, target, 10)
    for frame in frameList: frame.close


def plotSigma(sigma, target):
    """
    """
    matplotlib.pyplot.clf()
    y_pos = numpy.arange(len(sigma))
    sigmaMedian = numpy.median(sigma)
    matplotlib.pyplot.barh(y_pos, sigma)
    matplotlib.pyplot.xlabel('Sigma, median = {0}'.format(sigmaMedian))
    matplotlib.pyplot.ylabel('z-axis')
    matplotlib.pyplot.title('Sigma data for each z slice')
    matplotlib.pyplot.savefig(target)
    matplotlib.pyplot.close()
    matplotlib.rcdefaults()


def noiseAnalysis(source, maskNoise, maskCc, targetSnr, targetHist):
    """
    """
    dwiImage = nibabel.load(source)
    maskNoiseImage = nibabel.load(maskNoise)
    maskCcImage = nibabel.load(maskCc)

    dwiData = dwiImage.get_data()
    maskNoiseData = maskNoiseImage.get_data()
    maskCcData = maskCcImage.get_data()

    volumeNumber = dwiData.shape[3]

    if dwiData.shape[2] != maskNoiseData.shape[2]:
        zSliceShape = dwiData.shape[:2] + (1,)
        zMaskNoise = numpy.zeros(zSliceShape, dtype=maskNoiseData.dtype)
        zCc = numpy.zeros(zSliceShape, dtype=maskCcData.dtype)
        maskNoiseData = numpy.concatenate((maskNoiseData, zMaskNoise), axis=2)
        maskCcData = numpy.concatenate((maskCcData, zCc), axis=2)

    #Corpus Callossum masking
    dwiDataMaskCc = numpy.empty(dwiData.shape)
    maskCcData4d = numpy.tile(maskCcData,(volumeNumber,1,1,1))
    maskCcData4d = numpy.rollaxis(maskCcData4d, 0, start=4)
    dwiDataMaskCc = numpy.ma.masked_where(maskCcData4d == 0, dwiData)

    #Noise masking
    dwiDataMaskNoise = numpy.empty(dwiData.shape)
    maskNoise4d = numpy.tile(maskNoiseData,(volumeNumber,1,1,1))
    maskNoise4d = numpy.rollaxis(maskNoise4d, 0, start=4)
    dwiDataMaskNoise = numpy.ma.masked_where(maskNoise4d == 0, dwiData)

    #SNR
    volumeSize = numpy.prod(dwiData.shape[:3])
    mean_signal = numpy.reshape(dwiDataMaskCc, [volumeSize, volumeNumber])
    mean_signal = numpy.mean(mean_signal, axis=0)
    noise_std = numpy.reshape(dwiDataMaskNoise, [volumeSize, volumeNumber])
    noise_std = numpy.std(noise_std, axis=0)

    SNR = mean_signal / noise_std
    matplotlib.pyplot.plot(SNR)
    matplotlib.pyplot.xlabel('Volumes')
    matplotlib.pyplot.ylabel('SNR')
    matplotlib.pyplot.savefig(targetSnr)
    matplotlib.pyplot.close()
    matplotlib.rcdefaults()

    #Hist plot
    noiseHistData = dwiDataMaskNoise[:,:,:,1:]
    noiseHistData = numpy.reshape(
            noiseHistData, numpy.prod(noiseHistData.shape))
    num_bins = 40
    #xlim = numpy.percentile(noiseHistData, 98)
    matplotlib.pyplot.hist(
            noiseHistData, num_bins,
            histtype='stepfilled', facecolor='g', range=[0, 150])
    matplotlib.pyplot.xlabel('Intensity')
    matplotlib.pyplot.ylabel('Voxels number')
    matplotlib.pyplot.savefig(targetHist)
    matplotlib.pyplot.close()
    matplotlib.rcdefaults()


def plotReconstruction(data, mask, cc, target, model):
    """
    """
    #Showbox
    maskImage = nibabel.load(mask)
    maskData = maskImage.get_data()
    ccImage = nibabel.load(cc)
    ccData = ccImage.get_data()

    brainBox = dipy.segment.mask.bounding_box(maskData)
    brainBox = numpy.array(brainBox)
    ccBox = dipy.segment.mask.bounding_box(ccData)
    ccBox = numpy.array(ccBox)

    brainCenter = numpy.floor(numpy.mean(brainBox, 0))
    ccCenter = numpy.floor(numpy.mean(ccBox, 0))

    shift = numpy.subtract(brainBox[1], brainBox[0]) / 6

    xmin = ccCenter[0] - shift[0]
    xmax = ccCenter[0] + shift[0]
    ymin = ccCenter[1]
    ymax = ccCenter[1] + 1
    zmin = ccCenter[2] - shift[0]
    zmax = ccCenter[2] + shift[0]

    #Visualization
    sphere = dipy.data.get_sphere('symmetric724')
    ren = dipy.viz.fvtk.ren()

    if model == 'tensor':
        fa = dipy.reconst.dti.fractional_anisotropy(data.evals)
        rgbData = dipy.reconst.dti.color_fa(fa, data.evecs)
        evals = data.evals[xmin:xmax, ymin:ymax, zmin:zmax]
        evecs = data.evecs[xmin:xmax, ymin:ymax, zmin:zmax]
        cfa = rgbData[xmin:xmax, ymin:ymax, zmin:zmax]
        cfa /= cfa.max()
        cfa *= 2
        dipy.viz.fvtk.add(ren, dipy.viz.fvtk.tensor(evals, evecs, cfa, sphere))
    elif model == 'hardi_odf':
        data_small = data['dwiData'][xmin:xmax, ymin:ymax, zmin:zmax]
        csdodfs = data['csdModel'].fit(data_small).odf(sphere)
        csdodfs = numpy.clip(csdodfs, 0, numpy.max(csdodfs, -1)[..., None])
        dipy.viz.fvtk.add(ren,dipy.viz.fvtk.sphere_funcs(
            csdodfs, sphere, scale=1.3, colormap='RdYlBu', norm=False))
    elif model == 'hardi_peak':
        peak_dirs = data.peak_dirs[xmin:xmax, ymin:ymax, zmin:zmax]
        peak_values = data.peak_values[xmin:xmax, ymin:ymax, zmin:zmax]
        fodf_peaks = dipy.viz.fvtk.peaks(peak_dirs, peak_values, scale=1.3)
        dipy.viz.fvtk.add(ren, fodf_peaks)

    dipy.viz.fvtk.camera(
            ren, pos=(0,1,0), focal=(0,0,0), viewup=(0,0,1), verbose=False)
    dipy.viz.fvtk.record(ren, n_frames=1, out_path=target, size=(1200, 1200))
    dipy.viz.fvtk.clear(ren)


def plotTrk(source, target, anatomical, roi):
    roiImage= nibabel.load(roi)
    anatomicalImage = nibabel.load(anatomical)

    sourceImage = [s[0] for s in nibabel.trackvis.read(source, points_space='voxel')[0]]
    try:
        sourceActor = dipy.viz.fvtk.streamtube(
                sourceImage, dipy.viz.colormap.line_colors(sourceImage))
        roiActor = dipy.viz.fvtk.contour(
                roiImage.get_data(), levels=[1],
                colors=[(1., 1., 0.)], opacities=[1.])
        anatomicalActor = dipy.viz.fvtk.slicer(
            anatomicalImage.get_data(), voxsz=(1.0, 1.0, 1.0),
            plane_i=None, plane_j=None, plane_k=[65], outline=False)
    except ValueError:
        return False

    sourceActor.RotateX(-70)
    sourceActor.RotateY(2.5)
    sourceActor.RotateZ(185)

    roiActor.RotateX(-70)
    roiActor.RotateY(2.5)
    roiActor.RotateZ(185)

    anatomicalActor.RotateX(-70)
    anatomicalActor.RotateY(2.5)
    anatomicalActor.RotateZ(185)

    ren = dipy.viz.fvtk.ren()
    dipy.viz.fvtk.add(ren, sourceActor)
    dipy.viz.fvtk.add(ren, roiActor)
    dipy.viz.fvtk.add(ren, anatomicalActor)
    dipy.viz.fvtk.camera(
            ren, pos=(0,0,1), focal=(0,0,0), viewup=(0,1,0), verbose=False)
    dipy.viz.fvtk.record(ren, out_path=target, size=(1200, 1200), n_frames=1)
