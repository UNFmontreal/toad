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
        self.__subject = subject

    def implement(self):

        mainTemplate = os.path.join(
                self.toadDir, 'templates', 'files', 'qa.main.tpl')
        imagesDir = os.path.join(
                self.workingDir, self.get('qa', 'images_dir'))

        if not os.path.exists(imagesDir):
            os.makedirs(imagesDir)

        #Copy logo
        logoLink = os.path.join(
                self.toadDir, 'templates', 'files', 'qa_logo.png')
        util.copy(logoLink, imagesDir, 'qa_logo.png')

        #Copy style.css
        styleTemplate = os.path.join(
                self.toadDir, 'templates', 'files', 'qa.style.tpl')
        jQuery = os.path.join(
                self.toadDir, 'templates', 'files',
                self.get('general', 'jquery'))

        util.copy(styleTemplate, self.workingDir, 'style.css')
        util.copy(jQuery, self.workingDir, 'jquery.js')

        #Create menu.html only for tasks with implemented QA
        menuTemplate = os.path.join(
                self.toadDir, 'templates', 'files', 'qa.menu.tpl')
        util.copy(menuTemplate, self.workingDir, 'menu.html')

        #Create index.html
        tags = {
            'subject':self.__subject.getName(),
            'taskInfo':'',
            'parseHtmlTables':'',
            'parseVersionTables':'',
            }
        htmlCode = self.parseTemplate(tags, mainTemplate)
        util.createScript('index.html', htmlCode)


    def meetRequirement(self, result=True):
        """
        """
        return result


    def isDirty(self):
        """Validate if this tasks need to be submit for implementation

        """
        return Images(
                (os.path.join(self.workingDir, 'index.html'), 'QA index.html'),
                (os.path.join(self.workingDir, 'jquery.js'), 'Jquery library'))
