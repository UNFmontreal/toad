# -*- coding: utf-8 -*-

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class SequenceMRI(object):

    def __init__(self, name, directory):
        self.__name = name
        self.__directory = directory
        self.__prefix = None


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
        return self.__directory

    def getPrefix(self):
        return self.__prefix

    def setPrefix(self, prefix):
        self.__prefix = prefix