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

        #Copy css & js
        css = os.path.join(
                self.toadDir, 'templates', 'files',
                self.config.get('qa', 'css'))
        util.copy(css, self.workingDir, 'style.css')

        jQuery = os.path.join(
                self.toadDir, 'templates', 'files', self.get('qa', 'jquery'))
        util.copy(jQuery, self.workingDir, 'jquery.js')

        #Create menu.html only for tasks with implemented QA
        menuTemplate = os.path.join(
                self.toadDir, 'templates', 'files', 'qa.menu.tpl')
        util.copy(menuTemplate, self.workingDir, 'menu.html')

        #Create index.html
        tags = {'subject':self.subjectName}
        self.createTaskHtml(tags, 'index.html')


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
