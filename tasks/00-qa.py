# -*- coding: utf-8 -*-
import os

from core.toad.generictask import GenericTask
from lib.images import Images
from lib import util


__author__ = "Christophe Bedetti"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Christophe Bedetti","Mathieu Desrosiers"]


class QA(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'backup')
        self.setCleanupBeforeImplement(False)
        self.subjectName = subject.getName()

    def implement(self):

        if not os.path.exists(self.qaImagesDir):
            os.makedirs(self.qaImagesDir)

        #Copy logo
        logoName = self.config.get('qa', 'logo')
        logoLink = os.path.join(
                self.toadDir, 'templates', 'files', logoName)
        util.copy(logoLink, self.qaImagesDir, logoName)

        #Copy menu, css & js
        styleFiles = ('menu', 'css', 'jquery', 'js')
        for tag in styleFiles:
            fileName = self.config.get('qa', tag)
            fileLink = os.path.join(
                    self.toadDir, 'templates', 'files', fileName)
            util.copy(fileLink, self.workingDir, fileName)

        #Create index.html
        self.createTaskHtml(
                {'parseHtmlTables':'<a href="./metho.html">Methodology example</a>'},
                'index.html')

        #Create metho.html
        from jinja2 import Environment, FileSystemLoader
        templateDir = os.path.join(
                self.toadDir, 'templates', 'files')
        jinja2Env = Environment(loader=FileSystemLoader(templateDir), trim_blocks=True)
        tpl = jinja2Env.get_template('metho.tpl')
        tags_metho = self.__getTags()
        htmlCode = tpl.render(**tags_metho)
        util.createScript('metho.html', htmlCode)


    def __configGet(self, section, key):
        try:
            value = self.config.get(section, key)
        except:
            value = None
        return value


    def __getTags(self):
        tags = {}

        # ----------------------------------------------------
        # PREPARATION SECTION
        # ----------------------------------------------------
        denoisingKeys = ['number_array_coil']
        for key in denoisingKeys:
            tags[key] = self.__configGet('denoising', key)

        methodologyKeys = [
                'manufacturer', 'magneticfieldstrenght', 'mrmodel',
                't1_tr', 't1_te', 't1_ti', 't1_flipangle', 't1_fov', 't1_mat',
                't1_slices', 't1_voxelsize', 'dwi_tr', 'dwi_te', 'dwiflipangle',
                'dwi_voxelsize', 'dwi_numdirections', 'dwi_bvalue']
        for key in methodologyKeys:
            tags[key] = self.__configGet('methodology', key)

        # ----------------------------------------------------
        # PREPROCESSING
        # ----------------------------------------------------
        # Add the FSL references
        refs = [self.__configGet('references', 'fsl')]
        tags['fsl_vers']= None # parser.get('', '')
        tags['fsl_ref'] = "[{}]".format(len(refs))

        # Prepare the text for the denoising section
        if self.config.get('denoising', 'ignore') in ['True', 'true']:
            tags['denoising'] = False
        else:
            tags['denoising'] = True
            method = self.config.get('denoising', 'algorithm')
            tags['algorithm'] = method
            refs.append(self.__configGet('references', method))
            tags['denoising_ref'] = len(refs)

        # Prepare the text for the correction section
        if self.config.get('correction', 'ignore') in ['True', 'true']:
            tags['correction'] = False
        else:
            tags['correction'] = True
            tags['correction_method'] = None

        # Add the trilinear interpolation references
        refs.append(self.__configGet('references', 'tri1'))
        refs.append(self.__configGet('references', 'tri2'))
        tags['tri_ref']= "[{}, {}]".format(len(refs)-1, len(refs))

        # Add the FDT reference
        refs.append(self.__configGet('references', 'fdt'))
        tags['fdt_ref']= "[{}]".format(len(refs))

        # Add Freesurfer segmentation/label references
        refs.append(self.__configGet('references', 'segfreesurfer'))
        refs.append(self.__configGet('references', 'labfreesurfer'))
        tags['seg_ref']= "[{}, {}]".format(len(refs)-1, len(refs))

        refTxt = []
        for idx, ref in enumerate(refs):
            refTxt.append("<p>[{}] {}</p></ br>".format(idx+1, ref))
        tags['references']= refTxt

        return tags


    def meetRequirement(self, result=True):
        """
        """
        return result


    def isDirty(self):
        """Validate if this tasks need to be submit for implementation

        """
        return Images(
                (os.path.join(self.workingDir, 'index.html'), 'QA index.html'),
                (os.path.join(self.workingDir, self.config.get('qa', 'jquery')), 'Jquery library'))
