# -*- coding: utf-8 -*-
import os

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]

#A Sequence may contain dicoms images, but may also contains only metadata for speed purpose

class SequenceMRI(object):

    def __init__(self, name, directory, nbImages):
        self.__name = name
        self.__directory = directory
        self.__nbImages = nbImages
        self.__prefix = None

    def __eq__(self, other):
        return self.getName() == other.getName()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if self.__prefix is None:
            return "SequenceMRI:name={},directory={}\n".format(self.__name, self.__directory)
        else:
            return "SequenceMRI:name={},directory={},prefix={}\n".format(self.__name, self.__directory, self.__prefix)

    def getName(self):
        return self.__name

    def getDirectory(self):
        return "'{}'".format(self.__directory.replace("'", "'\\''"))

    def getPrefix(self):
        return self.__prefix

    def setPrefix(self, prefix):
        self.__prefix = prefix

    def getComparable(self):
        return "{}{}".format(self.__name, self.__nbImages)
