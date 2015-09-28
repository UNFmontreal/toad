# -*- coding: utf-8 -*-
import ConfigParser
import os

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class Config(object):


    def __init__(self, arguments=None):
        """Configuration mechanism for the toad pipeline

        The purpose of this class is to provide a single configuration mechanism
        that will handle all options and configurations that may be need during a
        toad execution.

        Args
            arguments: arguments specified in command line by the users.

        """
        if arguments is not None:
            self.config = self.__buildConfiguration(arguments)


    def __buildConfiguration(self, arguments):
        """Read various config files and return configurations value as a dictionary

        Args:
            arguments: an ArgumentParser containing command line invocation

        Returns:
            a RawConfigParser dictionaries containing configurations

        """

        config = ConfigParser.ConfigParser()
        config.read(self.__getConfigFiles(arguments))


        #parse command line arguments in the config file
        config.add_section('arguments')
        config.set('arguments', 'toad_dir', arguments.toadDir)

        if arguments.stopBeforeTask and isinstance(arguments.stopBeforeTask, basestring):
            config.set('arguments', 'stop_before_task', arguments.stopBeforeTask)

        #add local options to config file
        if arguments.local:
            config.set('arguments', 'local', 'True')
        else:
            config.set('arguments', 'local', 'False')

        if arguments.reinitialize:
            config.set('arguments', 'reinitialize', 'True')
        else:
            config.set('arguments', 'reinitialize', 'False')

        if arguments.debug:
            config.set('arguments', 'debug', 'True')
        else:
            config.set('arguments', 'debug', 'False')

        if arguments.skipValidation:
            config.set('arguments', 'validation', 'False')
        else:
            config.set('arguments', 'validation', 'True')

        if arguments.noPrompt:
            config.set('arguments', 'prompt', 'False')
        else:
            config.set('arguments', 'prompt', 'True')

        if arguments.task:
            config.set('arguments', 'custom_tasks', arguments.task)
        else:
            config.set('arguments', 'custom_tasks', None)

        if arguments.subject and isinstance(arguments.subject, basestring):
            config.set('arguments', 'subjectDir', arguments.subject)

        if os.environ.get("SGEQUEUE") is not None:
            config.set('general', 'sge_queue', os.environ.get("SGEQUEUE"))

        if arguments.queue:
            config.set('general', 'sge_queue', arguments.queue)

        if arguments.noTractography:
            config.set('tractographymrtrix', 'ignore', 'True')
            config.set('tractographydipy', 'ignore', 'True')
            config.set('arguments', 'tractography', 'False')
        else:
            config.set('arguments', 'tractography', 'True')

        #Should be safe to overwrite value base on command line arguments here
        if arguments.emergency:
            config.set('general', 'nb_threads', 'unlimited')

        if os.environ.get("TOADSERVER") is not None:
            config.set('general', 'server', os.environ.get("TOADSERVER"))
        else:
            config.set('general', 'server', 'unknown')

        if arguments.matlabIsAvailable:
            config.set('general', 'matlab_available', 'True')
        else:
            config.set('general', 'matlab_available', 'False')

        return config


    def getConfig(self):
        """Return this ConfigParser structures

        Returns:
             a config ConfigParser object

        """
        return self.config


    def __getConfigFiles(self, arguments):
        """Utility fonctions that find all configuration file that apply to a given toad subject


        First read master config file: etc/config.cfg
        Second, Process .toad.cfg in the user home directory
        Third, Look if there is a config file into the root of the study
        Fourth, Process any users input file enter as the command line option -c


        Args:
            arguments: a ArgumentParser pass by the constructor

        Returns:
            a list of all config files
        """
        configFiles = ["{}/etc/config.cfg".format(arguments.toadDir), '~/.toad.cfg']

        #config file could be found into the root of the project, into the subject and into the backup directory
        if arguments.subject:
            for directory in [os.path.dirname(arguments.subject),
                           arguments.subject,
                           os.path.join(arguments.subject, "00-backup")]:
                configFile = "{}/config.cfg".format(directory)
                if os.path.exists(configFile):
                    configFiles.append(configFile)

        if arguments.config:
            for config in arguments.config:
                if os.path.isfile(config):
                    configFiles.append(os.path.abspath(config))

        return configFiles
