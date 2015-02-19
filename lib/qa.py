from string import ascii_uppercase, digits
from random import choice
from lib import mriutil
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
            cmd = 'c3d {}  -scale  {} {} -foreach -slice {} 50% -endfor -oli {} {} -type uchar -omc {}'\
                .format(backgroundImage, scale, segmentationImage, axes, lutImage, opacity, tmp)
            self.launchCommand(cmd)

        cmd = 'pngappend x.png + y.png + z.png {}'.format(target)
        self.launchCommand(cmd)

        cmd = 'rm x.png y.png z.png'
        self.launchCommand(cmd)


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
