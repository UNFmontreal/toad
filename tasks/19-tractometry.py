# -*- coding: utf-8 -*-
import os
from core.toad.generictask import GenericTask
from lib import mriutil, util
from lib.images import Images


class Tractometry(GenericTask):
    def __init__(self, subject):
        GenericTask.__init__(
            self, subject, 'backup', 'tensorfsl', 'tensormrtrix', 'tensordipy',
            'tractfiltering', 'qa')
        self.setCleanupBeforeImplement(False)
        self.dirty = True


    def implement(self):
        pass
        mriutil.setWorkingDirTractometry(self.workingDir,
                                         self.getTractFilteringImages('dwi', None, 'trk','raw/bundles/'),
                                         self.__buildListMetrics())


        configFile = self.__getConfigFile('configTractometry', 'configTractometry_default')

        mriutil.runTractometry(configFile, self.workingDir, self.workingDir)


    def isIgnore(self):
        return self.get("ignore")


    def meetRequirement(self):
        """Validate if all requirements have been met prior to launch the task
        Returns:
            True if all requirement are meet, False otherwise
        """
        target_queries = self.getBackupImage('queries', None, 'qry')
        target_dict = self.getBackupImage('tq_dict', None, 'qry')

        outDir = 'raw/outlier_cleaned_tracts'

        if not target_queries and not target_dict:
            return Images((self.getTractFilteringImage('dwi', 'corpus_callosum', 'trk', outDir), 'CC'),
                           (self.getTractFilteringImage('dwi', 'cortico_spinal.left', 'trk', outDir), 'CS_left'),
                           (self.getTractFilteringImage('dwi', 'cortico_spinal.right', 'trk', outDir), 'CS_right'),
                           (self.getTractFilteringImage('dwi', 'inferior_fronto_occipital.left', 'trk', outDir), 'IFO_left'),
                           (self.getTractFilteringImage('dwi', 'inferior_fronto_occipital.right', 'trk', outDir), 'IFO_right'),
                           (self.getTractFilteringImage('dwi', 'inferior_longitudinal_fasciculus.left', 'trk', outDir), 'ILF_left'),
                           (self.getTractFilteringImage('dwi', 'inferior_longitudinal_fasciculus.right', 'trk', outDir), 'ILF_right'),
                           (self.getTractFilteringImage('dwi', 'uncinate_fasciculus.left', 'trk', outDir), 'UF_left'),
                           (self.getTractFilteringImage('dwi', 'uncinate_fasciculus.right', 'trk', outDir), 'UH_right'))
        else:
            return Images((self.getTractFilteringImage('dwi', None, 'trk', outDir)))

    def isDirty(self):
        """Validate if this tasks need to be submit during the execution
        Returns:
            True if any expected file or resource is missing, False otherwise
        """
        """Validate if this tasks need to be submit during the execution
        Returns:
            True if any expected file or resource is missing, False otherwise
        """
        target_queries = self.getBackupImage('queries', None, 'qry')
        target_dict = self.getBackupImage('tq_dict', None, 'qry')

        outDir = 'raw/histograms'

        if not target_queries and not target_dict:
            return not os.path.exists(outDir)
#            return Images((self.getImage('dwi', 'corpus_callosum', 'trk', outDir),'CC'),
#                           (self.getImage('dwi', 'cortico_spinal.left', 'trk', outDir),'CS_left'),
#                           (self.getImage('dwi', 'cortico_spinal.right', 'trk', outDir),'CS_right'),
#                           (self.getImage('dwi', 'inferior_fronto_occipital.left', 'trk', outDir),'IFO_left'),
#                           (self.getImage('dwi', 'inferior_fronto_occipital.right', 'trk', outDir),'IFO_right'),
#                           (self.getImage('dwi', 'inferior_longitudinal_fasciculus.left', 'trk', outDir),'ILF_left'),
#                           (self.getImage('dwi', 'inferior_longitudinal_fasciculus.right', 'trk', outDir),'ILF_right'),
#                           (self.getImage('dwi', 'uncinate_fasciculus.left', 'trk', outDir),'UF_left'),
#                           (self.getImage('dwi', 'uncinate_fasciculus.right', 'trk', outDir),'UH_right'))
        else:
            outDir = os.path.join(self.workingDir, outDir)
            return not os.path.exists(outDir)

    def __buildListMetrics(self):
        return [(self.getTensorFSLImage('dwi', 'fa'),'fsl_fa.nii.gz'),
                (self.getTensorFSLImage('dwi', 'md'),'fsl_md.nii.gz'),
                (self.getTensorFSLImage('dwi', 'ad'),'fsl_ad.nii.gz'),
                (self.getTensorFSLImage('dwi', 'md'),'fsl_rd.nii.gz'),
                (self.getTensorDIPYImage('dwi', 'fa'),'dipy_fa.nii.gz'),
                (self.getTensorDIPYImage('dwi', 'md'),'dipy_md.nii.gz'),
                (self.getTensorDIPYImage('dwi', 'ad'),'dipy_ad.nii.gz'),
                (self.getTensorDIPYImage('dwi', 'md'),'dipy_rd.nii.gz'),
                (self.getTensorMRTRIXImage('dwi', 'fa'),'mrtrix_fa.nii.gz'),
                (self.getTensorMRTRIXImage('dwi', 'md'),'mrtrix_md.nii.gz'),
                (self.getTensorMRTRIXImage('dwi', 'ad'),'mrtrix_ad.nii.gz'),
                (self.getTensorMRTRIXImage('dwi', 'md'),'mrtrix_rd.nii.gz')]

    def __getConfigFile(self, prefix, defaultFile):

        target = self.getBackupImage(prefix, None, 'json')
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
            self.defaultQuery = True
        return target

#    def qaSupplier(self):
#        """Create and supply images for the report generated by qa task
#
#        """
#        qaImages = Images()
#
#        return qaImages
