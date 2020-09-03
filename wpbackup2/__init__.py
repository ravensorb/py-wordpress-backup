""" wpbackup2 """

# Version of the wpbackup2 package
#__version__ = "0.3.4"

#import wpbackup2

from wpbackup2.exceptions import WpBackupNotFoundError # pylint: disable=line-too-long
from wpbackup2.exceptions import WpConfigNotFoundError # pylint: disable=line-too-long

from wpbackup2.exceptions import WpDatabaseMysqlFailed # pylint: disable=line-too-long
from wpbackup2.exceptions import WpDatabaseBackupFailed # pylint: disable=line-too-long
from wpbackup2.exceptions import WpDatabaseRestoreFailed # pylint: disable=line-too-long

from wpbackup2.wpbackup import WpBackup
from wpbackup2.wpsite import WpSite
