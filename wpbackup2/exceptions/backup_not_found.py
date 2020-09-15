""" wpbackup2 file exception: WpBackupNotFoundError """

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
