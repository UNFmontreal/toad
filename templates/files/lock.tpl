Subject $name is currently locked.
Which mean a $lock file have been found.

Is a jobs currently running for $name?

If a previously jobs crashed or have been interupted by a user. Please verify
    1- that subject $name is not active into the grid
        # qstat -r | grep "Full jobname" -B1

    2- that subject is not orphan
        # ps -ef |grep $name |grep toad


If you are 100% sure that no toad process is currently running. I may remove $lock file and continue the pipeline.
Otherwise, delete that file manually and restart the pipeline again (recommended).

If you continue, $name will be exclude from the submission?
If you are 100% sure that those subject are not running. You may type 'r' to remove the locks and continue the pipeline.
You may also interrupt the pipeline and delete those locks files manually (recommended).