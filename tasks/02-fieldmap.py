from generic.generictask import GenericTask

__author__ = 'desmat'

class Fieldmap(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, "preparation", "parcellation")


    def implement(self):
        """Placeholder for the business logic implementation

        """
        print "this is o.k."
        import sys
        sys.exit()



    def meetRequirement(self):
        """Validate if all requirements have been met prior to launch the task

        Returns:
            True if all requirement are meet, False otherwise
        """
        return True


    def isDirty(self):
        """Validate if this tasks need to be submit during the execution

        Returns:
            True if any expected file or resource is missing, False otherwise
        """
        return True