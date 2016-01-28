# -*- coding: utf-8 -*-
import os.path
from core.toad.generictask import GenericTask
from lib import mriutil


class Tractquerier(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'tensormrtrix', 'preparation', 'hardimrtrix', 'registration', 'tractographymrtrix', 'qa')
        self.setCleanupBeforeImplement(False)
        self.dirty = True


    def implement(self):
        # Load images
        dwi = self.getPreparationImage('dwi')
        hardiTck = self.getTractographymrtrixImage('dwi', 'hardi_prob', 'tck')
        if not hardiTck:
            hardiTck = self.getTractographymrtrixImage(
                    'dwi', 'tensor_prob', 'tck')
        norm = self.getRegistrationImage('norm', 'resample')
        aparcAsegResample = self.getRegistrationImage('aparc_aseg', 'resample')

        # conversion tck > trk
        #hardiTrk = self.__tck2trk(hardiTck, norm)

        # tract_querier
        qryFile = '/data/gosselin_n/cbedetti/TRAUMASOMMEIL/lpca_nocorrection/tract_queries_pont.qry'
        #self.__tractQuerier(hardiTrk, aparcAsegResample, qryFile)

        # tckmap
        tags = ['brainstem2thalamus', 'brainstem2ventraldc']
        self.__launchTckmap(tags, norm)

        self.dirty = False


    def __launchTckmap(self, tags, norm):
        tckmaps = []
        for tag in tags:
            tckmap = self.__tckmap(tag, norm)
            if tckmap:
                tckmaps.append(tckmap)
        self.__extractFiberStats(tckmaps)


    def __tck2trk(self, hardiTck, norm):
        trk = self.buildName(hardiTck, None, 'trk')
        #if os.path.isfile(trk):
        #target = self.getImage('dwi', 'hardi_prob', 'trk')
        #else:
        target = mriutil.tck2trk(hardiTck, norm , trk)
        return target


    def __tractQuerier(self, trk, atlas, qryFile):
        output = self.buildName(trk, None, 'trk')
        cmd = "tract_querier -t {} -a {} -q {} -o {}"
        cmd = cmd.format(trk, atlas, qryFile, output)
        self.launchCommand(cmd)


    def __tckmap(self, tag, norm):
        tck = self.getImage('dwi', tag, 'tck')
        tckmapCmd = "tckmap {} -template {} {}"
        tckstatsCmd ="tckstats {} | awk -F \" \" '{{print $6}}' | sed -n 2p > {}"
        if tck:
            tckMap = self.buildName(tck, 'map', 'nii.gz')
            cmd = tckmapCmd.format(tck, norm, tckMap)
            self.launchCommand(cmd)
            tckCount = self.buildName(tck, 'count', 'txt')
            cmd = tckstatsCmd.format(tck, tckCount)
            self.launchCommand(cmd)
            target = tckMap
        else:
            target = False
        return target


    def __extractFiberStats(self, tckmaps):
        # mrstats
        fa = self.getTensormrtrixImage('dwi', 'fa')
        rd = self.getTensormrtrixImage('dwi', 'rd')
        md = self.getTensormrtrixImage('dwi', 'md')
        ad = self.getTensormrtrixImage('dwi', 'ad')
        nufo = self.getHardimrtrixImage('dwi', 'nufo')
        #mrstatsCmd = "mrstats -mask {} -output mean {} > {}"
        fslmeantsCmd = "fslmeants -i {} -m {} -w | sed -n 1p > {}"
        for tckmap in tckmaps:
            if tckmap:
                for metric, postfix in zip([fa, rd, md, ad, nufo], ['fa', 'rd', 'md', 'ad', 'nufo']):
                    output = self.buildName(tckmap, postfix, 'txt')
                    #cmd = mrstatsCmd.format(tckmap, metric, output)
                    cmd = fslmeantsCmd.format(metric, tckmap, output)
                    self.launchCommand(cmd)


    def meetRequirement(self):
        """Validate if all requirements have been met prior to launch the task

        Returns:
            True if all requirement are meet, False otherwise
        """
        return True


    def isDirty(self):
        """Validate if this tasks need to be submit during the execution

        Returns:
            True if any expected file or resource is missing, False otherwise
        """
        return self.dirty
