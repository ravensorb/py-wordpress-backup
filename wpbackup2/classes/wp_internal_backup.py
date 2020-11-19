"""
wp_internal_backup

This is an internal class for managing the backup process for wordpress
files and database

This class should NOT be called directly
"""

# pylint: disable=line-too-long

import logging
import os
import subprocess
import tarfile

from enum import Flag, auto

from wpconfigr import WpConfigFile

from wpbackup2.exceptions import WpConfigNotFoundError
from wpbackup2.exceptions import WpDatabaseMysqlFailed
from wpbackup2.exceptions import WpDatabaseBackupFailed

from wpbackup2.classes.wpsite import WpSite

DB_DUMP_ARCNAME = 'database.sql'
WP_DIR_ARCNAME = 'wp-root'

class WpBackupMode(Flag):
    '''
    Enum for backup methods
    '''
    FILES = auto()
    DATABASE = auto()
    ALL = FILES | DATABASE

class WpInternalBackup:
    """ WpInternalBackup """

    __wp_site = None
    __wp_config = None
    __temp_path = None
    __what_if = False

    __log = None

    #########################################################################
    def __init__(self, wp_site, temp_path, what_if=False):
        self.__log = logging.getLogger(__name__)

        self.__what_if = what_if

        if not isinstance(wp_site, WpSite):
            raise TypeError("wp_site must be an instance of WpSite")

        self.__wp_site = wp_site
        self.__wp_config = WpConfigFile(self.__wp_site.wp_config_filename)

        if temp_path is None or len(temp_path) == 0:
            raise ValueError("temp_path must be specified")

        self.__temp_path = temp_path

    #########################################################################
    def __backup_files(self, archive_filename, include_database_dump=True):
        """
        Backup Wordpress Files
        """

        self.__log.info("Backing up Wordpress Files stored in '%s' to '%s'", self.__wp_site.site_path, archive_filename)

        self.__log.info('Will build the archive content in: %s', self.__temp_path)

        if not os.path.exists(self.__wp_site.wp_config_filename):
            raise WpConfigNotFoundError(wp_directory=self.__wp_site.site_path)

        self.__log.info('Creating archive: %s', archive_filename)
        if not self.__what_if:
            with tarfile.open(archive_filename, 'w:gz') as stream:

                if include_database_dump:
                    db_dump_filename = os.path.join(self.__temp_path, DB_DUMP_ARCNAME)

                    self.__log.info('Adding database dump "%s" to archive "%s" with arcname '
                                '"%s"...',
                                db_dump_filename,
                                archive_filename,
                                DB_DUMP_ARCNAME)
                    stream.add(db_dump_filename, arcname=DB_DUMP_ARCNAME)

                self.__log.info('Adding WordPress directory "%s" to archive "%s" with '
                            'arcname "%s"...',
                            self.__wp_site.site_path,
                            archive_filename,
                            WP_DIR_ARCNAME)
                stream.add(self.__wp_site.site_path, arcname=WP_DIR_ARCNAME)

        self.__log.info('Completed archive creation process...')

    #########################################################################
    def __backup_database(self):
        """
        Backup Wordpress Database
        """

        self.__log.info("Backing up Wordpress Database from '%s'", self.__wp_site.db_host)

        self.__log.info("Saving database to temp sql file for backup..")

        db_dump_filename = os.path.join(self.__temp_path, DB_DUMP_ARCNAME)

        args = [
            'mysqldump',
            '--add-drop-table',
            '-h',
            self.__wp_config.get('DB_HOST'),
            '-u',
            self.__wp_config.get('DB_USER'),
            '-p',
            self.__wp_config.get('DB_NAME'),
            '-p' + self.__wp_config.get('DB_PASSWORD')
        ]

        self.__log.debug("CMD: %s", args)

        try:
            if not self.__what_if:
                completed = subprocess.run(args, capture_output=True) # pylint: disable=subprocess-run-check

                if completed.returncode != 0:
                    self.__log.fatal('Database backup failed.\n\nmysqldump stdout:\n%s\n\nmysql '
                                    'stderr:\n%s',
                                    completed.stdout,
                                    completed.stderr)
                    raise WpDatabaseBackupFailed(fileName=db_dump_filename, stdOut=completed.stdout, stdError=completed.stderr)

                with open(db_dump_filename, 'wb') as stream:
                    stream.write(completed.stdout)
        except FileNotFoundError as error:
            self.__log.exception(error)
            self.__log.fatal('mysqldump was not found. Please install it and try again.')
            raise WpDatabaseMysqlFailed(message="mysqldump was not found", stdOut=None, stdError=None) from error

        self.__log.info('Saving database dump to "%s"...', db_dump_filename)

        self.__log.info('Database dump complete.')

    #########################################################################
    def backup(self, archive_filename, backup_mode = WpBackupMode.ALL):
        """
        Executes the backup process using the specified archive file
        """

        if WpBackupMode.ALL in backup_mode or WpBackupMode.DATABASE in backup_mode:
            self.__backup_database()

        if WpBackupMode.ALL in backup_mode or WpBackupMode.FILES in backup_mode:
            self.__backup_files(archive_filename, True if WpBackupMode.DATABASE in backup_mode else False)
