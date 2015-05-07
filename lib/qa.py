from lib import util, mriutil
from string import ascii_uppercase, digits
from random import choice
import os
import shutil
import functools
import numpy
import nibabel
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot
import mpl_toolkits.mplot3d
import scipy.ndimage.morphology
import dipy.segment.mask


class Qa(object):

    def slicerPng(self, source, target, maskOverlay=None, segOverlay=None, vmax=None, boundaries=None, grid=False, isData=False):
        """Utility method to slice a 3d image
        Args:
            source : background image
            target : output in png format
            optionalOverlay : optional overlay: put the edges of the image on top of the background
            vmax : to fix the colorbar max, if None slicerPng take the max of the background
        """
        if isData:
            imageData = source
        else:
            image = nibabel.load(source)
            imageData = image.get_data()

        if vmax == None:
            vmax=numpy.max(imageData)
    
        width, fig_dims = self.__configFigure(imageData)
        fig = matplotlib.pyplot.figure(figsize=fig_dims)
    
        slices = self.__image3d2slices(imageData, width, boundaries=boundaries)
        imageImshow = functools.partial(matplotlib.pyplot.imshow, \
                                        vmin=0, \
                                        vmax=vmax, \
                                        cmap=matplotlib.pyplot.cm.gray)
    
        if maskOverlay != None:
            mask = nibabel.load(maskOverlay)
            maskData = mask.get_data()
            maskSlices = self.__image3d2slices(maskData, width, boundaries=boundaries)

        if segOverlay != None:
            seg = nibabel.load(segOverlay)
            segData = seg.get_data()
            segSlices = self.__image3d2slices(segData, width, boundaries=boundaries)
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
    
        matplotlib.pyplot.subplots_adjust(left=0, right=1, bottom=0, top=1, hspace=0.001)
        fig.savefig(target, facecolor='black')
        matplotlib.pyplot.close()
        matplotlib.rcdefaults()


    def slicerGif(self, source, target, gifSpeed=30, vmax=None, boundaries=None):
        """Create a animated gif from a 4d NIfTI
        Args:
            source: 4D NIfTI image
            target: outputfile gif name
            gifSpeed: delay between images (tens of ms), default=30
        """
        gifId = self.__idGenerator()
    
        image = nibabel.load(source)
        imageData = image.get_data()
    
        imageList = []
        for num in range(imageData.shape[-1]):
            output = gifId + '{0:04}.png'.format(num)
            self.slicerPng(imageData[:,:,:,num], output, vmax=vmax, isData=True, boundaries=boundaries, grid=True)
            imageList.append(output)
        
        self.__imageList2Gif(imageList, target, gifSpeed)
        #Cleaning temp files
        cmd = 'rm {}*.png'.format(gifId)
        self.launchCommand(cmd)
    
        return target
             


    def slicerGifCompare(self, source1, source2, target, gifSpeed=100, vmax=100, boundaries=None):
        """Create a animated gif from a 4d NIfTI
        Args:
            source: 4D NIfTI image
            target: outputfile gif name
            gifSpeed: delay between images (tens of ms), default=30
        """
        gifId = self.__idGenerator()

        image1 = nibabel.load(source1)
        imageData1 = image1.get_data()

        image2 = nibabel.load(source2)
        imageData2 = image2.get_data()

        imageList = []
        for num, image in enumerate([imageData1, imageData2]):
            output = gifId + '{0:04}.png'.format(num)
            self.slicerPng(image[:,:,:,2], output, vmax=vmax, isData=True, boundaries=boundaries)
            imageList.append(output)

        self.__imageList2Gif(imageList, target, gifSpeed)
        #Cleaning temp files
        cmd = 'rm {}*.png'.format(gifId)
        self.launchCommand(cmd)

        return target



    def plotMovement(self, parametersFile, targetTranslations, targetRotations):
        """
        """
        parameters = numpy.loadtxt(parametersFile)
        Vsize = len(parameters)
        vols = range(0,Vsize-1)
        translations = parameters[1:Vsize,0:3]
        rotations = parameters[1:Vsize,3:6]
        rotations = rotations / numpy.pi * 180
    
        plotdata = [(translations,'translation (mm)',targetTranslations),
                    (rotations,'rotation (degree)',targetRotations)
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
    
        matplotlib.pyplot.close()
        matplotlib.rcdefaults()


    def plotvectors(self, bvecsFile, bvecsCorrected, target):
        """
        """
        gifId = self.__idGenerator()
        fig = matplotlib.pyplot.figure(figsize=(4,4))
        ax = mpl_toolkits.mplot3d.Axes3D(fig)
        matplotlib.pyplot.subplots_adjust(left=0, right=1, bottom=0, top=1, hspace=0.001)
    
        bvecs = numpy.loadtxt(bvecsFile)
        bvecsOpp= -bvecs
    
        graphParam = [(80, 'b', 'o', bvecsOpp), (80, 'r', 'o', bvecs)]
        
        if bvecsCorrected:
            bvecsCorr = numpy.loadtxt(bvecsCorrected)
            graphParam.append((20, 'k', '+', bvecsCorr))

        for s, c, m, bvec in graphParam:
            x = bvec[0,1:]
            y = bvec[1,1:]
            z = bvec[2,1:]
            ax.scatter(x, y, z, s=s, c=c, marker=m)
    
        lim = .7
        ax.set_xlim([-lim,lim])
        ax.set_ylim([-lim,lim])
        ax.set_zlim([-lim,lim])
        ax.set_axis_off()
    
        imageList = []
        for num in range(0,360,3):
            output = gifId + '{0:04}.png'.format(num)
            ax.view_init(elev=10., azim=num)
            matplotlib.pyplot.savefig(output)
            imageList.append(output)
    
        matplotlib.pyplot.close()
        matplotlib.rcdefaults()
    
        self.__imageList2Gif(imageList, target, 10)
    
        #Cleaning temp files
        cmd = 'rm {}*.png'.format(gifId)
        self.launchCommand(cmd)
    
        return target


    def noiseAnalysis(self, source, maskNoise, maskCc, targetSnr, targetHist):
        """
        """
        dwiImage = nibabel.load(source)
        maskNoiseImage = nibabel.load(maskNoise)
        maskCcImage = nibabel.load(maskCc)

        dwiData = dwiImage.get_data()
        maskNoiseData = maskNoiseImage.get_data()
        maskCcData = maskCcImage.get_data()

        volumeNumber = dwiData.shape[3]

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
        noiseHistData = numpy.reshape(noiseHistData, numpy.prod(noiseHistData.shape))
        num_bins = 40
        #xlim = numpy.percentile(noiseHistData, 98)
        matplotlib.pyplot.hist(noiseHistData, num_bins, histtype='stepfilled', facecolor='g', range=[0, 150])
        matplotlib.pyplot.xlabel('Intensity')
        matplotlib.pyplot.ylabel('Voxels number')
        matplotlib.pyplot.savefig(targetHist)
        matplotlib.pyplot.close()
        matplotlib.rcdefaults()
    
    
    def writeTable(self, imageLink, legend):
        """
        return html table with one column
        """
        tags = {'imageLink':imageLink, 'legend':legend}
        return self.parseTemplate(tags, os.path.join(self.toadDir, "templates/files/qa.table.tpl"))
        
        
    def createQaReport(self, images):
        """create html report for a task with qaSupplier implemented
        Args:
           images : an Images object
        """
        mainTemplate = os.path.join(self.qaDir, 'qa.main.tpl')
        tableTemplate = os.path.join(self.toadDir, 'templates', 'files', 'qa.table.tpl')
        taskInfo = images.getInformation()
        imagesDir = os.path.join(self.qaDir, self.config.get('qa', 'images_dir'))
        tablesCode = ''
        
        print "createQaReport images =", images
        for imageLink, legend in images:
            #@TODO Take into account multiple run of QA
            if imageLink:
                path, filename =  os.path.split(imageLink)
                shutil.copyfile(imageLink, os.path.join(imagesDir, filename))
                tags = {'imageLink':os.path.join(self.config.get('qa', 'images_dir'), filename),'legend':legend}
                tablesCode += self.parseTemplate(tags, tableTemplate)
            else:
                tags = {'imageLink':'', 'legend':legend}
                tablesCode += self.parseTemplate(tags, tableTemplate)

        tags = {'taskInfo':taskInfo,'parseHtmlTables':tablesCode}
        htmlCode = self.parseTemplate(tags, mainTemplate)

        htmlFile = os.path.join(self.qaDir,'{}.html'.format(self.getName()))
        util.createScript(htmlFile, htmlCode)


    def __configFigure(self, imageData, nbrOfSlices=7, dpi=72.27):
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




    def __image3d2slices(self, image3dData, maxWidth, boundaries=None):
        """Slice a 3d image along the 3 axis given a maximum Width
        Args:
            image3dData: 3d image
            maxWidth: maximum width of the result
        Return:
            tuple a lenght 3 with slices along the 3 axis (x, y, z)
        """
        
        xSlicesNumber = maxWidth / image3dData.shape[1]
        ySlicesNumber = maxWidth / image3dData.shape[0]
        zSlicesNumber = ySlicesNumber
        slicesNumbers = (xSlicesNumber, ySlicesNumber, zSlicesNumber)
        
        mins, maxs = (0, 0, 0), image3dData.shape
        
        if boundaries != None:
            boundariesImage = nibabel.load(boundaries)
            boundariesData = boundariesImage.get_data()
            mins, maxs = dipy.segment.mask.bounding_box(boundariesData)
        
        slicesIndices3d = []
        for minimum, maximum, slicesNumber in zip(mins, maxs, slicesNumbers):
            dimSize = maximum - minimum
            start = minimum + (dimSize / slicesNumber)
            stop = maximum
            slicesIndices = numpy.linspace(start, stop, slicesNumber, endpoint=False)
            slicesIndices = slicesIndices.astype('uint8')
            slicesIndices3d.append(slicesIndices)
        
        '''param = [(ximage3dDataSliced),
                    (yimage3dDataSliced),
                    (zimage3dDataSliced),
                   ]
        for image3dDataSliced in param:
            #So just to recap: to invert the effect of rollaxis(x,n), use rollaxis(x,0,n+1)
            image3dDataSliced = image3dData[slicesIndices3d[0], :, :]
            xNewShape = (image3dData.shape[1] * xSlicesNumber, image3dData.shape[2])
            ximage3dDataSliced = numpy.reshape(ximage3dDataSliced, xNewShape)'''

        ximage3dDataSliced = image3dData[slicesIndices3d[0], :, :]
        xNewShape = (image3dData.shape[1] * xSlicesNumber, image3dData.shape[2])
        ximage3dDataSliced = numpy.reshape(ximage3dDataSliced, xNewShape)
    
        yimage3dDataSliced = image3dData[:, slicesIndices3d[1], :]
        yimage3dDataSliced = numpy.rollaxis(yimage3dDataSliced, 1)
        yNewShape = (image3dData.shape[0] * ySlicesNumber, image3dData.shape[2])
        yimage3dDataSliced = numpy.reshape(yimage3dDataSliced, yNewShape)
    
        zimage3dDataSliced = image3dData[:, :, slicesIndices3d[2]]
        zimage3dDataSliced = numpy.rollaxis(zimage3dDataSliced, 2)
        zNewShape = (image3dData.shape[0] * zSlicesNumber, image3dData.shape[1])
        zimage3dDataSliced = numpy.reshape(zimage3dDataSliced, zNewShape)
        
        return (ximage3dDataSliced, yimage3dDataSliced, zimage3dDataSliced)



    def __idGenerator(self, size=8, chars=ascii_uppercase + digits):
        """Generate random strings
        Args:
            size: length of 8 uppercase and digits. default: 8 characters
            #@Christophe comment
            chars: ascii_uppercase + digits
        Returns:
            a string of lenght (size) that contain random number
        """
        return ''.join(choice(chars) for _ in range(size))



    def __imageList2Gif(self, imageList, target, gifSpeed):
        """Generate animated gif with convert from imagemagick
        Args:
            imageList: list of png to convert
            target: output filename
            gifSpeed: delay between images (tens of ms)
        """
        cmd = 'convert -delay {} '.format(str(gifSpeed))
        for image in imageList:
            cmd += '{} '.format(image)
        cmd += target
        self.launchCommand(cmd)

