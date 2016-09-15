# -*- coding: utf-8 -*-
import numpy
import nibabel
import dipy.core.gradients
import dipy.reconst.dti
import dipy.segment.mask
import dipy.reconst.dti

from core.toad.generictask import GenericTask
from lib.images import Images


__author__ = "Mathieu Desrosiers, Arnaud Bore"
__copyright__ = "Copyright (C) 2016, TOAD"
__credits__ = ["Mathieu Desrosiers", "Arnaud Bore"]

class TensorDipy(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'upsampling', 'registration', 'masking', 'qa')
        self.__fit = None

    def implement(self):
        dwi = self.getUpsamplingImage('dwi', 'upsample')
        bValsFile = self.getUpsamplingImage('grad', None, 'bvals')
        bVecsFile = self.getUpsamplingImage('grad', None, 'bvecs')
        mask = self.getRegistrationImage('mask', 'resample')

        fitMethod = self.get('fitMethod')  # Can be WLS, LS, NLLS or RT

        self.__fit = self.__produceTensors(dwi, bValsFile, bVecsFile, mask, fitMethod)

    def __produceTensors(self, source, bValsFile, bVecsFile, mask, fitMethod):
        self.info("Starting tensors creation from dipy on {}".format(source))
        dwiImage = nibabel.load(source)
        maskImage = nibabel.load(mask)
        maskData = maskImage.get_data()
        dwiData  = dwiImage.get_data()
        dwiData = dipy.segment.mask.applymask(dwiData, maskData)

        gradientTable = dipy.core.gradients.gradient_table(numpy.loadtxt(bValsFile), numpy.loadtxt(bVecsFile))
        self.info('WARNING: We need to flip the x direction due to MRtrix new way to extract bvecs')
        gradientTable.bvecs = gradientTable.bvecs * numpy.array([-1,1,1])

        if fitMethod.lower() is ('restore' or 'rt'):
            import dipy.denoise.noise_estimate as noise_estimate
            sigma = noise_estimate.estimate_sigma(dwiData)
            model = dipy.reconst.dti.TensorModel(gradientTable, fit_method=fitMethod, sigma=sigma)
        else:
            model = dipy.reconst.dti.TensorModel(gradientTable, fit_method=fitMethod)

        fit = model.fit(dwiData)  # Fitting method
        tensorsValues = dipy.reconst.dti.lower_triangular(fit.quadratic_form)
        correctOrder = [0, 1, 3, 2, 4, 5]
        tensorsValuesReordered = tensorsValues[:, :, :, correctOrder]
        tensorsImage = nibabel.Nifti1Image(tensorsValuesReordered.astype(numpy.float32), dwiImage.get_affine())
        nibabel.save(tensorsImage, self.buildName(source, "tensor"))

        nibabel.save(nibabel.Nifti1Image(fit.fa.astype(numpy.float32),
                                         dwiImage.get_affine()),
                                            self.buildName(source, "fa"))

        nibabel.save(nibabel.Nifti1Image(fit.ad.astype(numpy.float32),
                                         dwiImage.get_affine()),
                                            self.buildName(source, "ad"))
        nibabel.save(nibabel.Nifti1Image(fit.rd.astype(numpy.float32),
                                         dwiImage.get_affine()),
                                            self.buildName(source, "rd"))

        nibabel.save(nibabel.Nifti1Image(fit.md.astype(numpy.float32),
                                         dwiImage.get_affine()),
                                            self.buildName(source, "md"))

        nibabel.save(nibabel.Nifti1Image(fit.evecs[0].astype(numpy.float32),
                                         dwiImage.get_affine()),
                                             self.buildName(source, "v1"))

        nibabel.save(nibabel.Nifti1Image(fit.evecs[1].astype(numpy.float32),
                                         dwiImage.get_affine()),
                                            self.buildName(source, "v2"))

        nibabel.save(nibabel.Nifti1Image(fit.evecs[2].astype(numpy.float32),
                                         dwiImage.get_affine()),
                                            self.buildName(source, "v3"))

        faColor = numpy.clip(fit.fa, 0, 1)
        rgb = dipy.reconst.dti.color_fa(faColor, fit.evecs)
        nibabel.save(nibabel.Nifti1Image(numpy.array(255 * rgb, 'uint8'),
                                         dwiImage.get_affine()),
                                            self.buildName(source, "tensor_rgb"))
        return fit

    def isIgnore(self):
        return self.get("ignore")

    def meetRequirement(self):
        return Images((self.getUpsamplingImage('dwi', 'upsample'), "upsampled diffusion"),
                  (self.getUpsamplingImage('grad', None, 'bvals'), "gradient value bvals encoding file"),
                  (self.getUpsamplingImage('grad', None, 'bvecs'), "gradient vector bvecs encoding file"),
                  (self.getRegistrationImage('mask', 'resample'), 'brain  mask'))

    def isDirty(self):
        return Images((self.getImage("dwi", "tensor"), "dipy tensor"),
                     (self.getImage('dwi', 'v1'), "selected eigenvector 1"),
                     (self.getImage('dwi', 'v2'), "selected eigenvector 2"),
                     (self.getImage('dwi', 'v3'), "selected eigenvector 3"),
                     (self.getImage('dwi', 'fa'), "fractional anisotropy"),
                     (self.getImage('dwi', 'md'), "mean diffusivity MD"),
                     (self.getImage('dwi', 'ad'), "selected eigenvalue(s) AD"),
                     (self.getImage('dwi', 'rd'), "selected eigenvalue(s) RD"))
                 #"apparent diffusion coefficient" : self.getImage(self.workingDir, 'dwi', 'adc')}


    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        qaImages = Images()
        softwareName = 'dipy'

        #Set information
        information = "Fit method: {}".format(self.get('fitMethod'))
        qaImages.setInformation(information)

        #  mask image
        mask = self.getRegistrationImage('mask', 'resample')

        #  Produce tensor ellipsoids image
        dwi = self.getUpsamplingImage('dwi', 'upsample')
        cc = self.getMaskingImage('aparc_aseg', ['253','mask'])
        ellipsoidsQa = self.plotReconstruction(
                self.__fit, mask, cc, 'tensor', dwi)
        qaImages.append((
            ellipsoidsQa,
            'Coronal slice of tensor ellipsoids in the Corpus Callosum'))

        #  Build qa images
        tags = (
            #(['tensor', 'rgb'], 'RGB map'),
            ('fa', 0.7, 'Fractional anisotropy'),
            ('ad', 0.005, 'Axial Diffusivity'),
            ('md', 0.005, 'Mean Diffusivity'),
            ('rd', 0.005, 'Radial Diffusivity'),
            )

        for postfix, vmax, description in tags:
            image = self.getImage('dwi', postfix)
            if image:
                imageQa = self.plot3dVolume(
                        image, fov=mask, vmax=vmax,
                        colorbar=True, postfix=softwareName)
                qaImages.append((imageQa, description))

        return qaImages
