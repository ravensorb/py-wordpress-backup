""" wpbackup2 database exception: WpDatabaseBackupFailed """

class WpDatabaseBackupFailed(Exception):
    """
    Raised when the database backup fails

    Args:
        stdOut (str): standard output.
        stdErr (str): standard error.
        fileName (str): name of backup file
    """

    def __init__(self, fileName, stdOut, stdError):
        tmp = ('Database restore failed for file "{}.\nStdOut: "{}"\nStdErr: "{}"') # pylint: disable=line-too-long
        msg = tmp.format(fileName, stdOut, stdError)
        super().__init__(msg)
