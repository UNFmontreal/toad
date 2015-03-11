from string import ascii_uppercase, digits
from random import choice
from lib import mriutil
import os

from string import ascii_uppercase, digits
from random import choice
import numpy as np
import nibabel as nib
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os


class Qa(object):

#    def __init__(self):
#        pass

    def idGenerator(self, size=6, chars=ascii_uppercase + digits):
        """Generate random strings

        Args:
            size: length of 6 uppercase and digits. default: 6 characters
            #@Christophe comment
            chars: ascii_uppercase + digits

        Returns:
            a string of lenght (size) that contain random number
        """
        return ''.join(choice(chars) for _ in range(size))


    def pngSlicerImage(self, backgroundImage, optionalOverlay=None, target=None):
        """
        Utility method to use slicer from FSL package

        Args:
            backgroundImage : background image
            optionalOverlay : optional overlay: put the edges of the image on top of the background
            target : output in png format
        """
        if (target is None) and (optionalOverlay is None):
            target = self.buildName(backgroundImage, None, 'png')
        elif (target is None) and (optionalOverlay is not None):
            target = self.buildName(optionalOverlay, None, 'png')

        cmd = 'slicer {} '.format(backgroundImage)
        if optionalOverlay is not None:
            cmd += "{} ".format(optionalOverlay)
        cmd += "-a {}".format(target)
        self.launchCommand(cmd)
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
            cmd = 'c3d {}  -scale  {} {} -foreach -flip z -slice {} 50% -endfor -oli {} {} -type uchar -omc {}'\
                .format(backgroundImage, scale, segmentationImage, axes, lutImage, opacity, tmp)
            self.launchCommand(cmd)

        cmd = 'pngappend x.png + y.png + z.png {}'.format(target)
        self.launchCommand(cmd)

        cmd = 'rm x.png y.png z.png'
        self.launchCommand(cmd)
        return target


    def nifti4dtoGif(self, source, target=None, gifSpeed=30):
        """ Create a animated gif from a 4d NIfTI

        if target is None, the output filename will be base on source name

        Args:
            source: 4D NIfTI image
            target : outputfile gif name
            gifSpeed    : delay between images (tens of ms), default=30

        """
        if target is None:
            target = self.buildName(source, '', 'gif')

        gifId = self.idGenerator()

        # Number of volumes in the 4D image
        vSize = mriutil.getNbDirectionsFromDWI(source)
        vols = [gifId + '{0:04}'.format(i) for i in range(vSize)]

        # Spliting 4D image
        cmd = 'fslsplit {} {} -t'.format(source, gifId)
        self.launchCommand(cmd)

        # Extracting pngs from all volumes
        for vol in vols:
            self.pngSlicerImage(vol)

        # Creating .gif
        cmd = 'convert '
        for vol in vols:
            tmp = self.buildName(vol, '', 'png')
            cmd += '-delay {} {} '.format(str(gifSpeed), tmp)

        cmd += target
        self.launchCommand(cmd)

        # Cleaning temp files
        cmd = 'rm {0}*.png {0}*.nii.gz'.format(gifId)
        self.launchCommand(cmd)
        return target

    def __snrCalc(self, input, seg):
        """To implement
        
        """
        #target = self.buildName(input, 'snr')
        ccIdList = util.arrayOfInteger(self.config.get('masking','corpus_collosum'))
        ccMask = mriutil.extractFreesurferStructure(ccIdList, seg, 'cc_mask.nii')


        #mask_cc_part_img = nib.Nifti1Image(mask_cc_part.astype(np.uint8), affine)

        img = nib.load(input)
        data = img.get_data()

        #maskImg = nib.load(ccMask)
        maskImg = nib.Nifti1Image(ccMask.astype(np.uint8), affine)
        dataMask = maskImg.get_data()

        #region = 90
        #fig = plt.figure('Corpus callosum segmentation')
        #plt.subplot(1, 2, 1)
        #plt.title("Corpus callosum (CC)")
        ##plt.axis('off')
        #red = data[..., 0]
        #plt.imshow(np.rot90(red[region]))

        #plt.subplot(1, 2, 2)
        #plt.title("CC mask used for SNR computation")
        ##plt.axis('off')
        #plt.imshow(np.rot90(ccMaskData[region]))
        #fig.savefig("CC_segmentation.png", bbox_inches='tight')

        print img.shape
        print maskImg.shape

        print len(dataMask[0][0])
        print maskImg.get_data_dtype()
        mean_signal = np.mean(data[dataMask], axis=0)
        #print mean_signal

        #print mean_signal
        #structures = mriutil.extractFreesurferStructure(regions, source, targetImageName)
        #structureMask = structures.replace(".nii","%s.nii"%self.config.get('postfix','mask'))

        #self.info("Create a mask from %s image"%(structures))
        #self.info(mriutil.fslmaths(structures, structureMask, 'bin'))

    def writeTable(self, imageLink, legend):
        """
        return html table with one column 
        """
        tags = {'imageLink':imageLink, 'legend':legend}
        return self.parseTemplate(tags, os.path.join(self.toadDir, "templates/files/qa.table.tpl"))
