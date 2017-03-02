# -*- coding: utf-8 -*-
import os
import random

import numpy
import scipy
import scipy.ndimage
import nibabel

from core.toad.generictask import GenericTask
from lib.images import Images
from lib import util, mriutil


__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers", "Basile Pinsard"]


class Parcellation(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preparation', 'qa')
        self.id = self.get('id')
        # self.setCleanupBeforeImplement(False)

    def implement(self):
        anat = self.getPreparationImage('anat')

        # Look if a freesurfer tree is already available
        if not self.__findAndLinkFreesurferStructure():
            self.__submitReconAll(anat)
            # @TODO backup the recon-all to backup dir

        self.__convertFreesurferImageIntoNifti(anat)
        self.__createSegmentationMask(self.get('aparc_aseg'), self.get('mask'))
        self.__mergeParcellation(self.get('wmparc'),self.get('aparc_aseg'),self.get('brainstem'),self.get('lhHipp'),self.get('rhHipp'))
        tt5Mgz = self.__create5ttImage()
        mriutil.convertAndRestride(tt5Mgz, self.get('tt5'), self.get('preparation', 'stride_orientation'))
        anatFreesurfer = self.getImage('anat', 'freesurfer')

        if self.get('cleanup'):
            self.__cleanup()

    def __mergeParcellation(self, wmparcFile, aparcFile, brainstemFile, lhHippFile, rhHippFile):

        wmparc = nibabel.load(wmparcFile)
        aparc = nibabel.load(aparcFile)
        brainstem = nibabel.load(brainstemFile)
        lhHipp = nibabel.load(lhHippFile)
        rhHipp = nibabel.load(rhHippFile)

        aparcData = aparc.get_data()
        wmparcData = wmparc.get_data()
        brainstemData = brainstem.get_data()
        lhHippData = lhHipp.get_data()
        rhHippData = rhHipp.get_data()


        # Replace Left-Hipp (17) and Right-Hipp (53) to WM
        for leftValue in [17]:
            aparcData[aparcData == leftValue] = 2
            wmparcData[wmparcData == leftValue] = 5001
        for rightValue in [53]:
            aparcData[aparcData == rightValue] = 41
            wmparcData[wmparcData == rightValue] = 5002

        # Remove brainstem(16) and 4th ventricule (15)
        for brainstemValue in [15, 16]:
            aparcData[aparcData == brainstemValue] = 0
            wmparcData[wmparcData == brainstemValue] = 0

        aparcData[brainstemData != 0] =  brainstemData[brainstemData != 0]
        wmparcData[brainstemData != 0] =  brainstemData[brainstemData != 0]

        lhHippData[lhHippData == 204] = 554 # presubiculum
        rhHippData[rhHippData == 204] = 504 # presubiculum
        lhHippData[lhHippData == 205] = 557 # subiculum
        rhHippData[rhHippData == 205] = 507 # subiculum
        lhHippData[lhHippData == 206] = 552 # CA1
        rhHippData[rhHippData == 206] = 502 # CA1
        lhHippData[lhHippData == 208] = 550 # CA3, fs=CA2_3
        rhHippData[rhHippData == 208] = 500 # CA3, fs=CA2_3
        lhHippData[lhHippData == 209] = 556 # CA4, fs=CA4_DG
        rhHippData[rhHippData == 209] = 506 # CA4, fs=CA4_DG
        lhHippData[lhHippData == 212] = 553 # fimbria
        rhHippData[rhHippData == 212] = 503 # fimbria
        lhHippData[lhHippData == 215] = 557 # Hipp Fissure, Same as subiculum?
        rhHippData[rhHippData == 215] = 507 # Hipp Fissure, Same as subiculum?

        # Invented
        lhHippData[lhHippData == 203] = 559 # Parasubiculum
        rhHippData[rhHippData == 203] = 509 # Parasubiculum
        lhHippData[lhHippData == 210] = 560 # GC-DC
        rhHippData[rhHippData == 210] = 510 # GC-DC
        lhHippData[lhHippData == 211] = 561 # HATA
        rhHippData[rhHippData == 211] = 511 # HATA
        lhHippData[lhHippData == 214] = 562 # Molecular Layer
        rhHippData[rhHippData == 214] = 512 # Molecular Layer
        lhHippData[lhHippData == 226] = 563 # Hipp Tail
        rhHippData[rhHippData == 226] = 513 # Hipp Tail

        aparcData[rhHippData != 0] =  rhHippData[rhHippData != 0]
        aparcData[lhHippData != 0] =  lhHippData[lhHippData != 0]
        wmparcData[rhHippData != 0] =  rhHippData[rhHippData != 0]
        wmparcData[lhHippData != 0] =  lhHippData[lhHippData != 0]

        nibabel.Nifti1Image(lhHippData, lhHipp.affine, lhHipp.header).to_filename(lhHippFile)
        nibabel.Nifti1Image(rhHippData, rhHipp.affine, rhHipp.header).to_filename(rhHippFile)
        nibabel.Nifti1Image(wmparcData, wmparc.affine, wmparc.header).to_filename(wmparcFile)
        nibabel.Nifti1Image(aparcData, aparc.affine, aparc.header).to_filename(aparcFile)


    def __findAndLinkFreesurferStructure(self):
        """Look if a freesurfer structure already exists in the backup.

        freesurfer structure will be link and id will be update

        Returns:
            Return the linked directory name if a freesurfer structure is found, False otherwise
        """
        freesurferStructure = os.path.join(self.preparationDir, self.id)
        if mriutil.isAfreesurferStructure(freesurferStructure):
            self.info("{} seem\'s a valid freesurfer structure: moving it to {} directory".format(freesurferStructure,
                                                                                                  self.workingDir))
            util.symlink(freesurferStructure, self.workingDir, self.id)
            return True

        return False

    def __submitReconAll(self, anatomical):
        """Submit recon-all on the anatomical image
        Args:
            anatomical: the high resolution image
        """
        treeName = "freesurfer_{}".format(self.getTimestamp().replace(" ", "_"))

        # Backup already existing tree
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
        # Run BrainStem segmentation
        cmd = "recon-all -s {} -sd {} -brainstem-structures"\
            .format(self.id, self.workingDir)
        self.info("Run brainstem segmentation")
        self.launchCommand(cmd, None, None, 86400)
        # Run Hippocampal SubField segmentation
        cmd = "recon-all -s {} -sd {} -hippocampal-subfields-T1"\
            .format(self.id, self.workingDir)
        self.info("Run hippocampal subfield segmentation")
        self.launchCommand(cmd, None, None, 86400)

    def __convertFreesurferImageIntoNifti(self, anatomicalName):

        """
            Convert a List of mgz fresurfer into nifti compress format

        Args:
            anatomicalName: The subject anatomical image is need to identify the proper T1

        """
        for (target, source) in [(self.buildName(anatomicalName, 'freesurfer'), "T1.mgz"),
                                    (self.get('aparc_aseg'), "aparc+aseg.mgz"),
                                    (self.get('wmparc'), "wmparc.mgz"),
                                    (self.get('rh_ribbon'), "rh.ribbon.mgz"),
                                    (self.get('lh_ribbon'), "lh.ribbon.mgz"),
                                    (self.get('brainstem'), "brainstemSsLabels.v10.FSvoxelSpace.mgz"),
                                    (self.get("rhHipp"), "rh.hippoSfLabels-T1.v10.FSvoxelSpace.mgz"),
                                    (self.get("lhHipp"), "lh.hippoSfLabels-T1.v10.FSvoxelSpace.mgz"),
                                    (self.get('norm'), "norm.mgz")]:

            mriutil.convertAndRestride(self.__findImageInDirectory(source, os.path.join(self.workingDir, self.id)),
                                       target,
                                       self.get('preparation', 'stride_orientation'))

    def __create5ttImage(self, subdiv=4):
        """

        :param subdiv:
        :return:
        """

        subjectDir = os.path.join(self.workingDir, self.id)
        aparcAseg = self.__findImageInDirectory("aparc+aseg.mgz", subjectDir)
        lhHippFile = self.__findImageInDirectory("lh.hippo", subjectDir)
        rhHippFile = self.__findImageInDirectory("rh.hippo", subjectDir)
        brainstemFile = self.__findImageInDirectory("brainstemSsLabels", subjectDir)
        lhWhite = self.__findImageInDirectory("lh.white", subjectDir)
        rhWhite = self.__findImageInDirectory("rh.white", subjectDir)
        lhPial = self.__findImageInDirectory("lh.pial", subjectDir)
        rhPial = self.__findImageInDirectory("rh.pial", subjectDir)
        target = 'tmp_5tt_{0:.6g}.mgz'.format(random.randint(0, 999999))

        def read_surf(fname, surf_ref):
            if fname[-4:] == '.gii':
                gii = nibabel.gifti.read(fname)
                return gii.darrays[0].data, gii.darrays[1].data
            else:
                verts, tris = nibabel.freesurfer.read_geometry(fname)
                ras2vox = numpy.array([[-1, 0, 0, 128], [0, 0, -1, 128], [0, 1, 0, 128], [0, 0, 0, 1]])
                surf2world = surf_ref.get_affine().dot(ras2vox)
                verts[:] = nibabel.affines.apply_affine(surf2world, verts)
                return verts, tris

        def surf_fill_vtk(vertices, polys, mat, shape):
            """

            :param vertices:
            :param polys:
            :param mat:
            :param shape:
            :return:
            """
            import vtk
            from vtk.util import numpy_support

            voxverts = nibabel.affines.apply_affine(numpy.linalg.inv(mat), vertices)
            points = vtk.vtkPoints()
            points.SetNumberOfPoints(len(voxverts))
            for i, pt in enumerate(voxverts):
                points.InsertPoint(i, pt)

            tris = vtk.vtkCellArray()
            for vert in polys:
                tris.InsertNextCell(len(vert))
                for v in vert:
                    tris.InsertCellPoint(v)

            pd = vtk.vtkPolyData()
            pd.SetPoints(points)
            pd.SetPolys(tris)
            del points, tris

            whiteimg = vtk.vtkImageData()
            whiteimg.SetDimensions(shape)
            if vtk.VTK_MAJOR_VERSION <= 5:
                whiteimg.SetScalarType(vtk.VTK_UNSIGNED_CHAR)
            else:
                info = vtk.vtkInformation()
                whiteimg.SetPointDataActiveScalarInfo(info, vtk.VTK_UNSIGNED_CHAR, 1)

            ones = numpy.ones(numpy.prod(shape), dtype=numpy.uint8)
            whiteimg.GetPointData().SetScalars(numpy_support.numpy_to_vtk(ones))

            pdtis = vtk.vtkPolyDataToImageStencil()
            if vtk.VTK_MAJOR_VERSION <= 5:
                pdtis.SetInput(pd)
            else:
                pdtis.SetInputData(pd)

            pdtis.SetOutputWholeExtent(whiteimg.GetExtent())
            pdtis.Update()

            imgstenc = vtk.vtkImageStencil()
            if vtk.VTK_MAJOR_VERSION <= 5:
                imgstenc.SetInput(whiteimg)
                imgstenc.SetStencil(pdtis.GetOutput())
            else:
                imgstenc.SetInputData(whiteimg)
                imgstenc.SetStencilConnection(pdtis.GetOutputPort())
            imgstenc.SetBackgroundValue(0)

            imgstenc.Update()

            data = numpy_support.vtk_to_numpy(
                imgstenc.GetOutput().GetPointData().GetScalars()).reshape(shape).transpose(2, 1, 0)
            del pd, voxverts, whiteimg, pdtis, imgstenc
            return data

        def fill_hemis(lh_surf, rh_surf):
            """

            :param lh_surf:
            :param rh_surf:
            :return:
            """
            vertices = numpy.vstack([lh_surf[0], rh_surf[0]])
            tris = numpy.vstack([lh_surf[1],
                                rh_surf[1]+lh_surf[0].shape[0]])
            mat = parc.affine.dot(numpy.diag([1/float(subdiv)]*3+[1]))
            shape = numpy.asarray(parc.shape)*subdiv
            fill = surf_fill_vtk(vertices, tris, mat, shape)
            pve = reduce(
                lambda x, y: x+fill[y[0]::subdiv, y[1]::subdiv, y[2]::subdiv],
                numpy.mgrid[:subdiv, :subdiv, :subdiv].reshape(3, -1).T, 0
                ).astype(numpy.float32)
            pve /= float(subdiv**3)
            return pve

        def group_rois(rois_ids):
            m = numpy.zeros(parc.shape, dtype=numpy.bool)
            for i in rois_ids:
                numpy.logical_or(parc_data == i, m, m)
            return m

        parc = nibabel.load(aparcAseg)
        parc_data = parc.get_data()
        voxsize = numpy.asarray(parc.header.get_zooms()[:3])
        lh_wm = read_surf(lhWhite, parc)
        rh_wm = read_surf(rhWhite, parc)
        lh_gm = read_surf(lhPial, parc)
        rh_gm = read_surf(rhPial, parc)
        wm_pve = fill_hemis(lh_wm, rh_wm)
        gm_pve = fill_hemis(lh_gm, rh_gm)

        gm_rois = group_rois([8,   # Left-Cerebellum-Cortex
                              47,  # Right-Cerebellum-Cortex
                              17,  # Left-Hippocampus
                              18,  # Left-Amygdala
                              53,  # Right-Hippocampus
                              54,  # Right-Amygdala
                              559, # Left-para-subiculum
                              554, # Left-pre-subiculum
                              557, # Left-subiculum
                              552, # Left-CA1
                              550, # Left-CA3
                              556, # Left-CA4
                              560, # Left-GC-DC
                              561, # Left-HATA
                              553, # Left-fimbria
                              562, # Left-molecular-layer
                              555, # Left-fissure
                              563, # Left-Hipp-Tail
                              509, # Right-para-subiculum
                              504, # Right-pre-subiculum
                              507, # Right-subiculum
                              502, # Right-CA1
                              500, # Right-CA3
                              506, # Right-CA4
                              510, # Right-GC-DC
                              511, # Right-HATA
                              503, # Right-fimbria
                              512, # Right-molecular-layer
                              505, # Right-fissure
                              513 # Right-Hipp-Tail
                              ]).astype(numpy.float32)

        gm_smooth = scipy.ndimage.gaussian_filter(gm_rois, sigma=voxsize)

        subcort_rois = group_rois([10,  # Left-Thalamus-Proper
                                   11,  # Left-Caudate
                                   12,  # Left-Putamen
                                   13,  # Left-Pallidum
                                   26,  # Left-Accumbens-area
                                   49,  # Right-Thalamus-Proper
                                   50,  # Right-Caudate
                                   51,  # Right-Putamen
                                   52,  # Right-Pallidum
                                   58   # Right-Accumbens-area 
                                   ]).astype(numpy.float32)

        subcort_smooth = scipy.ndimage.gaussian_filter(subcort_rois, sigma=voxsize)

        wm_rois = group_rois([7,   # Left-Cerebellum-White-Matter
                              16,  # Brain-Stem
                              175, # Medulla
                              174, # Pons
                              173, # MidBrain
                              28,  # Left-VentralDC
                              46,  # Right-Cerebellum-White-Matter
                              60,  # Right-VentralDC
                              85,  # Optic-Chiasm
                              192, # Corpus_Callosum
                              88,  # future_WMSA
                              250, # Fornix
                              251, # CC_Posterior
                              252, # CC_Mid_Posterior
                              253, # CC_Central
                              254, # CC_Mid_Anterior
                              255  # CC_Anterior
                              ]).astype(numpy.float32)

        wm_smooth = scipy.ndimage.gaussian_filter(wm_rois, sigma=voxsize)
        bs_mask = parc_data == 16 # Brain-Stem
        bs_vdc_dil = scipy.ndimage.morphology.binary_dilation(group_rois([16, # Brain-Stem
                                                                          175, # Medulla
                                                                          174, # Pons
                                                                          173, # MidBrain
                                                                          60, # Right-VentralDC
                                                                          28  # Left-VentralDC
                                                                         ]), iterations=2)
        bs_vdc_excl = numpy.logical_and(bs_vdc_dil, numpy.logical_not(group_rois([16, # Brain-Stem
                                                                                  7,  # Left-Cerebellum-White-Matter
                                                                                  46, # Right-Cerebellum-White-Matter
                                                                                  60, # Right-VentralDC
                                                                                  28, # Left-VentralDC
                                                                                  10, # Left-Thalamus-Proper
                                                                                  49, # Right-Thalamus-Proper
                                                                                  2,  # Left-Cerebral-White-Matter
                                                                                  41, # Right-Cerebral-White-Matter
                                                                                  0   # Nothing
                                                                                  ])))

        lbs = numpy.where((bs_mask).any(-1).any(0))[0][-1]-3

        parc_data_mask = parc_data > 0
        outer_csf = numpy.logical_and(
            numpy.logical_not(parc_data_mask),
            scipy.ndimage.morphology.binary_dilation(parc_data_mask))

        csf_rois = group_rois([4,  # Left-Lateral-Ventricle
                               5,  # Left-Inf-Lat-Vent
                               14, # 3rd-Ventricle
                               15, # 4th-Ventricle
                               24, # CSF
                               30, # Left-vessel
                               31, # Left-choroid-plexus
                               43, # Right-Lateral-Ventricle
                               44, # Right-Inf-Lat-Vent
                               62, # Right-vessel
                               63, # Right-choroid-plexus
                               72  # 5th-Ventricle
                            ])

        csf_smooth = scipy.ndimage.gaussian_filter(
            numpy.logical_or(csf_rois, outer_csf).astype(numpy.float32),
            sigma=voxsize)

        bs_roi = csf_smooth.copy()
        bs_roi[..., :lbs, :] = 0
        csf_smooth[..., lbs:, :] = 0
        wm_smooth[..., lbs:, :] = 0

        # add csf around brainstem and ventral DC to remove direct connection to gray matter
        csf_smooth[bs_vdc_excl] += gm_smooth[bs_vdc_excl]
        gm_smooth[bs_vdc_excl] = 0

        mask88 = parc_data == 88 # future_WMSA
        wm = wm_pve+wm_smooth-csf_smooth-subcort_smooth
        wm[wm > 1] = 1
        wm[wm < 0] = 0

        gm = gm_pve-wm_pve-wm-subcort_smooth+gm_smooth+bs_roi
        gm[gm < 0] = 0

        tt5 = numpy.concatenate([gm[..., numpy.newaxis],
                                subcort_smooth[..., numpy.newaxis],
                                wm[..., numpy.newaxis],
                                csf_smooth[..., numpy.newaxis],
                                numpy.zeros(parc.shape+(1,), dtype=numpy.float32)], 3)

        tt5 /= tt5.sum(-1)[..., numpy.newaxis]
        tt5[numpy.isnan(tt5)] = 0

        nibabel.save(nibabel.Nifti1Image(tt5.astype(numpy.float32), parc.get_affine()), target)
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
        op = ((numpy.mgrid[:5, :5, :5]-2.0)**2).sum(0) <= 4
        mask = scipy.ndimage.binary_closing(nii.get_data() > 0, op, iterations=2)
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
        # look for existing map store into preparation and link it so they are not created
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
        return Images((self.getPreparationImage('anat'), 'high resolution'))

    def isDirty(self):
        return Images((self.getImage('aparc_aseg'), 'parcellation  atlas'),
                        (self.getImage('wmparc'), 'wm parcellation'),
                        (self.getImage('anat', 'freesurfer'), 'anatomical'),
                        (self.getImage('rh_ribbon'), 'rh_ribbon'),
                        (self.getImage('lh_ribbon'), 'lh_ribbon'),
                        (self.getImage('norm'), 'norm'),
                        (self.getImage('mask'), 'freesurfer brain masks'),
                        (self.getImage("brainstem"), 'Brainstem label'),
                        (self.getImage("lhHipp"), 'Left Hippocampus label'),
                        (self.getImage("rhHipp"), 'Right Hippocampus label'),
                        (self.getImage('tt5'), '5tt'))

    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        anat = self.getImage('anat', 'freesurfer')  # Get freesurfer anat
        norm = self.getImage('norm')
        brainMask = self.getImage('mask')
        aparcAseg = self.getImage('aparc_aseg')
        wmparc = self.getImage('wmparc')
        tt5 = self.getImage('tt5')

        # Build qa images
        anatQa = self.plot3dVolume(anat, fov=brainMask)
        brainMaskQa = self.plot3dVolume(norm, edges=brainMask, fov=brainMask)
        aparcAsegQa = self.plot3dVolume(
                anat, segOverlay=aparcAseg, fov=aparcAseg)
        wmparcQa = self.plot3dVolume(anat, segOverlay=wmparc, fov=wmparc)
        tt5Qas = self.plot4dVolumeToFrames(tt5, fov=brainMask)

        qaImages = Images(
            (anatQa, 'High resolution anatomical image from Freesurfer'),
            (brainMaskQa, 'Brain mask on norm from Freesurfer'),
            (aparcAsegQa, 'Aparc aseg segmentation from Freesurfer'),
            (wmparcQa, 'White matter segmentation from Freesurfer'),
            (tt5Qas[0], 'Cortical grey matter'),
            (tt5Qas[1], 'Sub-cortical grey matter'),
            (tt5Qas[2], 'White matter'),
            (tt5Qas[3], 'CSF'),
            (tt5Qas[4], 'Pathological tissue'),
            )

        return qaImages
