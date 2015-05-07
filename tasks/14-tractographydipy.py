from core.generictask import GenericTask

__author__ = 'desmat'

class TractographyDipy(GenericTask):

    def __init__(self, subject):

        GenericTask.__init__(self, subject)


    def implement(self):
        pass


    def isIgnore(self):
        return self.get("ignore").lower() in "true"


    def meetRequirement(self):
        return True


    def isDirty(self):
        return True
