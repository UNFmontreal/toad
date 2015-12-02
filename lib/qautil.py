# -*- coding: utf-8 -*-

import functools
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot
import nibabel
import numpy
import tempfile

__author__ = "Christophe Bedetti"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Christophe Bedetti"]


def configFigure(imageData, nbrOfSlices=7, dpi=72.27):
     """
     """
     width = max(imageData.shape) * nbrOfSlices

     fig_width_px  = 2000
     try:
         fig_height_px = int(2000 * 3 / nbrOfSlices)#max(imageData.shape) * 3
     except ValueError:
         fig_height_px = 857

     fig_width_in  = fig_width_px  / dpi  # figure width in inches
     fig_height_in = fig_height_px / dpi  # figure height in inches
     fig_dims      = [fig_width_in, fig_height_in] # fig dims as a list

     #Figure parameters
     matplotlib.rcParams['figure.figsize'] = fig_dims
     matplotlib.rcParams['figure.dpi'] = dpi

     #savefig parameter
     matplotlib.rcParams['savefig.dpi'] = dpi

     return width, fig_dims


def image3d2slices(self, image3dData, outputWidth, boundaries=None):
    """Slice a 3d image along the 3 axis given a maximum Width
    Args:
        image3dData: 3d image
        outputWidth: maximum width of the output
        boundaries: 
    Return:
        tuple a lenght 3 with slices along the 3 axis (x, y, z)
    """
    # Determine mins and maxs of the image boundaries
    if boundaries != None:
        boundariesData = self.__loadImage(boundaries)
        mins, maxs = dipy.segment.mask.bounding_box(boundariesData)
        image3dData = numpy.ma.masked_where(boundariesData==0, image3dData)
    else:
        mins, maxs = (0, 0, 0), image3dData.shape
    crop = dipy.segment.mask.crop(image3dData, mins, maxs)

    # Number of slices in each dimension
    x = outputWidth / crop.shape[1]
    y = outputWidth / crop.shape[0]
    z = y
    slicesNumbers = (x, y, z)

    # Compute slices indices
    sliceIndex = []
    for dimSize, slicesNumber in zip(crop.shape ,slicesNumbers):
        start = dimSize / slicesNumber
        stop = dimSize
        index = numpy.linspace(start, stop, slicesNumber, endpoint=False)
        index = index.astype('uint8')
        sliceIndex.append(index)
    # Extract x slices
    xSlices = crop[sliceIndex[0], :, :]
    xNewShape = (crop.shape[1] * x, crop.shape[2])
    xSlices = numpy.reshape(xSlices, xNewShape)

    # Extract y slices
    ySlices = crop[:, sliceIndex[1], :]
    ySlices = numpy.rollaxis(ySlices, 1)
    yNewShape = (crop.shape[0] * y, crop.shape[2])
    ySlices = numpy.reshape(ySlices, yNewShape)

    # Extract z slices
    zSlices = crop[:, :, sliceIndex[2]]
    zSlices = numpy.rollaxis(zSlices, 2)
    zNewShape = (crop.shape[0] * z, crop.shape[1])
    zSlices = numpy.reshape(zSlices, zNewShape)

    return (xSlices, ySlices, zSlices)


def slicer3d(source, target, fov=None, maskEdges=None, segOverlay=None, textData=None, grid=False, vmax=None, sourceIsData=False):
    """Utility method to slice a 3d image
    Args:
        source : background image
        target :
        fov :
        maskEdges : put the edges of the image on top of the background
        segOverlay :
        textData :
        grid :
        vmax : to fix the colorbar max, if None slicerPng take the max of the background
        sourceIsData :
    Output:
        png image
    """

    # 
    if sourceIsData:
        imageData = source
    else:
        imageData = nibabel.load(source).get_data()

    if vmax == None:
        vmax=numpy.percentile(imageData, 99)

    width, fig_dims = self.__configFigure(imageData)
    fig = matplotlib.pyplot.figure(figsize=fig_dims)

    slices = image3d2slices(imageData, fov=fov)
    imageImshow = functools.partial(matplotlib.pyplot.imshow,
                                    vmin=0,
                                    vmax=vmax,
                                    cmap=matplotlib.pyplot.cm.gray)

    if maskEdges != None:
        maskData = nibabel.load(maskEdges).get_data()
        maskSlices = image3d2slices(maskData, fov=fov)

    if segOverlay != None:
        segSata = nibabel.load(segOverlay).get_data()
        segSlices = image3d2slices(segData, fov=fov)
        segSlices = [numpy.ma.masked_where(segSlices[dim] == 0, segSlices[dim]) for dim in range(3)]
        lutFiles = os.path.join(self.toadDir, 'templates', 'lookup_tables', self.config.get('template', 'freesurfer_lut'))
        lutData = numpy.loadtxt(lutFiles, usecols=(0,1,2,3))
        lutCmap = matplotlib.colors.ListedColormap(lutData[:,1:]/256)
        norm = matplotlib.colors.BoundaryNorm(lutData[:,0], lutCmap.N)
        segImshow = functools.partial(matplotlib.pyplot.imshow, \
                                      alpha=0.6, \
                                      norm=norm, \
                                      cmap=lutCmap)
      #show_slices
    for dim in range(3):
        ax = matplotlib.pyplot.subplot(3, 1, dim+1)
        imageImshow(numpy.rot90(slices[dim]))
        if maskOverlay != None:
            matplotlib.pyplot.contour(numpy.rot90(maskSlices[dim]), [0], colors='r')
        if segOverlay != None:
            segImshow(numpy.rot90(segSlices[dim]))
        if grid:
            try:
                step = int(min(imageData.shape) / 5)
            except ValueError:
                step = 16
            ax.xaxis.set_ticks(numpy.arange(step,slices[dim].shape[0],step))
            ax.yaxis.set_ticks(numpy.arange(step,slices[dim].shape[1],step))
            ax.grid(True, color='0.75', linestyle='-', linewidth=1)
            ax.set_axisbelow(True)
        else:
            ax.set_axis_off()

    if textData != None:
        fig.text(0, 0, textData, verticalalignment='bottom', horizontalalignment='left', color='red', fontsize=width/30)

    matplotlib.pyplot.subplots_adjust(left=0, right=1, bottom=0, top=1, hspace=0.001)
    fig.savefig(target, facecolor='black')
    matplotlib.pyplot.close()
    matplotlib.rcdefaults()

    return target


