import functools
import importlib
import inspect
import glob
import sys
import os

class TasksManager(object):

    def __init__(self, subject):
        self.__subject = subject
        self.__tasks = self.__initialize()
        self.__runnableTasks = self.__initializeRunnableTasks(self.__tasks)

    def getSubjectName(self):
        """get the name of the current subject

        """
        return self.__subject


    def getTasks(self):
        """get the list of all available task

        the task list is not sort so there is no guaranty that dependencies is respected

        Returns
            a list of all available task instance
        """
        return self.__tasks


    def getQaTasks(self):
        """get the list of all available task who implement the methods qaSupplier

        the task list is not sort so there is no guaranty that dependencies is respected

        Returns
            a list of all available task instance who implement the methods qaSupplier
        """
        tasks = []
        for task in self.__tasks:
            if "qaSupplier" in dir(task):
                tasks.append(task)
        return sorted(tasks)


    def getRunnableTasks(self):
        """Return a list of task with ignored task remove.

        the list is guaranty to respect all dependencies

        Returns:
            The number of tasks that are mark runnable

        """
        return self.__runnableTasks


    def getNumberOfRunnableTasks(self):
        """Return the number of tasks that are mark runnable

        Returns:
            The number of tasks that are mark runnable

        """
        return len(self.__runnableTasks)


    def getFirstRunnableTasks(self):
        """Return the first runnable task from the runnable task list

        Returns:
            the first task in the runnable tasks list
        """
        if len(self.__runnableTasks) > 0:
            return self.__runnableTasks[0]


    def run(self):
        """Execute the run() methods of every runnable tasks

        """
        for task in self.__runnableTasks:
            task.run()


    def __initialize(self):
        """Create a list of task instances.

        The list is order by tasks order ascending

        Returns:
            A list of task instances

        """
        tasks =[]
        tasksFiles = glob.glob("{}/tasks/*.py".format(self.__subject.getConfig().get('arguments','toad_dir')))
        customTasks = self.__subject.getConfig().get('arguments','custom_tasks')
        if customTasks is not None:
            for customTask in customTasks:
                if os.path.isfile(customTask):
                    tasksFiles.append(os.path.abspath(customTask))
        for taskFile in tasksFiles:
            task= self.__instanciateIfATask(taskFile)
            if task is not None:
                tasks.append(task)
            else:
                print "File {} do not appear as a valid task file".format(taskFile)
        return tasks


    def __instanciateIfATask(self, taskFile):
        """ return an array of tasks files names order by the first 2 digits of the filename name

        This function also validate the filename and the extension validity.

        Args:
            tasksFiles: An unsorted array of python tasks file.

        Returns:
            the array sorted by the first 2 digit of the filename

        """
        def __isDefined(clazz, method):
            return method in vars(clazz.__class__) and inspect.isroutine(vars(clazz.__class__)[method])
        [directory, fileName] = os.path.split(taskFile)
        [package, ext] = os.path.splitext(os.path.basename(fileName))
        if ext == ".py":
            try:
                if directory not in sys.path:
                    sys.path.append(directory)
                try:
                    module = importlib.import_module(package)
                except ImportError:
                     self.info("Cannot instanciate {} module, module discarted.".format(package))
                classes = inspect.getmembers(module, inspect.isclass)
                for clazz in classes:
                    if package in clazz[1].__module__:
                        clazz = clazz[1](self.__subject)
                        if not __isDefined(clazz,"isDirty"):
                            print "Warning: isDirty() method not found. Class {} discard".format(clazz)
                            return None
                        if not __isDefined(clazz,"meetRequirement"):
                            print "Warning: meetRequirement() method not found. Class {} discard".format(clazz)
                            return None
                        if not __isDefined(clazz,"implement"):
                            print "Warning: implement() method not found.  Class {} discard".format(clazz)
                            return None
                        return clazz
            except ValueError:
                pass
        return None


    def __initializeRunnableTasks(self, tasks):
        """List all tasks that should be submit into the pipeline for that subject

        First determine which tasks a given subject should execute. Then
        look into the workflow if some tasks may be skipped

        Args:
            tasks:  a list of available tasks

        Returns
            A list of instances that need to be execute
        """

        workflow = []

        #remove ignored tasks first
        tasks = self.__removeIgnoredTasks(tasks)

        #resolve all dependencies
        graphOfDependencies = self.__resolveDependencies(tasks)

        #flatten dependencies graph to obtain a list
        dependencies = []
        for dependency in graphOfDependencies:
            dependencies.extend(sorted(dependency))

        #reorder the the tasks with current values
        for i in range(0, len(dependencies)):
            dependencies[i].setOrder(i)

        #determine all impacts the dirty tasks could have
        for dirtyTask in self.__getDirtyTasks(dependencies):
            workflow += self.__getWorkflow(dirtyTask, dependencies)

        #remove duplicate and sort
        return sorted(set(workflow))


    def __getWorkflow(self, source, tasks):
        """
        Return the work flow of a specific task

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

        for task in tasks:
            arrayOfTasks.append(task)

        for task in tasks[:]:
            if task is source:
                break
            else:
                arrayOfTasks.remove(task)

        for task in arrayOfTasks:
            for dependency in task.getDependencies():
                for flagged in flaggedTasks:
                    if dependency == flagged.getName():
                        flaggedTasks.append(task)

        return sorted(set(flaggedTasks))




    def __getDirtyTasks(self, tasks):
        """ get the list of all dirty task

        If a task is marked as ignore it will be remove from the list

        Args:
            tasks: a list containing all tasks into the pipeline

        Returns:
            a list of dirty tasks

        """
        dirtyTasks=[]
        for task in tasks:
            if task.isTaskDirty():
                dirtyTasks.append(task)
        return dirtyTasks


    def __removeIgnoredTasks(self, tasks):
        """remove from list all tasks that are mark as ignored

        Args:
            tasks: a list of tasks

        Returns:
            a list of task, all ignore task have been remove

        """
        mandatory = []
        for task in tasks:
            if not task.isIgnore():
                mandatory.append(task)
        return mandatory


    def __sortGraph(self, dictionnaries):
        """Dependencies are expressed as a dictionary whose keys are task order
        and whose values are a set of order dependencies .

        Args:
            dictionnaries: a dictionary whose keys are task numerical order value and whose
                values are a set of numerical dependencies see: GenericTask.setOrder()

        Returns:
            Output is a list of sets in topological order.

        """
        if len(dictionnaries) == 0:
            return
        dictionnaries = dictionnaries.copy()

        for key, value in dictionnaries.items():
            value.discard(key)

        valueNotDependings= functools.reduce(set.union, dictionnaries.values()) - set(dictionnaries.keys())
        dictionnaries.update({dependency:set() for dependency in valueNotDependings})
        while True:
            ordered = set(value for value, dependency in dictionnaries.items() if len(dependency) == 0)
            if not ordered:
                break
            yield ordered
            dictionnaries = {value: (dependency - ordered)
                    for value, dependency in dictionnaries.items()
                        if value not in ordered}
        if len(dictionnaries) != 0:
            raise ValueError('Found a cycling dependencies that exist among: {}'.format(', '.join(repr(value) for value in dictionnaries.items())))


    def __resolveDependencies(self, tasks):
        """Produce a list of sets of tasks in topological order base on dependencies.

        Args:
            tasks: A list of task

        Returns:
            a list of set of Tasks in topological order

        """
        taksDictionnaries = {}
        numericalDictionnaries = {}
        tasksGraph = []
        order = 0

        for task in tasks:
            task.setOrder(order)
            taksDictionnaries[task] = order
            order+=1

        for task, order in taksDictionnaries.iteritems():
            dependenciesSet = set()
            for dependency in task.getDependencies():
                for task in tasks:
                    if task.getName() == dependency:
                        dependenciesSet |= {taksDictionnaries[task]}
            numericalDictionnaries[order] = dependenciesSet

        for sets in  list(self.__sortGraph(numericalDictionnaries)):
            aSet = set()
            for order in sets:
                aSet.add(tasks[order])
            tasksGraph.append(aSet)

        return tasksGraph
