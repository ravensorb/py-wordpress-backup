""" wpbackup2 exceptions """

###########################################################################
###########################################################################
## File Related
###########################################################################
class WpBackupNotFoundError(Exception):
    """
    Raised when backup file cannot be found.

    Args:
        filename (str): backup file that expected.
    """

    def __init__(self, filename):
        tmp = ('Unable to locate the backup file requested "{}"')
        msg = tmp.format(filename)
        super().__init__(msg)

###########################################################################
class WpConfigNotFoundError(Exception):
    """
    Raised when "wp-config.php" cannot be found.

    Args:
        wp_directory (str): Directory where "wp-config.php" was expected.
    """

    def __init__(self, wp_directory):
        tmp = ('This version of wpbackup expects "wp-config.php" to '
               'exist in the root of the WordPress directory ("{}").')
        msg = tmp.format(wp_directory)
        super().__init__(msg)

###########################################################################
###########################################################################
## Database
###########################################################################
class WpDatabaseMysqlFailed(Exception):
    """
    Raised when the mysql command failes

    Args:
        message (str): message
        stdOut (str): standard output.
        stdErr (str): standard error.
    """

    def __init__(self, message, stdOut, stdError):
        tmp = ('"{}.\nStdOut: "{}"\nStdErr: "{}"')
        msg = tmp.format(message, stdOut, stdError)
        super().__init__(msg)

###########################################################################
class WpDatabaseBackupFailed(Exception):
    """
    Raised when the database backup fails

    Args:
        stdOut (str): standard output.
        stdErr (str): standard error.
        fileName (str): name of backup file
    """

    def __init__(self, fileName, stdOut, stdError):
        tmp = ('Database backup failed for file "{}.\nStdOut: "{}"\nStdErr: "{}"')
        msg = tmp.format(fileName, stdOut, stdError)
        super().__init__(msg)

###########################################################################
class WpDatabaseRestoreFailed(Exception):
    """
    Raised when the database restore fails

    Args:
        stdOut (str): standard output.
        stdErr (str): standard error.
        fileName (str): name of backup file
    """

    def __init__(self, fileName, stdOut, stdError):
        tmp = ('Database restore failed for file "{}.\nStdOut: "{}"\nStdErr: "{}"')
        msg = tmp.format(fileName, stdOut, stdError)
        super().__init__(msg)
