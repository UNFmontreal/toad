from core.toad.generictask import GenericTask
__author__ = "Your_name"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Your_name", "Mathieu Desrosiers"]


class Atlasregistration(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject)

    def implement(self):
        brodmann = self.getParcellationImage("brodmann")
        aal2 = self.getParcellationImage("aal2")
        networks7 = self.getParcellationImage("networks7")

    def meetRequirement(self):
        return True


    def isDirty(self):
        return True
