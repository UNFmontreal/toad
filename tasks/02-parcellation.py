import os
import numpy
import scipy, scipy.ndimage
import nibabel
import random
from tvtk.api import tvtk
from core.generictask import GenericTask
from lib.images import Images
from lib import util, mriutil

__author__ = 'desmat'


class Parcellation(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preparation', 'qa')
        self.id = self.get('id')
        self.setCleanupBeforeImplement(False)


    def implement(self):

        anat = self.getImage(self.dependDir, 'anat')

        #look if a freesurfer tree is already available
        if not  self.__findAndLinkFreesurferStructure():
            self.__submitReconAll(anat)

        self.__convertFeesurferImageIntoNifti(anat)
        self.__createImageFromAtlas("template_brodmann", self.get("brodmann"))
        self.__createImageFromAtlas("template_buckner", self.get("buckner"))
        self.__createImageFromAtlas("template_choi", self.get("choi"))
        self.__createSegmentationMask(self.get('aparc_aseg'), self.get('mask'))
        tt5Mgz = self.__create5ttImage()
        self. __convertAndRestride(tt5Mgz, self.get('tt5'))


        anatFreesurfer = self.getImage(self.workingDir, 'anat', 'freesurfer')

        if self.get('cleanup'):
            self.__cleanup()


    def __findAndLinkFreesurferStructure(self):
        """Look if a freesurfer structure already exists in the backup.

        freesurfer structure will be link and id will be update

        Returns:
            Return the linked directory name if a freesurfer structure is found, False otherwise
        """
        freesurferStructure = os.path.join(self.dependDir, self.id)
        if mriutil.isAfreesurferStructure(freesurferStructure):
           self.info("{} seem\'s a valid freesurfer structure: moving it to {} directory".format(freesurferStructure, self.workingDir))
           util.symlink(freesurferStructure, self.id)
           return True
        return False


    def __submitReconAll(self, anatomical):
        """Submit recon-all on the anatomical image
        Args:
            anatomical: the high resolution image
        """
        treeName = "freesurfer_{}".format(self.getTimestamp().replace(" ","_"))

        #backup already existing tree
        if os.path.isdir(self.id):
            self.info("renaming existing freesurfer tree {} to {}".format(self.id, treeName))
            os.rename(self.id, treeName)

        self.info("Starting parcellation with freesurfer")
        self.info("Set SUBJECTS_DIR to {}".format(self.workingDir))
        os.environ["SUBJECTS_DIR"] = self.workingDir
        cmd = "recon-all -{} -i {} -subjid {} -sd {} -openmp {}"\
            .format(self.get('directive'), anatomical, self.id, self.workingDir, self.getNTreads())
        self.info("Log could be found at {}/{}/scripts/recon-all.log".format(self.workingDir, self.id))
        self.launchCommand(cmd, None, None, 86400)


    def __convertFeesurferImageIntoNifti(self, anatomicalName):

        """
            Convert a List of mgz fresurfer into nifti compress format

        Args:
            anatomicalName: The subject anatomical image is need to identify the proper T1

        """
        for (target, source) in [(self.buildName(anatomicalName, 'freesurfer'), "T1.mgz"),
                                    (self.get('aparc_aseg'), "aparc+aseg.mgz"),
                                    (self.get('rh_ribbon'), "rh.ribbon.mgz"),
                                    (self.get('lh_ribbon'), "lh.ribbon.mgz"),
                                    (self.get('norm'), "norm.mgz")]:

            self.__convertAndRestride(self.__findImageInDirectory(source, os.path.join(self.workingDir, self.id)), target)

    """
    def __createBrodmannImage(self):

            Create a brodmann area map

        Returns:
            A brodmann area images


        brodmannTemplate = os.path.join(self.toadDir, "templates", "mri", self.get("templates_brodmann"))
        target = self.get("brodmann")
        self.info("Set SUBJECTS_DIR to {}".format(self.workingDir))
        os.environ["SUBJECTS_DIR"] = self.workingDir

        #@TODO remove all trace of mgz file
        cmd = "mri_vol2vol --mov {} --targ $FREESURFER_HOME/subjects/fsaverage/mri/T1.mgz" \
              " --o brodmann_fsaverage.mgz --regheader --interp nearest".format(brodmannTemplate)
        self.launchCommand(cmd)

        cmd =  "mri_vol2vol --mov $SUBJECTS_DIR/{0}/mri/norm.mgz --targ brodmann_fsaverage.mgz --s {0} " \
               " --m3z talairach.m3z --o {1} --interp nearest --inv-morph".format(self.id, target)
        self.launchCommand(cmd)
        return self.__convertAndRestride(target, target)
    """



    def __create5ttImage(self, subdiv=4):
        """

        """

        subjectDir = os.path.join(self.workingDir, self.id)
        aparcAseg = self.__findImageInDirectory("aparc+aseg.mgz", subjectDir)
        lhWhite = self.__findImageInDirectory("lh.white", subjectDir)
        rhWhite = self.__findImageInDirectory("rh.white", subjectDir)
        lhPial = self.__findImageInDirectory("lh.pial", subjectDir)
        rhPial = self.__findImageInDirectory("rh.pial", subjectDir)
        target = 'tmp_5tt_{0:.6g}.mgz'.format(random.randint(0,999999))

        def read_surf(fname, surf_ref):
            if fname[-4:] == '.gii':
                gii = nibabel.gifti.read(fname)
                return gii.darrays[0].data, gii.darrays[1].data
            else:
                verts,tris =  nibabel.freesurfer.read_geometry(fname)
                ras2vox = numpy.array([[-1,0,0,128], [0,0,-1,128], [0,1,0,128], [0,0,0,1]])
                surf2world = surf_ref.get_affine().dot(ras2vox)
                verts[:] = nibabel.affines.apply_affine(surf2world, verts)
                return verts, tris

        def surf_fill2(vertices, polys, mat, shape):
            from tvtk.common import is_old_pipeline
            voxverts = nibabel.affines.apply_affine(numpy.linalg.inv(mat), vertices)

            pd = tvtk.PolyData(points=voxverts, polys=polys)

            if is_old_pipeline():
                whiteimg = tvtk.ImageData(dimensions = shape, scalar_type = 'unsigned_char')
            else:
                whiteimg = tvtk.ImageData(dimensions = shape)
            whiteimg.point_data.scalars = numpy.ones(numpy.prod(shape), dtype=numpy.uint8)

            pdtis = tvtk.PolyDataToImageStencil()
            if is_old_pipeline():
                pdtis.input = pd
            else:
                pdtis.set_input_data(pd)
                                                                             
            pdtis.output_whole_extent = whiteimg.extent
            pdtis.update()

            imgstenc = tvtk.ImageStencil()
            if is_old_pipeline():
                imgstenc.input = whiteimg
                imgstenc.stencil = pdtis.output
            else:
                imgstenc.set_input_data(whiteimg)
            imgstenc.set_stencil_data(pdtis.output)
            imgstenc.background_value = 0
            imgstenc.update()

            data = imgstenc.output.point_data.scalars.to_array().reshape(shape[::-1]).transpose(2,1,0)
            return data


        def fill_hemis(lh_surf,rh_surf):
            vertices = numpy.vstack([lh_surf[0],rh_surf[0]])
            tris = numpy.vstack([lh_surf[1],
                              rh_surf[1]+lh_surf[0].shape[0]])
            mat = parc.affine.dot(numpy.diag([1/float(subdiv)]*3+[1]))
            shape = numpy.asarray(parc.shape)*subdiv
            fill = surf_fill2(vertices, tris, mat, shape)
            pve = reduce(
                lambda x,y: x+fill[y[0]::subdiv,y[1]::subdiv,y[2]::subdiv],
                numpy.mgrid[:subdiv,:subdiv,:subdiv].reshape(3,-1).T,0
                ).astype(numpy.float32)
            pve /= float(subdiv**3)
            return pve


        def group_rois(rois_ids):
            m = numpy.zeros(parc.shape, dtype=numpy.bool)
            for i in rois_ids:
                numpy.logical_or(parc_data==i, m, m)
            return m


        parc = nibabel.load(aparcAseg)
        voxsize = numpy.asarray(parc.header.get_zooms()[:3])
        parc_data = parc.get_data()
        lh_wm = read_surf(lhWhite, parc)
        rh_wm = read_surf(rhWhite, parc)
        lh_gm = read_surf(lhPial, parc)
        rh_gm = read_surf(rhPial, parc)
        wm_pve = fill_hemis(lh_wm,rh_wm)
        gm_pve = fill_hemis(lh_gm,rh_gm)

        gm_rois = group_rois([8,47,17,18,53,54]).astype(numpy.float32)
        gm_smooth = scipy.ndimage.gaussian_filter(gm_rois, sigma=voxsize)

        subcort_rois = group_rois([10,11,12,13,26,49,50,51,52,58]).astype(numpy.float32)
        subcort_smooth = scipy.ndimage.gaussian_filter(subcort_rois, sigma=voxsize)

        wm_rois = group_rois([7,16,28,46,60,85,192,88,
                             250,251,252,253,254,255]).astype(numpy.float32)

        wm_smooth = scipy.ndimage.gaussian_filter(wm_rois,sigma=voxsize)
        bs_mask = parc_data==16
        bs_vdc_dil = scipy.ndimage.morphology.binary_dilation(group_rois([16,60,28]), iterations=2)
        bs_vdc_excl = numpy.logical_and(bs_vdc_dil, numpy.logical_not(group_rois([16,7,46,60,28,10,49,2,41,0])))

        lbs = numpy.where((bs_mask).any(-1).any(0))[0][-1]-3

        parc_data_mask = parc_data>0
        outer_csf = numpy.logical_and(
            numpy.logical_not(parc_data_mask),
            scipy.ndimage.morphology.binary_dilation(parc_data_mask))


        csf_rois = group_rois([4,5,14,15,24,30,31,43,44,62,63,72])

        csf_smooth = scipy.ndimage.gaussian_filter(
            numpy.logical_or(csf_rois, outer_csf).astype(numpy.float32),
            sigma=voxsize)

        bs_roi = csf_smooth.copy()
        bs_roi[...,:lbs,:] = 0
        csf_smooth[...,lbs:,:] = 0
        wm_smooth[...,lbs:,:] = 0

        # add csf around brainstem and ventral DC to remove direct connection to gray matter
        csf_smooth[bs_vdc_excl] += gm_smooth[bs_vdc_excl]
        gm_smooth[bs_vdc_excl] = 0

        mask88 = parc_data==88
        wm = wm_pve+wm_smooth-csf_smooth-subcort_smooth
        wm[wm>1] = 1
        wm[wm<0] = 0

        gm = gm_pve-wm_pve-wm-subcort_smooth+gm_smooth+bs_roi
        gm[gm<0] = 0

        tt5 = numpy.concatenate([gm[...,numpy.newaxis],
                              subcort_smooth[...,numpy.newaxis],
                              wm[...,numpy.newaxis],
                              csf_smooth[...,numpy.newaxis],
                              numpy.zeros(parc.shape+(1,),dtype=numpy.float32)],3)


        tt5/=tt5.sum(-1)[..., numpy.newaxis]
        tt5[numpy.isnan(tt5)]=0

        nibabel.save(nibabel.Nifti1Image(tt5.astype(numpy.float32),parc.get_affine()), target)
        return target



    def __createImageFromAtlas(self, source, target):
        """
            Create a area map base on a source name
        Args:
            source: template name as specify into config.cfg
            target: output file name

        Returns:
            A brodmann area images

        """
        tmpImage = 'tmp_{0:.6g}.mgz'.format(random.randint(0,999999))
        template = os.path.join(self.toadDir, "templates", "mri", self.get(source))

        self.info("Set SUBJECTS_DIR to {}".format(self.workingDir))
        os.environ["SUBJECTS_DIR"] = self.workingDir

        #@TODO remove all trace of mgz file
        cmd = "mri_vol2vol --mov {} --targ $FREESURFER_HOME/subjects/fsaverage/mri/T1.mgz" \
              " --o {} --regheader --interp nearest".format(template, tmpImage)
        self.launchCommand(cmd)

        cmd =  "mri_vol2vol --mov $SUBJECTS_DIR/{0}/mri/norm.mgz --targ {1} --s {0} " \
               " --m3z talairach.m3z --o {2} --interp nearest --inv-morph".format(self.id, tmpImage, target)
        self.launchCommand(cmd)
        return self.__convertAndRestride(target, target)


    def __convertAndRestride(self, source, target):
        """Utility for converting between different file formats

        Args:
            source: The input source file
            target: The name of the resulting output file name

        """
        self.info("convert {} image to {} ".format(source, target))
        cmd = "mrconvert {} {} -stride {} -force -quiet"\
            .format(source, target, self.get('preparation', 'stride_orientation'))
        self.launchCommand(cmd)
        return target


    def __findImageInDirectory(self, image, freesurferDirectory):
        """Utility method that look if a input image could be found in a directory and his subdirectory

        Args:
            image: an input image name
            freesurferDirectory: the location of the freesurfer structure
        Returns:
            the file name if found, False otherwise

        """
        for root, dirs, files in os.walk(freesurferDirectory):
            if image in files:
                return os.path.join(root, image)
        return False


    def __createSegmentationMask(self, source, target):
        """
        Compute mask from freesurfer segmentation : aseg then morphological operations

        Args:
            source: The input source file
            target: The name of the resulting output file name
        """

        nii = nibabel.load(source)
        op = ((numpy.mgrid[:5,:5,:5]-2.0)**2).sum(0)<=4
        mask = scipy.ndimage.binary_closing(nii.get_data()>0, op, iterations=2)
        scipy.ndimage.binary_fill_holes(mask, output=mask)
        nibabel.save(nibabel.Nifti1Image(mask.astype(numpy.uint8), nii.get_affine()), target)
        del nii, mask, op
        return target


    def __linkExistingImage(self, images):
        """
            Create symbolic link for each existing input images into the current working directory.

        Args:
            images: A list of image

        Returns:
            A list of invalid images

        """
        unlinkedImages = {}
        #look for existing map store into preparation and link it so they are not created
        for key, value in images.iteritems():
            if value:
                self.info("Found {} area image, create link from {} to {}".format(key, value, self.workingDir))
                util.symlink(value, self.workingDir)
            else:
                unlinkedImages[key] = value
        return unlinkedImages


    def __cleanup(self):
        """Utility method that delete some symbolic links that are not usefull

        """
        import glob
        self.info("Cleaning up extra files")
        sources = glob.glob("*.mgz*")+glob.glob("*.lta")+glob.glob("*.reg")
        for source in sources:
            if os.path.isfile(source):
                os.remove(source)

    def meetRequirement(self):

        return  Images((self.getImage(self.dependDir, 'anat'), 'high resolution'))


    def isDirty(self):

        return Images((self.getImage(self.workingDir, 'aparc_aseg'), 'parcellation  atlas'),
                  (self.getImage(self.workingDir, 'anat', 'freesurfer'), 'anatomical'),
                  (self.getImage(self.workingDir, 'rh_ribbon'), 'rh_ribbon'),
                  (self.getImage(self.workingDir, 'lh_ribbon'), 'lh_ribbon'),
                  (self.getImage(self.workingDir, 'brodmann'), 'brodmann atlas'),
                  (self.getImage(self.workingDir, 'buckner'), 'buckner atlas'),
                  (self.getImage(self.workingDir, 'choi'), 'choi atlas'),
                  (self.getImage(self.workingDir, 'norm'), 'norm'),
                  (self.getImage(self.workingDir, 'mask'), 'freesurfer brain masks'),
                  (self.getImage(self.workingDir, 'tt5'), '5tt'),)

    
    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        #@TODO add buckner and choi templates

        #Get images
        anat = self.getImage(self.workingDir, 'anat')
        norm = self.getImage(self.workingDir, 'norm')
        brainMask = self.getImage(self.workingDir, 'mask')
        aparcAseg = self.getImage(self.workingDir, 'aparc_aseg')
        brodmann = self.getImage(self.workingDir, 'brodmann')

        #Build qa names
        anatPng = self.buildName(anat, None, 'png')
        brainMaskPng = self.buildName(brainMask, None, 'png')
        aparcAsegPng = self.buildName(aparcAseg, None, 'png')
        brodmannPng = self.buildName(brodmann, None, 'png')

        #Build qa images
        self.slicerPng(anat, anatPng, boundaries=brainMask)
        self.slicerPng(norm, brainMaskPng, maskOverlay=brainMask, boundaries=brainMask)
        self.slicerPng(anat, aparcAsegPng, segOverlay=aparcAseg, boundaries=aparcAseg)
        self.slicerPng(anat, brodmannPng, segOverlay=brodmann, boundaries=brodmann)

        qaImages = Images(
            (anatPng, 'High resolution anatomical image of freesurfer'),
            (brainMaskPng, 'Brain mask on norm from freesurfer'),
            (aparcAsegPng, 'Aparc aseg segmentation from freesurfer'),
            (brodmannPng, 'Brodmann segmentation from freesurfer'),
            )

        return qaImage
