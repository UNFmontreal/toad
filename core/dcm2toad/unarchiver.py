# -*- coding: utf-8 -*-
import tempfile
import tarfile
import zipfile

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class Unarchiver(object):

    def __init__(self, fileName):
        self.__fileName = fileName

    def getFileName(self):
        return self.__fileName

    def isArchive(self):
        """return "tar", "zip" or empty string"""
        if (self.__fileName.endswith('.tar.gz') or self.__fileName.endswith('.tgz')) and tarfile.is_tarfile(self.__fileName):
            return True
        elif self.__fileName.endswith('.zip') and zipfile.is_zipfile(self.__fileName):
            return True

        return False

    def type(self):
        if tarfile.is_tarfile(self.__fileName):
            return "Tar"
        elif zipfile.is_zipfile(self.__fileName):
            return "Zip"
        return None


    def unArchive(self):
        temporaryDirectory = tempfile.mkdtemp()
        print "Unarchiving {} tarfile, This may take a while...".format(self.__fileName)
        if self.type() is "Tar":
            archive = tarfile.open(self.__fileName, 'r')
        elif self.type() is "Zip":
            archive = zipfile.ZipFile(self.__fileName, 'r')
        archive.extractall(temporaryDirectory)
        archive.close()
        return temporaryDirectory
