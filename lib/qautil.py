# -*- coding: utf-8 -*-

#import os
#import shutil
#import mpl_toolkits.mplot3d
#import dipy.reconst.dti
#import dipy.data
#import dipy.viz.fvtk
#import dipy.viz.colormap
#import xml.dom.minidom as minidom
#from string import ascii_uppercase, digits
#from random import choice
#from nipy.labs.viz_tools import slicers
import dipy.segment.mask
import functools
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot
import nibabel
import numpy
import tempfile
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
        image3dMasked = numpy.ma.masked_where(fovData==0, image3dData)
    else:
        mins, maxs = (0, 0, 0), image3dData.shape
        image3dMasked = image3dData

    # Image to slice
    #@TODO: try to crop the image to show more slices
    #image3dCrop = dipy.segment.mask.crop(image3dMasked, mins, maxs)
    #imageToSlice = image3dCrop
    imageToSlice = image3dMasked

    # Number of slices in each dimension
    x = widthSize / imageToSlice.shape[1]
    y = widthSize / imageToSlice.shape[0]
    z = y
    numberOfSlices = (x, y, z)

    # Compute slices indices
    sliceIndices = []
    for dimShape, dimNbrOfSlices in zip(imageToSlice.shape, numberOfSlices):
        start = dimShape / dimNbrOfSlices
        stop = dimShape
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
        self.height = 6 # Figure height in inches, x100 px with default dpi
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
        return (self.height * ratio, self.height)


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
            self.fig.set_size_inches([_ / 2 for _ in self.figsize])
        else:
            self.fig.set_size_inches(self.figsize)
        self.__showColorbar()
        self.fig.savefig(target, facecolor='black')
        matplotlib.pyplot.close()


    def __showEdges(self, dim):
        matplotlib.pyplot.contour(
                numpy.rot90(self.edgesSlices[dim]), [0], colors='r')


    def __showSeg(self, dim):
        lutData = numpy.loadtxt(self.lutFile, usecols=(0,1,2,3))
        lutCmap = matplotlib.colors.ListedColormap(lutData[:,1:]/256)
        norm = matplotlib.colors.BoundaryNorm(lutData[:,0], lutCmap.N)
        segImshow = functools.partial(
                matplotlib.pyplot.imshow, alpha=0.6,
                norm=norm, cmap=lutCmap)
        segSlices = numpy.ma.masked_where(
                self.segSlices[dim] == 0, self.segSlices[dim])
        segImshow(numpy.rot90(segSlices))


    def __showGrid(self, dim):
        try:
            step = int(min(self.imageData.shape) / 5)
        except ValueError:
            step = 16
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
        if self.colorbar:
            self.fig.subplots_adjust(right=0.8)
            cbar_ax = self.fig.add_axes([0.85, 0.15, 0.05, 0.7])
            cbar = self.fig.colorbar(self.im, cax=cbar_ax)
            #cbar.outline.set_color('w')
            #cbar.ax.yaxis.set_tick_params(color='w')


class Plot4dVolume(object):

    def __init__(
            self, source, gifSpeed=30, vmax=None, fov=None):
        """Create a animated gif from a 4d NIfTI image
        Args:
            source: 4D NIfTI image
            target: outputfile gif name
            gifSpeed: delay between images (tens of ms), default=30
        """
        #self.source = source
        self.gifSpeed = gifSpeed
        print self.gifSpeed
        self.fov = fov
        #gifId = self.__idGenerator()
        self.imageData = nibabel.load(source).get_data()
        self.vmax = self.initVmax(vmax)


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
        frameList = self.__createFrames()
        cmd = 'convert -delay {} '.format(str(self.gifSpeed))
        for frame in frameList:
            cmd += '{} '.format(frame.name)
            frame.close
        cmd += target
        print "convert"
        util.launchCommand(cmd)
        for frame in frameList: frame.close


    def __createFrames(self):
        frameList = []
        for num in range(self.imageData.shape[-1]):
            frame = tempfile.NamedTemporaryFile(suffix='.jpg')#, delete=False)
            plot = Plot3dVolume(
                    self.imageData[:,:,:,num], vmax=self.vmax,
                    sourceIsData=True, fov=self.fov, grid=True)
            plot.save(frame.name, smallSize=True)
            frameList.append(frame)
        return frameList


