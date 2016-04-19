# -*- coding: utf-8 -*-
import os
from core.toad.generictask import GenericTask
from lib import mriutil, util
from lib.images import Images


class Tractquerier(GenericTask):
    def __init__(self, subject):
        GenericTask.__init__(
            self, subject,
            'backup', 'upsampling', 'registration', 'atlasregistration',
            'tractographymrtrix', 'qa')
        self.setCleanupBeforeImplement(False)
        self.dirty = True

    def implement(self):

        self.defaultQuery = False
        dwi = self.getUpsamplingImage('dwi', 'upsample')
        nbDirections = mriutil.getNbDirectionsFromDWI(dwi)

        # Load tractography
        self.tractographyTrk = self.__getTractography(nbDirections)

        ### Get atlas to refere to
        atlasResample = self.__getAtlas()

        ### Find dictionnary
        qryDict = self.__getTractquerierFile('tq_dict', 'tq_dict_freesurfer')

        ### Find query
        qryFile = self.__getTractquerierFile('queries', 'queries_freesurfer')

        # Launch tract_querier
        self.__tractQuerier(self.tractographyTrk, atlasResample, self.workingDir, qryFile)
        self.dirty = False

    def __getTractography(self, nbDirections):
        if nbDirections <= 45:
            postfixTractography = 'tensor_prob'
        else:
            postfixTractography = 'hardi_prob'
        return self.getTractographymrtrixImage('dwi', postfixTractography, 'trk')


    def __getAtlas(self):
        atlas = self.get('atlas')
        target = self.getAtlasRegistrationImage(atlas, 'resample')
        if not target:
            target = self.getRegistrationImage(atlas, 'resample')
        else:
            self.info("No atlas resample found in tractquerier task")
        return target


    def __getTractquerierFile(self, prefix, defaultFile):
        target = self.getBackupImage(prefix, None, 'qry')
        if target:
            util.symlink(target, self.buildName(target, None, 'qry'))
        else:
            defaultFileName = '{}.qry'.format(defaultFile)
            defaultFileLink = os.path.join(
                self.toadDir,
                "templates",
                "tract_queries",
                defaultFileName,
            )
            target = defaultFileLink
            util.copy(defaultFileLink, self.workingDir, defaultFileName)
            self.defaultQuery = True
        return target


    def __tractQuerier(self, trk, atlas, qryDict, qryFile):
        target = self.buildName(trk, None, 'trk')
        cmd = "tract_querier -t {} -a {} -I {} -q {} -o {}"
        cmd = cmd.format(trk, atlas, qryDict, qryFile, target)
        self.launchCommand(cmd)
        return target


    def __buildNameTractQuerierOutputs(self):
        self.queries = [self.getImage('dwi', 'corpus_callosum', 'trk'),
                        self.getImage('dwi', 'cortico_spinal.left', 'trk'),
                        self.getImage('dwi', 'cortico_spinal.right', 'trk'),
                        self.getImage('dwi', 'inferior_fronto_occipital.left', 'trk'),
                        self.getImage('dwi', 'inferior_fronto_occipital.right', 'trk'),
                        self.getImage('dwi', 'inferior_longitudinal_fasciculus.left', 'trk'),
                        self.getImage('dwi', 'inferior_longitudinal_fasciculus.right', 'trk'),
                        self.getImage('dwi', 'uncinate_fasciculus.left', 'trk'),
                        self.getImage('dwi', 'uncinate_fasciculus.right', 'trk')]


    def isIgnore(self):
        return self.get("ignore")


    def meetRequirement(self):
        """Validate if all requirements have been met prior to launch the task
        Returns:
            True if all requirement are meet, False otherwise
        """

        images = Images()

        dwi = self.getUpsamplingImage('dwi', 'upsample')
        nbDirections = mriutil.getNbDirectionsFromDWI(dwi)

        # Load tractography
        if nbDirections <= 45:
            postfixTractography = 'tensor_prob'
        else:
            postfixTractography = 'hardi_prob'

        Images((self.getTractographymrtrixImage('dwi', postfixTractography, 'trk'),'Tractography file'),
                (self.__getAtlas(),'Atlas'))

        return images


    def isDirty(self):
        """Validate if this tasks need to be submit during the execution
        Returns:
            True if any expected file or resource is missing, False otherwise
        """

        dwi = self.getUpsamplingImage('dwi', 'upsample')
        nbDirections = mriutil.getNbDirectionsFromDWI(dwi)

        # Which tractography
        if nbDirections <= 45:
            postfixTractography = 'tensor_prob'
        else:
            postfixTractography = 'hardi_prob'

        target_queries = self.getBackupImage('queries', None, 'qry')
        target_dict = self.getBackupImage('tq_dict', None, 'qry')

        if not target_queries and not target_dict:
            return Images((self.getImage('dwi', postfixTractography+'_corpus_callosum', 'trk'),'CC'),
                           (self.getImage('dwi', postfixTractography+'_cortico_spinal.left', 'trk'),'CS_left'),
                           (self.getImage('dwi', postfixTractography+'_cortico_spinal.right', 'trk'),'CS_right'),
                           (self.getImage('dwi', postfixTractography+'_inferior_fronto_occipital.left', 'trk'),'IFO_left'),
                           (self.getImage('dwi', postfixTractography+'_inferior_fronto_occipital.right', 'trk'),'IFO_right'),
                           (self.getImage('dwi', postfixTractography+'_inferior_longitudinal_fasciculus.left', 'trk'),'ILF_left'),
                           (self.getImage('dwi', postfixTractography+'_inferior_longitudinal_fasciculus.right', 'trk'),'ILF_right'),
                           (self.getImage('dwi', postfixTractography+'_uncinate_fasciculus.left', 'trk'),'UF_left'),
                           (self.getImage('dwi', postfixTractography+'_uncinate_fasciculus.right', 'trk'),'UH_right'))

        return True


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
            self.__buildNameTractQuerierOutputs()
            print self.queries
            # images production
            tags = (
                (self.queries[0],
                 'Corpus Callosum',
                 95, 60, 40, -80, 0, 160),
                (self.queries[1],
                 'Corticospinal tract Left',
                 95, 80, 40, -90, 0, 160),
                (self.queries[2],
                 'Corticospinal tract right',
                 95, 80, 40, -90, 0, 200),
                (self.queries[3],
                 'Inferior Fronto Occipital tract left',
                 95, 80, 40, -90, 0, 90),
                (self.queries[4],
                 'Inferior Fronto Occipital tract right',
                 95, 80, 40, -90, 0, -90),
                (self.queries[5],
                 'inferior Longitudinal Fasciculus left',
                 95, 80, 40, -90, 0, 90),
                (self.queries[6],
                 'Inferior Longitudinal Fasciculus right',
                 95, 80, 40, -90, 0, -90),
                (self.queries[7],
                 'Uncinate Fasciculus left',
                 95, 80, 40, -90, 0, 90),
                (self.queries[8],
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
