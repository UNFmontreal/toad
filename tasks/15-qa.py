from lib.generictask import GenericTask
from lib import util, mriutil
from string import ascii_uppercase, digits
from random import choice
import numpy as np
import nibabel as nib
import matplotlib as mpl
mpl.use('Agg') 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os


__author__ = 'cbedetti'

class QA(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preparation', 'unwarping', 'denoising', 'preprocessing', 'parcellation',  'registration')
        self.reportName = self.config.get('qa','report_name')
        self.imgWidth = 650
        self.dirty = True #change to False after one execution of implement
        self.debug = False


    def implement(self):

        #Usefull images for the QA
        anat = self.getImage(self.preparationDir,'anat')
        dwi = self.getImage(self.preparationDir,'dwi')
        bvec = self.getImage(self.preparationDir, 'grad',  None, 'bvec')
        brain = self.getImage(self.preprocessingDir,'anat','brain')
        wm = self.getImage(self.preprocessingDir,'anat','wm')
        dwi_up = self.getImage(self.preprocessingDir, 'dwi' ,'upsample')
        b0_up = self.getImage(self.preprocessingDir, 'b0' ,'upsample')
        anatfs = self.getImage(self.parcellationDir, 'anat_freesurfer')
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
        
        #Special case for unwarping and denoising
        
        unwarp = self.getImage(self.unwarpingDir,'dwi','unwarp')
        if unwarp:
            bvec_eddy = self.getImage(self.unwarpingDir, 'grad', 'eddy', 'bvec')
            eddy_parameters = os.path.join(self.subjectDir, self.unwarpingDir, "tmp.nii.eddy_parameters")
            unwarp_tg = self.buildName(unwarp, None, 'gif', False)
            translation_tg = 'translation.png'
            rotation_tg = 'rotation.png'
        else:
            bvec_eddy = False
            eddy_parameters = False
            unwarp_tg = None
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
            (unwarp, unwarp_tg),
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
        if unwarp:
            gradVectorLegend += ' | Black + : movement corrected bvec'

        dwiQaTags = [
            ('Raw', dwi_tg, str(mriutil.getMriDimensions(dwi))),
            ('DWI Unwarp', unwarp_tg, None),
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

        self.dirty = False

    def __idGenerator(self, size=6, chars=ascii_uppercase + digits):
        """
        Generate random strings
        Default: lenght of 6 uppercase and digits
        """
        return ''.join(choice(chars) for _ in range(size))
        
        
    def __slicer(self, bg, ol, tgPng):
        """
        Utility method to use slicer from FSL package
            bg : background image
            ol : optional overlay: put the edges of the image on top of the background
            tgPng : output in png format
        """
        cmd = 'slicer ' + bg + ' '
        if ol != None:
            cmd += ol + ' '
        cmd += '-a ' + tgPng
        self.launchCommand(cmd)
        
    
    def __c3dSeg(self, bg, seg, tgPng, scale, opacity):
        """
        Utility method to use c3d from ITKSnap package
            bg : background image
            seg : segmentation image
            tgPng : output in png format
            scale the background image
            opacity of the segmentation between 0 and 1
        """
        for axes in ['x', 'y', 'z']:
            cmd = 'c3d ' + bg + ' -scale ' + scale + ' ' + seg + ' '
            cmd += '-foreach -slice ' + axes + ' 50% -endfor '
            cmd += '-oli ' + os.path.join(self.toadDir, "templates/lookup_tables/") + 'FreeSurferColorLUT_ItkSnap.txt ' + opacity + ' -type uchar -omc ' + axes + '.png'
            self.launchCommand(cmd)
        cmd = 'pngappend x.png + y.png + z.png ' + tgPng
        self.launchCommand(cmd)
        cmd = 'rm x.png y.png z.png'
        self.launchCommand(cmd)
        
    
    def __nii4dtoGif(self, inputfile, tgGif, gifSpeed=30):
        """
        Create a animated gif from a 4d NIfTI
        
        Compulsory arguments :
        inputfile 4D NIfTI image
        tgGif : outputfile gif name
        
        Optional arguments :
        gifSpeed    : delay between images (tens of ms), default=30
        """
        gifId = self.__idGenerator()
        
        # Number of volumes in the 4D image
        vSize = mriutil.getNbDirectionsFromDWI(inputfile)
        vols = [gifId + '{0:04}'.format(i) for i in range(vSize)]
        
        # Spliting 4D image
        cmd = 'fslsplit ' + inputfile + ' ' + gifId + ' -t'
        self.launchCommand(cmd)
        
        # Extracting pngs from all volumes
        for vol in vols:
            self.__slicer(vol, None, vol + '.png')
        
        # Creating .gif
        cmd = 'convert '
        for vol in vols:
            cmd += '-delay ' + str(gifSpeed) + ' ' + vol + '.png '
        cmd += tgGif
        self.launchCommand(cmd)
        
        # Cleaning temp files
        cmd = 'rm ' + gifId + '*'
        self.launchCommand(cmd)


    def __plotMvt(self, eddypm, translationOutput, rotationOutput):
        """
        
        """
        parameters = np.loadtxt(eddypm)
        
        Vsize = len(parameters)
        vols = range(0,Vsize-1)
        
        translations = parameters[1:Vsize,0:3]
        
        rotations = parameters[1:Vsize,3:6]
        rotations = rotations / np.pi * 180
        
        plotdata = [
            (translations,'translation (mm)',translationOutput),
            (rotations,'rotation (degree)',rotationOutput)
            ]
        
        for data, ylabel, pngoutput in plotdata:
            plt.clf()
            px, = plt.plot(vols, data[:,0])
            py, = plt.plot(vols, data[:,1])
            pz, = plt.plot(vols, data[:,2])
            plt.xlabel('DWI volumes')
            plt.xlim([0,Vsize+10])
            plt.ylabel(ylabel)
            plt.legend([px, py, pz], ['x', 'y', 'z'])
            plt.savefig(pngoutput)
    
    
    def __plotVectors(self, rawBvec, eddyBvec, outputfile):
        """
        
        """
        gifId = self.__idGenerator()
        fig = plt.figure()
        ax = Axes3D(fig)
        
        bvec1 = np.loadtxt(rawBvec)
        bvec0= -bvec1
        
        graphParam = [(80, 'b', 'o', bvec0), (80, 'r', 'o', bvec1)]
        
        if eddyBvec:
            bvec2 = np.loadtxt(eddyBvec)
            graphParam.append((20, 'k', '+', bvec2))
        
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
        plt.axis('off')
        
        cmd = 'convert '
        for ii in xrange(0,360,2):
            ax.view_init(elev=10., azim=ii)
            plt.savefig(gifId+str(ii)+'.png')
            cmd += '-delay 10 ' + gifId + str(ii) + '.png '
        cmd += outputfile
        self.launchCommand(cmd)
        cmd = 'rm ' + gifId + '*'
        self.launchCommand(cmd)
        
        
    def __snrCalc(self, input, seg):
        """
        
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
        
            
    def __writeTable(self, title, imgLink, legend=None):
        """
        return html table with one column 
        """
        tags = {'title':title}
        
        if imgLink !=None:
            tags['image'] = self.parseTemplate({'imgLink': imgLink, 'imgWidth':self.imgWidth} ,"%stemplates/files/qa.image.tpl"%self.toadDir)
        else:
            tags['image'] = 'Step not performed during the pipeline execution'
        
        if legend != None:
            tags['legend'] = self.parseTemplate({'legend': legend} ,"%stemplates/files/qa.legend.tpl"%self.toadDir)
        else:
            tags['legend'] = ''
            
        return self.parseTemplate(tags, os.path.join(self.toadDir, "templates/files/qa.table.tpl"))


    def meetRequirement(self, result=True):
        """
        """ 
	
        anat = self.getImage(self.preparationDir,'anat')
        dwi = self.getImage(self.preparationDir,'dwi')
        bvec = self.getImage(self.preparationDir, 'grad',  None, 'bvec')
        brain = self.getImage(self.preprocessingDir,'anat','brain')
        wm = self.getImage(self.preprocessingDir,'anat','wm')
        b0_up = self.getImage(self.preprocessingDir, 'b0' ,'upsample')
        anatfs = self.getImage(self.parcellationDir, 'anat_freesurfer')
        aparcaseg = self.getImage(self.parcellationDir, 'aparc_aseg')
        brodmann = self.getImage(self.parcellationDir, 'brodmann')
        brain_rs = self.getImage(self.registrationDir,'anat',['brain','resample'])
        wm_rs = self.getImage(self.registrationDir,'anat',['brain','wm','resample'])
        aparcaseg_rs = self.getImage(self.registrationDir, 'aparc_aseg', 'resample')
        brodmann_rs = self.getImage(self.registrationDir, 'brodmann', 'resample')
        
        infoMessages = {
            anat:'No anatomical image found in directory %s.'%self.preparationDir,
            dwi:'No DWI image found in directory %s.'%self.preparationDir,
            bvec:'No gradient file found in directory %s.'%self.preparationDir,
            brain:'No brain image found in directory %s.'%self.preprocessingDir,
            wm:'No white matter image found in directory %s.'%self.preprocessingDir,
            b0_up:'No B0 upsample image found in directory %s.'%self.preprocessingDir,
            anatfs:'No Freesurfer anatomical image found in directory %s.'%self.parcellationDir,
            aparcaseg:'No aparc_aseg image found in directory %s.'%self.parcellationDir,
            brodmann:'No Brodmann segmentation image found in directory %s.'%self.parcellationDir,
            brain_rs:'No brain resample image found in directory %s.'%self.registrationDir,
            wm_rs:'No white matter resample image found in directory %s.'%self.registrationDir,
            aparcaseg_rs:'No aparc_aseg resample image found in directory %s.'%self.registrationDir,
            brodmann_rs:'No Brodmann segmentation resample image found in directory %s.'%self.registrationDir,
            }
        
        for key, value in infoMessages.iteritems():
            if key == False:
                self.info(value)
                result = False
                
        return result

    def isDirty(self):
        """Validate if this tasks need to be submit for implementation

        """
	return self.dirty
