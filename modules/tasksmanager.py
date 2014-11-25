import importlib
import inspect
import glob
import os


class TasksManager(object):


    def __init__(self, subject):
        self.__subject = subject
        self.__tasks = self.__setTasks()
        self.__runnableTasks = self.__setRunnableTasks()


    def getTasks(self):
        """get the list of all available task for the toad pipeline

        Returns
            a list of all available task instance
        """
        return self.__tasks


    def getNumberOfRunnableTasks(self):
        """Return the number of tasks that are mark runnable

        Returns:
            The number of tasks that are mark runnable

        """
        return len(self.__runnableTasks)


    def getRunnableTasks(self):
        #@HEADER
        return self.__runnableTasks


    def getFirstRunnableTasks(self):
        if len(self.__runnableTasks) > 0:
            return self.__runnableTasks[0]


    def run(self):
        for task in self.__runnableTasks:
            task.run()


    def __setRunnableTasks(self):
        """List all tasks that should be submit into the pipeline for that subject

        First determine which tasks a given subject should execute. Then
        look into the workflow if some tasks may be skipped

        Args:
            subject:  the subject submit into the pipeline

        Returns
            A list of instances that need to be execute
        """
        tasks=[]
        for task in self.__getDirtyTasks():
            tasks += self.__getWorkflow(task)
        #remove duplicate
        tasks=list(set(tasks))
        tasks.sort()
        return tasks


    def __getWorkflow(self, source):
        """Return the work flow of a specific task

        A workflow is an array that represent all tasks that will be impact if the source task is to be submit into the
        pipeline

        Args:
            instances: An array containing all pipeline tasks instances. see __getInstances
            source: a task

        Returns:
            An array of task name that represent the workflow that a task will impact
        """
        arrayOfTasks = []
        flaggedTasks = [source]

        for task in self.__tasks:
            arrayOfTasks.append(task)

        for task in self.__tasks[:]:
            if task is source:
                break
            else:
                arrayOfTasks.remove(task)

        for task in arrayOfTasks:
            for dependency in task.getDependencies():
                for flagged in flaggedTasks:
                    if dependency == flagged.getName():
                        flaggedTasks.append(task)

        return flaggedTasks


    def __setTasks(self):
        """Create a list of task instances.

        The list is order by tasks order ascending

        Returns:
            A list of task instances

        """
        tasks =[]
        tasksFiles = glob.glob("%s/tasks/*-*.py"%(self.__subject.getConfig().get('arguments','toadDir')))
        for taskFile in tasksFiles:
            task= self.__createATask(taskFile)
            if task is not None:
                tasks.append(self.__createATask(taskFile))
        tasks.sort()
        return self.__removeIgnoredTasks(tasks)


    def __getDirtyTasks(self):
        """ get the list of all dirty task

        If a task is marked as ignore it will be remove from the list

        Args:
            a list containing all tasks into the pipeline

        """
        dirtyTasks=[]
        for task in self.__tasks:
            if task.isTaskDirty():
                dirtyTasks.append(task)
        return self.__removeIgnoredTasks(dirtyTasks)


    def __createATask(self, taskFile):
        """ return an array of tasks files names order by the first 2 digits of the filename name

        This function also validate the filename and the extension validity.

        Args:
            tasksFiles: An unsorted array of python tasks file.

        Returns:
            the array sorted by the first 2 digit of the filename

        """
        [taskName, ext] = os.path.splitext(os.path.basename(taskFile))
        if (len(taskName) > 3) and (ext == ".py") and taskName[2] == '-':
            try:
                tokens = taskName.split("-")
                order = int(tokens[0])
                package = taskName
                module = importlib.import_module("tasks.%s"%package)
                classes = inspect.getmembers(module, inspect.isclass)
                for clazz in classes:
                    if clazz[1].__module__=="tasks.%s"%package:
                        clazz = clazz[1](self.__subject)
                        clazz.setOrder(order)
                        return clazz

            except ValueError:
                pass
        return None

    def __removeIgnoredTasks(self, tasks):
        """remove from list all tasks that should be skipped

        Args:
            tasks: a list of tasks
        """
        mandatory = []
        for task in tasks:
            if not task.isIgnore():
                mandatory.append(task)
        return mandatory