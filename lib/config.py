import ConfigParser
import os


class Config(object):


    def __init__(self, arguments=None):
        """Configuration mechanism for the toad pipeline

        The purpose of this class is to provide a single configuration mechanism
        that will handle all options and configurations that may be need during a
        toad execution.

        Args
            arguments: arguments specified in command line by the users.

        """
        if(arguments is not None):
            self.config = self.buildConfiguration(arguments)


    def buildConfiguration(self, arguments):
        """Read various config files and return configurations value as a dictionary

        First read master config file: etc/config.cfg
        Second, Process .toad.cfg in the user home directory
        Third, Process any users input file enter as the command line option -c

        Args:
            arguments: an ArgumentParser containing command line invocation

        Returns:
            a RawConfigParser dictionaries containing configurations

        """
        config = ConfigParser.ConfigParser()
        configFiles = ["{}/etc/config.cfg".format(arguments.toadDir)]
        config.read(configFiles)

        configFiles = ['~/.toad.cfg',
                       "{}/config.cfg".format(arguments.studyDir)]

        if arguments.subject and isinstance(arguments.subject, basestring):
            subjectFile = "{}/config.cfg".format(arguments.subject)
            if os.path.exists(subjectFile):
                configFiles.append(subjectFile)
            subjectFile = "{}/config.cfg".format(os.path.join(arguments.subject, "00-backup"))
            if os.path.exists(subjectFile):
                configFiles.append(subjectFile)

        config.read(configFiles)

        #parse command line arguments in the config file
        config.add_section('arguments')
        config.set('arguments', 'toad_dir', arguments.toadDir)
        config.set('arguments', 'studyDir', arguments.studyDir)

        #add local options to config file
        if arguments.local:
            config.set('arguments', 'local', 'True')
        else:
            config.set('arguments', 'local', 'False')

        if arguments.reinitialize:
            config.set('arguments', 'reinitialize', 'True')
        else:
            config.set('arguments', 'reinitialize', 'False')

        if arguments.skipValidation:
            config.set('arguments', 'validation', 'False')
        else:
            config.set('arguments', 'validation', 'True')

        if arguments.noPrompt:
            config.set('arguments', 'prompt', 'False')
        else:
            config.set('arguments', 'prompt', 'True')

        if arguments.subject and isinstance(arguments.subject, basestring):
            config.set('arguments', 'subjectDir', arguments.subject)

        #Should be safe to overwrite value base on command line arguments here
        if arguments.emergency:
            config.set('general', 'nb_threads', 'unlimited')

        return config


    def getConfig(self):
        """Return this ConfigParser structures

        Returns:
             a config ConfigParser object

        """
        return self.config
