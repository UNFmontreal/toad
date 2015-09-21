# -*- coding: utf-8 -*-
__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class Prefix(object):

    def __init__(self, name, description, value):
        self.__name = name
        self.__description = description
        self.__value = value

    def __eq__(self, other):
        return self.__name == other.getName()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
            return "Prefix:name={},description={},value={}\n".format(self.__name, self.__description, self.__value)

    def getName(self):
        return self.__name

    def getDescription(self):
        return self.__description

    def getValue(self):
        return self.__value

    def setValue(self, value):
        self.__value = value