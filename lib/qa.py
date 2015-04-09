from lib import util, mriutil
from string import ascii_uppercase, digits
from random import choice
import functools
import numpy
import nibabel
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot
import mpl_toolkits.mplot3d


class Qa(object):

    def slicerPng(self, backgroundImage, optionalOverlay=None, target=None, vmax=None, isBackgroundArray=False):
        """Utility method to slice a 3d image
        Args:
            backgroundImage : background image
            optionalOverlay : optional overlay: put the edges of the image on top of the background
            target : output in png format
            vmax : to fixe the colorbar max, if None clicerPng take the max of the background
            loadBackgroundImage : 
        """
        #if (target is None) and (optionalOverlay is None):
        #    target = self.buildName(backgroundImage, None, 'png')
        #elif (target is None) and (optionalOverlay is not None):
        #    target = self.buildName(optionalOverlay, None, 'png')
    
        if isBackgroundArray:
            imageData = backgroundImage
        else:
            image = nibabel.load(backgroundImage)
            imageData = image.get_data()

    
        if vmax == None:
            vmax=numpy.max(imageData)
    
        width, fig_dims = __configFigure(imageData)
        fig = matplotlib.pyplot.figure(figsize=fig_dims)
    
        slices = __image3d2slices(imageData, width)
        imageImshow = functools.partial(matplotlib.pyplot.imshow, \
                                        vmin=0, \
                                        vmax=vmax, \
                                        cmap=matplotlib.pyplot.cm.gray)
    
        if optionalOverlay != None:
            overlay = nibabel.load(optionalOverlay)
            overlayData = overlay.get_data()
            overlaySlices = __image3d2slices(overlayData, width)
            overlayImshow = functools.partial(matplotlib.pyplot.contour, \
                                              [0], \
                                              colors='r')
    
        #show_slices
        for dim in range(3):
            ax = matplotlib.pyplot.subplot(3, 1, dim+1)
            imageImshow(numpy.rot90(slices[dim]))
            if optionalOverlay != None:
                matplotlib.pyplot.contour(numpy.rot90(overlaySlices[dim]), [0], colors='r')
            ax.set_axis_off()
    
        matplotlib.pyplot.subplots_adjust(left=0, right=1, bottom=0, top=1, hspace=0.001)
        fig.savefig(target, facecolor='black')
        matplotlib.pyplot.close()
        matplotlib.rcdefaults()
    
        return target


    def c3dSegmentation(self, backgroundImage, segmentationImage, scale, opacity, target=None):
        """Utility method to use c3d from ITKSnap package
        
        if target is None, the output filename will be base on the segmentation image name
        
        Args:
            backgroundImage : background image
            segmentationImage : segmentation image
            scale the background image
            opacity of the segmentation between 0 and 1
            target : output filename in png format
        """
        if target is None:
            target = self.buildName(segmentationImage, '', 'png')
        
        lutImage = os.path.join(self.toadDir, "templates/lookup_tables/",'FreeSurferColorLUT_ItkSnap.txt')
        for axes in ['x', 'y', 'z']:
            tmp = self.buildName(axes,'', 'png')
            cmd = 'c3d {} -scale {} {} -foreach -flip z -slice {} 50% -endfor -oli {} {} -type uchar -omc {}'\
                .format(backgroundImage, scale, segmentationImage, axes, lutImage, opacity, tmp)
            self.launchCommand(cmd)
        
        cmd = 'pngappend x.png + y.png + z.png {}'.format(target)
        self.launchCommand(cmd)
        
        cmd = 'rm x.png y.png z.png'
        self.launchCommand(cmd)
        return target



    def slicerGif(self, source, target=None, gifSpeed=30):
        """Create a animated gif from a 4d NIfTI
        if target is None, the output filename will be base on source name
        Args:
            source: 4D NIfTI image
            target: outputfile gif name
            gifSpeed: delay between images (tens of ms), default=30
        """
        if target is None:
            target = self.buildName(source, '', 'gif')
    
        gifId = __idGenerator()
    
        # Spliting 4D image
        image = nibabel.load(source)
        imageData = image.get_data()
        imageAffine = image.get_affine()
        vmax = numpy.max(imageData[:,:,:,1:]) * .8
    
        imageList = []
        for num in range(imageData.shape[-1]):
            output = gifId + '{0:04}.png'.format(num)
            slicerPng(imageData[:,:,:,num], target=output, vmax=vmax, isBackgroundArray=True)
            imageList.append(output)
        
        __imageList2Gif(imageList, target, gifSpeed)
        #Cleaning temp files
        cmd = 'rm {}*.png'.format(gifId)
        self.launchCommand(cmd)
    
        return target
             


    def plotMovement(self, parametersFile, target):
        """
        """
        parameters = numpy.loadtxt(parametersFile)
        Vsize = len(parameters)
        vols = range(0,Vsize-1)
        translations = parameters[1:Vsize,0:3]
        rotations = parameters[1:Vsize,3:6]
        rotations = rotations / numpy.pi * 180
    
        plotdata = [(translations,'translation (mm)','qa/translations.png'),
                    (rotations,'rotation (degree)','qa/rotations.png')
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


    def plotvectors(self, bvecsFile, target):
        """
        """
        gifId = __idGenerator()
        fig = matplotlib.pyplot.figure(figsize=(4,4))
        ax = mpl_toolkits.mplot3d.Axes3D(fig)
        matplotlib.pyplot.subplots_adjust(left=0, right=1, bottom=0, top=1, hspace=0.001)
    
        bvecs = numpy.loadtxt(bvecsFile)
        bvecsOpp= -bvecs
    
        graphParam = [(80, 'b', 'o', bvecsOpp), (80, 'r', 'o', bvecs)]
    
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
    
        __imageList2Gif(imageList, target, 10)
    
        #Cleaning temp files
        cmd = 'rm {}*.png'.format(gifId)
        self.launchCommand(cmd)
    
        return target
    


    def noise(self, source, tensors):
        """
        """
        dwi = nibabel.load(source)
        mask = nibabel.load('Diffusion_mask.nii.gz')
        tensorfit = nibabel.load('tensorsDipy.nii.gz')
    
        dwiData = dwi.get_data()
        maskData = mask.get_data()
        tensorfit = tensorfit.get_data()
    
        #from dipy.segment.mask import median_otsu
        #b0_mask, mask = median_otsu(dwiData)
    
        import dipy.core.gradients
        import dipy.reconst.dti
        bValsFile = 'Diffusion.bvals'
        bVecsFile = 'Diffusion.bvecs'
        gradientTable = dipy.core.gradients.gradient_table(numpy.loadtxt(bValsFile), numpy.loadtxt(bVecsFile))
        model = dipy.reconst.dti.TensorModel(gradientTable)
        fit = model.fit(dwiData, mask=maskData)
    
        from dipy.segment.mask import segment_from_cfa
        from dipy.segment.mask import bounding_box
    
    
        CC_box = numpy.zeros_like(dwiData[..., 0])
        mins, maxs = bounding_box(maskData)
        mins = numpy.array(mins)
        maxs = numpy.array(maxs)
        diff = (maxs - mins) // 4
        bounds_min = mins + diff
        bounds_max = maxs - diff
        CC_box[bounds_min[0]:bounds_max[0],
               bounds_min[1]:bounds_max[1],
               bounds_min[2]:bounds_max[2]] = 1
        threshold = (0.6, 1, 0, 0.1, 0, 0.1)
        #mask_cc_part, cfa = segment_from_cfa(fit, CC_box, threshold, return_cfa=True)
        mask_cc_part = segment_from_cfa(fit, CC_box, threshold)
        #cfa_img = nib.Nifti1Image((cfa*255).astype(np.uint8), affine)
        #mask_cc_part_img = nib.Nifti1Image(mask_cc_part.astype(np.uint8), affine)
        #nib.save(mask_cc_part_img, 'mask_CC_part.nii.gz')
    
        slicerPng(dwiData[:,:,:,0], optionalOverlay=mask_cc_part, target='qa/maskcc.png', isBackgroundArray=True)
    
        mean_signal = numpy.mean(dwiData[mask_cc_part], axis=0)
    
        from scipy.ndimage.morphology import binary_dilation
        mask_noise = binary_dilation(maskData, iterations=10)
        mask_noise[..., :mask_noise.shape[-1]//2] = 1
        mask_noise = ~mask_noise
        #mask_noise_img = nib.Nifti1Image(mask_noise.astype(np.uint8), affine)
        #nibabel.save(mask_noise_img, 'mask_noise.nii.gz')
        slicerPng(mask_noise, target='qa/masknoise.png', isBackgroundArray=True)
        noise_std = numpy.std(dwiData[mask_noise], axis=0)
    
        print mean_signal, noise_std
        SNR = mean_signal / noise_std
        print SNR
    
        matplotlib.pyplot.plot(SNR)
        matplotlib.pyplot.xlabel('Volumes')
        matplotlib.pyplot.ylabel('SNR')
        matplotlib.pyplot.title('SNR in CC for each volumes')
        matplotlib.pyplot.savefig('qa/snr.png')
        matplotlib.pyplot.close()
    
        #histogramme
        tempMask = numpy.tile(mask_noise,(33,1,1,1))
        tempMask = numpy.rollaxis(tempMask, 0, start=4)
        print tempMask.shape
        noiseHist = numpy.ma.masked_where(tempMask == 0, dwiData)
        noiseHist = noiseHist[:,:,:,1:]
        slicerPng(noiseHist[:,:,:,3], target='qa/noiseHist.png', isBackgroundArray=True)
        size = numpy.prod(noiseHist.shape)
        reshapeNoise = numpy.reshape(noiseHist, size)
        num_bins = 20
        matplotlib.pyplot.hist(reshapeNoise, num_bins, histtype='stepfilled', facecolor='g')
        #matplotlib.pyplot.plot(bins)
        matplotlib.pyplot.xlabel('Intensity')
        matplotlib.pyplot.ylabel('Voxels number')
        matplotlib.pyplot.title('Noise histogram, 10x10x10 box, all diffusion weighted volumes')
        matplotlib.pyplot.savefig('qa/hist.png')
    
        matplotlib.pyplot.close()
    
    
    def writeTable(self, imageLink, legend):
        """
        return html table with one column
        """
        tags = {'imageLink':imageLink, 'legend':legend}
        return self.parseTemplate(tags, os.path.join(self.toadDir, "templates/files/qa.table.tpl"))
        
        
    def createQaReport(self, structure):
        """create html report for a task with qaSupplier implemented
        
        Args:
            imagesArray : array of tupple [(imageLink, legend), ...]
        """
        
        imagesDir = os.path.join(self.qaDir, 'img')
        tablesCode = ''
        for imageLink, legend in structure.getData():
            #@TODO Take into account multiple run of QA
            shutil.copyfile(imageLink, os.path.join(imagesDir, imageLink))
            tags = {'imageLink':imageLink,'legend':legend}
            tablesCode += self.parseTemplate(tags, os.path.join(self.toadDir, 'templates/files/qa.table.tpl'))
        
        htmlCode = self.parseTemplate({'parseHtmlTables':tablesCode}, os.path.join(self.toadDir, 'templates/files/qa.main.tpl'))
        
        htmlFile = os.path.join(self.qaDir,'{}.html'.format(self.getName()))
        util.createScript(htmlFile, htmlCode)


    def __configFigure(self, imageData, nbrOfSlices=7, dpi=72.27):
        """
        """
        fig_width_px  = max(imageData.shape) * nbrOfSlices
        fig_height_px = max(imageData.shape) * 3
    
        fig_width_in  = fig_width_px  / dpi  # figure width in inches
        fig_height_in = fig_height_px / dpi  # figure height in inches
        fig_dims      = [fig_width_in, fig_height_in] # fig dims as a list
    
        #Figure parameters
        matplotlib.rcParams['figure.figsize'] = fig_dims
        matplotlib.rcParams['figure.dpi'] = dpi
    
        #savefig parameter
        matplotlib.rcParams['savefig.dpi'] = dpi
    
        return fig_width_px, fig_dims



    def __image3d2slices(self, image3dData, maxWidth):
        """Slice a 3d image along the 3 axis given a maximum Width
        Args:
            image3dData: 3d image
            maxWidth: maximum width of the result
        Return:
            tuple a lenght 3 with slices along the 3 axis (x, y, z)
        """
        # 
        xSlicesNumber = maxWidth / image3dData.shape[1]
        ySlicesNumber = maxWidth / image3dData.shape[0]
        zSlicesNumber = ySlicesNumber
        slicesNumbers = (xSlicesNumber, ySlicesNumber, zSlicesNumber)
    
        slicesIndices3d = []
        for dimSize, slicesNumber in zip(image3dData.shape, slicesNumbers):
            start = dimSize / slicesNumber
            stop = dimSize
            slicesIndices = numpy.linspace(start, stop, slicesNumber, endpoint=False)
            slicesIndices = slicesIndices.astype('uint8')
            slicesIndices3d.append(slicesIndices)
    
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
        #So just to recap: to invert the effect of rollaxis(x,n), use rollaxis(x,0,n+1)
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

