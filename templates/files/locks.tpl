Subjects $names are currently locked.
Which mean files:

$locks
exists.

Are thoses jobs currently running?

If a previously jobs crashed or have been interrupted. Please verify
    1- those subjects $names are not active into the grid
        # qstat -r | grep "Full jobname" -B1

    2- those subject are not orphan
        # ps -ef |grep toad

Otherwise, you may delete
    $locks

