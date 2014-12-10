from lib.generictask import GenericTask

__author__ = 'desmat'

class Results(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject)


    def implement(self):
        pass


    def meetRequirement(self):
        return True


    def isDirty(self):
        return True