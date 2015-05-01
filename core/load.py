import socket
import os

__author__ = 'mathieu'


class Load(object):


    def __init__(self, config):
        """Determine the number of threads a package should consume without stressing the server.

        The package should implement some multithreading capabilty prior to use that package

        Args:

           config: a configParser
        """
        self.__config = config
        self.__nbThreads = self.__config.get('general', 'nb_threads')
        try:
            self.nbSubjects = int(self.__config.get('general', 'nb_subjects'))
        except ValueError:
            self.nbSubjects = 1000


    def __getLoad(self):
        """utility that displays the load average of the system over the last 1 minutes

        Returns:
            a float value representing the load
        """
        return os.getloadavg()[0]


    def getNTreadsEddy(self):
        """Define the number of thread that should be deploy without stressing the server too much

        Returns:
            the suggested number of threads that should be deploy
        """
        os.environ["OMP_NUM_THREADS"] = self.__getNTreads()


    def getNTreadsDenoise(self):
        """Define the number of thread that should be deploy without stressing the server too much

        limit the number of threads to 5 because higher values may lead to matlab crash

        Returns:
            the suggested number of threads that should be deploy
        """
        try:
            nTreads = int(self.__getNTreads())
            if nTreads > 5:
                nTreads = 5

        except ValueError:
            nTreads = 1
        return str(nTreads)


    def getNTreadsMrtrix(self):
        """Define the number of thread that should be deploy without stressing the server too much

        Returns:
            the suggested number of threads that should be deploy
        """
        return self.__getNTreads()


    def __getNTreads(self):
        """Define the number of thread that should be deploy without stressing the server too much

            -First compute the number of threads base on the server capacity
            -Second look if nbThreads have not been overwrite into the config file
            -Third make sure the system is not overworking
            -Last, if emergency have been call, pray to avoid a crash

        Returns:
            the suggested number of threads that should be deploy

        """

        serverName = self.__config.get('general', 'server')

        #First compute the number of threads base on the server capacity
        if 'magma' in serverName:
            if self.nbSubjects <= 5:
                value = 4
            elif self.nbSubjects <= 10:
                value = 3
            elif self.nbSubjects <= 15:
                value = 2
            else:
                value = 1

        elif 'stark' in serverName:
            if self.nbSubjects <= 5:
                value = 5
            elif self.nbSubjects <= 10:
                value = 4
            elif self.nbSubjects <= 15:
                value = 3
            elif self.nbSubjects <= 20:
                value = 2
            else:
                value = 1

        elif 'mammouth' in serverName:
                value = 24
        else:
            value = 1


        #Second look if nbThreads have not been overwrite into the config file
        if self.__nbThreads is not "algorithm" or self.__nbThreads is not "unlimited":
            try:
                nbThreads = int(self.__nbThreads)
                if nbThreads <= value:
                    value = nbThreads
            except ValueError:
                pass


        #Third make sure the system is not overworking
        if self.isSystemOverloaded(serverName):
            value = 1

        #Last, if emergency have been call, pray to avoid a crash
        if self.__nbThreads is "unlimited" and self.nbSubjects == 1:
            value = 100

        return str(value)


    def isSystemOverloaded(self, serverName):
        """ Define a treshold for the load of the server

        Args:
            serverName: the name of the server

        Returns:
            A boolean if the system is consider overload or not
        """
        if serverName == "magma" and self.__getLoad() > 70:
                return True
        elif serverName == "stark" and self.__getLoad() > 100:
                return True
        return False


    def getNTreads(self):
        """Define the number of thread that should be deploy without stressing the server too much

        Returns:
            the suggested number of threads that should be deploy

        """
        return self.__getNTreads()
