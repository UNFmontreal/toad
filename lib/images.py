import os

class Images(object):

    def __init__(self, *args):
        self.__count = 0
        self.__images = []
        for arg in args:
            if isinstance(arg, tuple) and len(arg) == 2:
                self.__images.append(arg)
        self.__count=len(self.__images)

    def __iter__(self):
        return self

    def next(self):
        if self.__current > self.__count:
            raise StopIteration
        else:
            self.__current += 1
            return self.__current - 1

    def isEmpty(self):
        return len(self.__images) == 0

    def getData(self):
        return self.__images

    """
    class Counter:
        def __init__(self, low, high):
            self.current = low
            self.high = high

        def __iter__(self):
            return self

        def next(self): # Python 3: def __next__(self)
            if self.current > self.high:
                raise StopIteration
            else:
                self.current += 1
                return self.current - 1

    for c in Counter(3, 8):
        print c

    """



    def append(self, tupleItem):
        self.__images.append(tupleItem)
        self.__count += 1

    def extend(self, images):
        self.__images.append(images)
        self.__count += len(images)

    def insert(self, index, tupleItem):
        self.__images.insert(index, tupleItem)
        self.__count += 1


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

list.insert(i, x)
Insert an item at a given position. The first argument is the index of the element before which to insert, so a.insert(0, x) inserts at the front of the list, and a.insert(len(a), x) is equivalent to a.append(x).

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