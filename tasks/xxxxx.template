from lib.generictask import GenericTask

__author__ = 'desmat'

class Template(GenericTask):


    def __init__(self, subject):
        """A preset format, used as a starting point for developing a toad task

        Simply copy and rename this file:  cp xxxxx.template yourtaskname.py into the tasks folder.
            XX is simply a 2 digit number that represent the order the tasks will be executed.
            yourtaskname is any name at your convenience. the name must be lowercase
        Change the class name Template for Yourtaskname. Note the first letter of the name should be capitalized

        A directory called XX-yourtaskname will be create into the subject dir. A local variable self.workingDir will
        be initialize to that directory

        Args:
            subject: a Subject instance inherit by the subjectmanager.

        """

        GenericTask.__init__(self, subject)
        """Inherit from a generic Task.

        Args:
            subject: Subject instance inherit by the subjectmanager.

            Note that you may supply additional arguments to generic tasks.
            Exemple: if you provide Task.__init__(self, subject, foo, bar ...)
            toad will create an variable fooDir and barDir and then create an alias 'dependDir'
            that will point to the first additionnal argurments fooDir.

        """


    def implement(self):
        """Placeholder for the business logic implementation

        """
        pass


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