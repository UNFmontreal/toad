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
        self.createTaskHtml({}, 'index.html')


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
