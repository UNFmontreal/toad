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
        GenericTask.__init__(self, subject, 'preparation', 'eddy', 'denoising', 'preprocessing', 'parcellation',  'registration')
        self.reportName = self.config.get('qa','report_name')
        self.imgWidth = 650
        self.dirty = True #change to False after one execution of implement
        self.debug = False


    def implement(self):
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
        self.dirty = False

        

    


        
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
        anat = self.getImage(self.preparationDir,'anat')
        dwi = self.getImage(self.preparationDir,'dwi')
        bvec = self.getImage(self.preparationDir, 'grad',  None, 'bvec')
        brain = self.getImage(self.preprocessingDir,'anat','brain')
        wm = self.getImage(self.preprocessingDir,'anat','wm')
        #b0_up = self.getImage(self.preprocessingDir, 'b0' ,'upsample')
        anatfs = self.getImage(self.parcellationDir, 'freesurfer_anat')
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
            #b0_up:'No B0 upsample image found in directory %s.'%self.preprocessingDir,
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
        """

        return True

    def isDirty(self):
        """Validate if this tasks need to be submit for implementation

        """
        return self.dirty
