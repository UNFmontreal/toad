Subjects $names are currently locked.
Which mean files:

$locks
exists.


Is jobs currently running for $names?


If those subjects previously crashed or have been interrupted. Please make sure:
    1- those subjects $names are not active into the grid
        # qstat -r | grep "Full jobname" -B1

    2- those subject are not orphan
        # ps -ef |grep toad


If you continue, those subjects will be exclude from the submission?
If you are 100% sure that those subject are not running. You may type 'r' to remove the locks and continue the pipeline.
You may also interrupt the pipeline and delete those locks files manually (recommended).