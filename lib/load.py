import socket
import os

__author__ = 'mathieu'


class Load(object):


    def __init__(self, nThreads="algorithm"):
        """Determine the number of threads a package should consume without stressing the server.

        The package should implement some multithreading capabilty prior to use that package

        Args:
            nTreads: if not set to "algorithm", Force to override the return value to a specific number.

        """
        self.nThreads = nThreads


    def __getLoad(self):
        """utility that displays the load average of the system over the last 1 minutes

        Returns:
            a float value representing the load
        """
        return os.getloadavg()[0]


    def __get5MinuteLoad(self):
        """utility that displays the load average of the system over the last 5 minutes

        Returns:
            a float value representing the load
        """
        return os.getloadavg()[1]


    def isSingleThread(self):
        """Define if a command line should be run as a single thread.

        Returns:
            True if the load on the system is consider low, False Otherwise
        """
        return self.__getLoad() < 15


    def getNTreadsAnts(self):
        """Define the number of thread that should be deploy without stressing the server too much

        Returns:
            the suggested number of threads that should be deploy
        """
        os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = self.__getNTreads()


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

        Returns:
            the suggested number of threads that should be deploy
        """
        if self.nThreads == "algorithm":
            if 'magma' in socket.gethostname():
                if self.__getLoad() > 100:
                    return "1"

                elif self.__getLoad() > 40 and (self.__getLoad() < self.__get5MinuteLoad()):
                    return "5"

                elif self.__getLoad() > 40:
                    return "3"

                elif self.__getLoad() > 20:
                    return "5"

                elif self.__getLoad() > 10:
                    return "7"

                elif self.__getLoad() > 1:
                    return "10"

                else:
                    return "23"

            elif 'stark' in socket.gethostname():
                if self.__getLoad() > 100:
                    return "4"

                elif self.__getLoad() > 50 and (self.__getLoad() < self.__get5MinuteLoad()):
                    return "9"

                elif self.__getLoad() > 50:
                    return "7"

                elif self.__getLoad() > 20:
                    return "15"

                elif self.__getLoad() > 5:
                    return "20"

                elif self.__getLoad() > 1:
                    return "30"

                else:
                    return "63"

            else:
                return "3"
        else:
            return self.nThreads


    def getNTreads(self):
        return self.__getNTreads()