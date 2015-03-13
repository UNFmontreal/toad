from string import ascii_uppercase, digits
from random import choice
from lib import util, mriutil
import shutil
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


    def createQaReport(self, imagesArray):
        """create html report for a task with qaSupplier implemented

        Args:
           imagesArray : array of tupple [(imageLink, legend), ...]
        """

        imagesDir = os.path.join(self.qaDir, 'img')
        tablesCode = ''
        for imageLink, legend in imagesArray:
            #@TODO Take into account multiple run of QA
            shutil.copyfile(imageLink, os.path.join(imagesDir, imageLink))
            tags = {'imageLink':imageLink,'legend':legend}
            tablesCode += self.parseTemplate(tags, os.path.join(self.toadDir, 'templates/files/qa.table.tpl'))

        htmlCode = self.parseTemplate({'parseHtmlTables':tablesCode}, os.path.join(self.toadDir, 'templates/files/qa.main.tpl'))

        htmlFile = os.path.join(self.qaDir,'{}.html'.format(self.getName()))
        util.createScript(htmlFile, htmlCode)

        """
        #Usefull images for the QA
        anat = self.getImage(self.preparationDir,'anat')
        dwi = self.getImage(self.preparationDir,'dwi')
        bvec = self.getImage(self.preparationDir, 'grad',  None, 'bvec')
        bval = self.getImage(self.preparationDir, 'grad', None, 'bval')
        brain = self.getImage(self.preprocessingDir,'anat','brain')
        wm = self.getImage(self.preprocessingDir,'anat','wm')
        dwi_up = self.getImage(self.preprocessingDir, 'dwi' ,'upsample')
        b0_up = os.path.join(self.workingDir, os.path.basename(dwi_up).replace(self.config.get("prefix", 'dwi'), self.config.get("prefix", 'b0')))
        self.info(mriutil.extractFirstB0FromDwi(dwi_up, b0_up, bval))
        anatfs = self.getImage(self.parcellationDir, 'freesurfer_anat')
        aparcaseg = self.getImage(self.parcellationDir, 'aparc_aseg')
        brodmann = self.getImage(self.parcellationDir, 'brodmann')
        brain_rs = self.getImage(self.registrationDir,'anat',['brain','resample'])
        wm_rs = self.getImage(self.registrationDir,'anat',['brain','wm','resample'])
        aparcaseg_rs = self.getImage(self.registrationDir, 'aparc_aseg', 'resample')
        brodmann_rs = self.getImage(self.registrationDir, 'brodmann', 'resample')

        #png and gif targets
        anat_tg = self.buildName(anat, None, 'png', False)
        brain_tg = self.buildName(brain, None, 'png', False)
        wm_tg = self.buildName(wm, None, 'png', False)
        anatfs_tg = self.buildName(anatfs, None, 'png', False)
        aparcaseg_tg = self.buildName(aparcaseg, None, 'png', False)
        brodmann_tg = self.buildName(brodmann, None, 'png', False)
        dwi_tg = self.buildName(dwi, None, 'gif', False)
        vector_tg = 'vector.gif'
        snr_tg = 'snr.png'
        snr_denoised_tg = 'snr_denoised.png'
        brain_rs_tg = self.buildName(brain_rs, None, 'png', False)
        wm_rs_tg = self.buildName(wm_rs, None, 'png', False)
        aparcaseg_rs_tg = self.buildName(aparcaseg_rs, None, 'png', False)
        brodmann_rs_tg = self.buildName(brodmann_rs, None, 'png', False)
        
        #Special case for eddy_correction and denoising
        
        eddy = self.getImage(self.eddyDir,'dwi','eddy')
        if eddy:
            bvec_eddy = self.getImage(self.eddyDir, 'grad', 'eddy', 'bvec')
            #@TODO this line of code is not working
            #eddy_parameters = os.path.join(self.subjectDir, self.eddyDir, "tmp.nii.eddy_parameters")
            import glob
            fixs = glob.glob("{}/*_temporary.nii.eddy_parameters".format(self.eddyDir))
            for fix in fixs:
                eddy_parameters = fix

            eddy_tg = self.buildName(eddy, None, 'gif', False)
            translation_tg = 'translation.png'
            rotation_tg = 'rotation.png'
        else:
            bvec_eddy = False
            eddy_parameters = False
            eddy_tg = None
            translation_tg = None
            rotation_tg = None

        denoise = self.getImage(self.denoisingDir,'dwi','denoise')
        if denoise:
            denoise_tg = self.buildName(denoise, None, 'gif', False)        
        else:
            denoise_tg = None
        # slicer images production
        slicerImages = [
            (anat, None, anat_tg),
            (anat, brain, brain_tg),
            (anat, wm, wm_tg),
            (anatfs, None, anatfs_tg),
            (b0_up, brain_rs, brain_rs_tg),
            (b0_up, wm_rs, wm_rs_tg),
            ]
        for background, overlay, target in slicerImages:
            if not self.debug:
                self.__slicer(background, overlay, target)
        
        #c3d images production
        c3dImages = [
            (anatfs, aparcaseg, aparcaseg_tg, '2', '0.5'),
            (anatfs, brodmann, brodmann_tg, '2', '0.5'),
            (b0_up, aparcaseg_rs, aparcaseg_rs_tg, '1', '0.95'),
            (b0_up, brodmann_rs, brodmann_rs_tg, '1', '0.95'),
            ]
        for background, segmentation, target, scale, opacity in c3dImages:
            if not self.debug:
                self.__c3dSeg(background, segmentation, target, scale, opacity)
        
        #nii4dtoGif images production
        nii4dtoGifImages = [
            (dwi, dwi_tg),
            (eddy, eddy_tg),
            (denoise, denoise_tg),
            ]
        for image, target in nii4dtoGifImages:
            if not self.debug:
                if image:
                    self.__nii4dtoGif(image, target)
                else:
                    target = None
                    
        #eddy movement images production
        if not self.debug:
            if eddy_parameters:
                self.__plotMvt(eddy_parameters, translation_tg, rotation_tg)
            else:
                translation_tg = None
                rotation_tg = None
        
        #Gradient vector image production
        if not self.debug:
            self.__plotVectors(bvec, bvec_eddy, vector_tg)
        
        #SNR calculation
        #self.__snrCalc(dwi_up, aparcaseg_rs)
        
        
        #### Anat QA ####
        anatQaTags = [
            ('T1 Raw', anat_tg, str(mriutil.getMriDimensions(anat))),
            ('Brain mask', brain_tg, None),
            ('White matter segmentation', wm_tg, None),
            ('T1 Freesurfer', anatfs_tg, str(mriutil.getMriDimensions(anatfs))),
            ('Freesurfer aparc_aseg', aparcaseg_tg, None),
            ('Freesurfer brodmann', brodmann_tg, None),
            ]
        parseT1Here = ''
        for title, image, legend in anatQaTags:
            parseT1Here += self.__writeTable(title, image, legend)
        
        #### DWI QA ####
        gradVectorLegend = 'Red : raw bvec | Blue : opposite bvec'
        if eddy:
            gradVectorLegend += ' | Black + : movement corrected bvec'

        dwiQaTags = [
            ('Raw', dwi_tg, str(mriutil.getMriDimensions(dwi))),
            ('DWI eddy', eddy_tg, None),
            ('Translation correction by eddy', translation_tg, None),
            ('Rotation correction by eddy', rotation_tg, None),
            ('Gradients vectors on the unitary sphere', vector_tg, gradVectorLegend),
            ('DWI Denoising', denoise_tg, None),
            ]
        parseDWIHere = ''
        for title, image, legend in dwiQaTags:
            parseDWIHere += self.__writeTable(title, image, legend)
            
        
        #### Registration QA ####
        regQaTags = [
            ('Brain Registration', brain_rs_tg, None),
            ('WM Registration', wm_rs_tg, None),
            ('Freesurfer aparc_aseg resample', aparcaseg_rs_tg, None),
            ('Freesurfer brodmann resample', brodmann_rs_tg, None),
            ]
        parseRegistrationHere = ''
        for title, image, legend in regQaTags:
            parseRegistrationHere += self.__writeTable(title, image, legend)
        
        
        #### html production ####
        tags = {'parseT1Here': parseT1Here, 'parseDWIHere': parseDWIHere, 'parseRegistrationHere': parseRegistrationHere }
        htmlCode = self.parseTemplate(tags, os.path.join(self.toadDir, "templates/files/qa.main.tpl"))
        util.createScript(self.reportName, htmlCode)
        """

