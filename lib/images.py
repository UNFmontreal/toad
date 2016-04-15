# -*- coding: utf-8 -*-
import os

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class Images(object):

    def __init__(self, *args):
        self.__information = ''
        self.__images = []
        for arg in args:
            if isinstance(arg, tuple) and len(arg) == 2:
                self.__images.append(arg)
            elif isinstance(arg, str):
                self.__images.append((arg, arg))
            else:
                self.__images.append((False, False))


    def __repr__(self):
        string = ""
        for image, description in self.__images:
            string += "\"{}\"--> {}\n".format(description, image)
        return string

    def __iter__(self):
        return iter(self.__images)

    def isEmpty(self):
        return len(self.__images) == 0

    def getData(self):
        return self.__images

    def setInformation(self, information):
        self.__information = information

    def getInformation(self):
        return self.__information

    def size(self):
        return len(self.__images)

    def append(self, tupleItem):
        self.__images.append(tupleItem)

    def extend(self, images):
        self.__images.extend(images)

    def insert(self, index, tupleItem):
        self.__images.insert(index, tupleItem)

    def isSomeImagesMissing(self):
        """Iterate over a structure to see if all image exists

        This function is an helper for isDirty and meetRequirement method
        The key represent a description of the image, the value is a call to getImage.

        Args:
            structure: a list of tuples or a tuple.
                    The tuples should have 2 elements: first element should be an image, second a description
        Returns:
            True if some image do not exists, False otherwise
        """
        result = False
        for image, description in self.__images:
            if not image:
                result = True
            else:
                if not os.path.exists(image):
                    result = True
        return result


    def isAllImagesExists(self):
        """Iterate over a dictionary of getImage to see if all image exists

        This function is an helper for isDirty and meetRequirement method
        The key represent a description of the image, the value is a call to getImage.

        Args:
            structure: a list of tuples.
                    The tuples should have 2 elements: first element should be an image, second a description

        Returns:
            True if all images in the structure exists, False otherwise
        """
        return not self.isSomeImagesMissing()


    def isNoImagesExists(self):
        return not self.isAtLeastOneImageExists()


    def isAtLeastOneImageExists(self):
        for image, description in self.__images:
            if image:
                return True
        return False



"""
list.remove(x)
Remove the first item from the list whose value is x. It is an error if there is no such item.

list.pop([i])
Remove the item at the given position in the list, and return it. If no index is specified, a.pop() removes and returns the last item in the list. (The square brackets around the i in the method signature denote that the parameter is optional, not that you should type square brackets at that position. You will see this notation frequently in the Python Library Reference.)

list.index(x)
Return the index in the list of the first item whose value is x. It is an error if there is no such item.

list.count(x)
Return the number of times x appears in the list.

list.sort(cmp=None, key=None, reverse=False)
Sort the items of the list in place (the arguments can be used for sort customization, see sorted() for their explanation).

list.reverse()
Reverse the elements of the list, in place.

"""
