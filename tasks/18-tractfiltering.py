# -*- coding: utf-8 -*-
import os
from core.toad.generictask import GenericTask
from lib import mriutil, util
from lib.images import Images


class TractFiltering(GenericTask):
    def __init__(self, subject):
        GenericTask.__init__(self, subject,
                             'preparation', 'registration', 'tensorfsl', 'tractquerier', 'qa')
        self.setCleanupBeforeImplement(False)
        self.dirty = True

        self.relativeOutDir = 'raw/outlier_cleaned_tracts'
        self.absOutDir = os.path.join(self.workingDir, self.relativeOutDir)

        target_queries = self.getPreparationImage('queries', None, 'qry')
        target_dict = self.getPreparationImage('tq_dict', None, 'qry')

        if not target_queries and not target_dict:
            self.defaultQuery = True
        else:
            self.defaultQuery = False

    def implement(self):

        mriutil.setWorkingDirTractometry(self.workingDir,
                                         self.getTractQuerierImages('dwi', None, 'trk'),
                                         [(self.getTensorFSLImage('dwi', 'fa'),
                                           'fsl_fa.nii.gz')])  # Set Working dir for tractometry

        configFile = self.__getConfigFile('configTractFiltering', 'configTractFiltering_default')

        mriutil.runTractometry(configFile, self.workingDir, self.workingDir)  # Run tractometry

    def isIgnore(self):
        return self.get("ignore")

    def meetRequirement(self):
        """Validate if all requirements have been met prior to launch the task
        Returns:
            True if all requirement are meet, False otherwise
        """
        if self.defaultQuery:
            return Images((self.getTractQuerierImage('dwi', 'corpus_callosum', 'trk'), 'CC'),
                          (self.getTractQuerierImage('dwi', 'cortico_spinal.left', 'trk'), 'CS_left'),
                          (self.getTractQuerierImage('dwi', 'cortico_spinal.right', 'trk'), 'CS_right'),
                          (self.getTractQuerierImage('dwi', 'inferior_fronto_occipital.left', 'trk'), 'IFO_left'),
                          (self.getTractQuerierImage('dwi', 'inferior_fronto_occipital.right', 'trk'), 'IFO_right'),
                          (
                          self.getTractQuerierImage('dwi', 'inferior_longitudinal_fasciculus.left', 'trk'), 'ILF_left'),
                          (self.getTractQuerierImage('dwi', 'inferior_longitudinal_fasciculus.right', 'trk'),
                           'ILF_right'),
                          (self.getTractQuerierImage('dwi', 'uncinate_fasciculus.left', 'trk'), 'UF_left'),
                          (self.getTractQuerierImage('dwi', 'uncinate_fasciculus.right', 'trk'), 'UH_right'))
        else:
            return Images((self.getTractQuerierImages('dwi', None, 'trk')))

    def isDirty(self):
        """Validate if this tasks need to be submit during the execution
        Returns:
            True if any expected file or resource is missing, False otherwise
        """
        if self.defaultQuery:
            return Images((self.getImage('dwi', 'corpus_callosum', 'trk', self.relativeOutDir), 'CC'),
                          (self.getImage('dwi', 'cortico_spinal.left', 'trk', self.relativeOutDir), 'CS_left'),
                          (self.getImage('dwi', 'cortico_spinal.right', 'trk', self.relativeOutDir), 'CS_right'),
                          (self.getImage('dwi', 'inferior_fronto_occipital.left', 'trk', self.relativeOutDir),
                           'IFO_left'),
                          (self.getImage('dwi', 'inferior_fronto_occipital.right', 'trk', self.relativeOutDir),
                           'IFO_right'),
                          (self.getImage('dwi', 'inferior_longitudinal_fasciculus.left', 'trk', self.relativeOutDir),
                           'ILF_left'),
                          (self.getImage('dwi', 'inferior_longitudinal_fasciculus.right', 'trk', self.relativeOutDir),
                           'ILF_right'),
                          (self.getImage('dwi', 'uncinate_fasciculus.left', 'trk', self.relativeOutDir), 'UF_left'),
                          (self.getImage('dwi', 'uncinate_fasciculus.right', 'trk', self.relativeOutDir), 'UH_right'))
        else:
            return not os.path.exists(self.absOutDir)

    def __getConfigFile(self, prefix, defaultFile):

        target = self.getPreparationImage(prefix, None, 'json')
        if target:
            util.symlink(target, self.buildName(target, None, 'json'))
        else:
            defaultFileName = '{}.json'.format(defaultFile)
            defaultFileLink = os.path.join(
                self.toadDir,
                "templates",
                "tractometry",
                defaultFileName,
            )
            target = defaultFileLink
            util.copy(defaultFileLink, self.workingDir, defaultFileName)
        return target

    def __buildNameTractfilteringOutputs(self):
        self.outputs = [self.getImage('dwi', 'corpus_callosum', 'trk', self.relativeOutDir),
                        self.getImage('dwi', 'cortico_spinal.left', 'trk', self.relativeOutDir),
                        self.getImage('dwi', 'cortico_spinal.right', 'trk', self.relativeOutDir),
                        self.getImage('dwi', 'inferior_fronto_occipital.left', 'trk', self.relativeOutDir),
                        self.getImage('dwi', 'inferior_fronto_occipital.right', 'trk', self.relativeOutDir),
                        self.getImage('dwi', 'inferior_longitudinal_fasciculus.left', 'trk', self.relativeOutDir),
                        self.getImage('dwi', 'inferior_longitudinal_fasciculus.right', 'trk', self.relativeOutDir),
                        self.getImage('dwi', 'uncinate_fasciculus.left', 'trk', self.relativeOutDir),
                        self.getImage('dwi', 'uncinate_fasciculus.right', 'trk', self.relativeOutDir)]

    def qaSupplier(self):
        """Create and supply images for the report generated by qa task
        """
        qaImages = Images()

        information = "Warning: due to storage restriction, streamlines were " \
                      "downsampled. Even if there is no difference in structural " \
                      "connectivity, you should be careful before computing any " \
                      "metrics along these streamlines.\n To run toad without this " \
                      "downsampling, please refer to the documentation."

        qaImages.setInformation(information)

        if self.defaultQuery:
            # get images
            norm = self.getRegistrationImage("norm", "resample")
            self.__buildNameTractfilteringOutputs()
            # images production
            tags = (
                (self.outputs[0],
                 'Corpus Callosum',
                 95, 60, 40, -80, 0, 160),
                (self.outputs[1],
                 'Corticospinal tract Left',
                 95, 80, 40, -90, 0, 160),
                (self.outputs[2],
                 'Corticospinal tract right',
                 95, 80, 40, -90, 0, 200),
                (self.outputs[3],
                 'Inferior Fronto Occipital tract left',
                 95, 80, 40, -90, 0, 90),
                (self.outputs[4],
                 'Inferior Fronto Occipital tract right',
                 95, 80, 40, -90, 0, -90),
                (self.outputs[5],
                 'inferior Longitudinal Fasciculus left',
                 95, 80, 40, -90, 0, 90),
                (self.outputs[6],
                 'Inferior Longitudinal Fasciculus right',
                 95, 80, 40, -90, 0, -90),
                (self.outputs[7],
                 'Uncinate Fasciculus left',
                 95, 80, 40, -90, 0, 90),
                (self.outputs[8],
                 'Uncinate Fasciculus right',
                 95, 80, 40, -90, 0, -90))

            for data, description, xSlice, ySlice, zSlice, xRot, yRot, zRot in tags:
                if data is not None:
                    imageQa = self.plotTrk(data, norm, None, xSlice, ySlice, zSlice, xRot, yRot, zRot)
                    qaImages.append((imageQa, description))
                else:
                    # Add message about QA
                    pass

        return qaImages
