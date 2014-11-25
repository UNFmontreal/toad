Subject $name is currently locked.
Which mean a $lock file have been found.

Is a jobs currently running for $name?

If a previously jobs crashed or have been interupted by a user. Please verify
    1- that subject $name is not active into the grid
        # qstat -r | grep "Full jobname" -B1

    2- that subject is not orphan
        # ps -ef |grep $name |grep toad


Otherwise, you may delete $lock file.