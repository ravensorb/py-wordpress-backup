""" wpbackup """

# pylint: disable=line-too-long

import logging
import tempfile
import datetime

from wpbackup2.classes.wp_internal_restore import WpInternalRestore
from wpbackup2.classes.wp_internal_backup import WpInternalBackup

from wpbackup2.classes.wp_internal_backup import WpBackupMode
from wpbackup2.classes.wp_internal_restore import WpRestoreMode
from wpbackup2.classes.wpsite import WpSite


class WpBackup:
    """ WpBackup """

    __what_if = False
    __temp_dir = None

    #########################################################################
    def __init__(self, what_if=False):
        self.__log = logging.getLogger(__name__)

        self.__what_if = what_if
        self.__temp_dir = tempfile.TemporaryDirectory()

    #########################################################################
    def __del__(self):
        self.__temp_dir = None

    #########################################################################
    def backup(self, wp_site, archive_filename, backup_mode=WpBackupMode.ALL):
        """
        Performs a backup.

        Args:
            wp_site (WpSite):           WordPress Site Details.e
            archive_filename (str):     Path and filename of tar gzip file to create.
            backup_mode (WpBackupMode): The backup mode to use
        Raises:
            WpConfigNotFoundError:  wp-config.php was not found.
        """

        self.__log.info('Starting backup.')

        wp_op = WpInternalBackup(wp_site, self.__temp_dir.name, what_if=self.__what_if)

        if archive_filename is None or len(archive_filename) == 0:
            archive_filename = "wpbackup2-{}-{}.tar.gz".format(wp_site.db_name, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

        wp_op.backup(archive_filename=archive_filename, backup_mode=backup_mode)

        self.__log.info('Backup complete.')

    #########################################################################
    def restore(self, wp_site, archive_filename, restore_mode=WpRestoreMode.ALLCLEAN):
        """
        Performs a restoration.

        Args:
            wp_site (WpSite):                   WordPress Site Details.
            archive_filename (str):             Path and filename of tar gzip file to
                                                create.
            restore_mode (WpRestoreMode):       The restore mode to use

        Raises:
            WpConfigNotFoundError:  wp-config.php was not found.
        """

        if not isinstance(wp_site, WpSite):
            raise TypeError("wp_site might be an instance of WpSite")

        if archive_filename is None or len(archive_filename) == 0:
            raise TypeError("archive name was not specified")

        self.__log.info('Starting restore.')

        wp_op = WpInternalRestore(wp_site, self.__temp_dir.name, what_if=self.__what_if)

        wp_op.restore(archive_filename=archive_filename, restore_mode=restore_mode)

        self.__log.info('Restore complete.')
