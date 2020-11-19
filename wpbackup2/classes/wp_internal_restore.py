"""
wp_internal_restore

This is an internal class for managing the restore process for wordpress
files and database

This class should NOT be called directly
"""

# pylint: disable=line-too-long

import logging
import os
import subprocess
import tarfile
import shutil

from enum import Flag, auto

import wpdatabase2
from wpconfigr import WpConfigFile

from wpbackup2.exceptions import WpDatabaseMysqlFailed
from wpbackup2.exceptions import WpDatabaseRestoreFailed

from wpbackup2.classes.wpsite import WpSite

DB_DUMP_ARCNAME = 'database.sql'
WP_DIR_ARCNAME = 'wp-root'

class WpRestoreMode(Flag):
    '''
    Enum for restore methods
    '''
    FILES = auto()
    DATABASE = auto()
    REMOVEFILESBEFORERESTORE = auto()
    DELETEDATABASEBEFORERESTORE = auto()
    ALLOVERWRITE = FILES | DATABASE
    ALLCLEAN = FILES | DATABASE | REMOVEFILESBEFORERESTORE | DELETEDATABASEBEFORERESTORE

class WpInternalRestore:
    """ WpInternalRestore """

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
    def __update_config(self):
        self.__log.info("Updating wp_config.php file...")

        if not self.__what_if:
            if (self.__wp_site.db_host is not None and len(self.__wp_site.db_host) > 0):
                self.__wp_config.set('DB_HOST', "{}{}".format(self.__wp_site.db_host, ":{}".format(self.__wp_site.db_port) if (self.__wp_site.db_port is not None) else ""))

            if (self.__wp_site.db_name is not None and len(self.__wp_site.db_name) > 0):
                self.__wp_config.set('DB_NAME', self.__wp_site.db_name)

            if self.__wp_site.credentials is not None:
                if (self.__wp_site.credentials.username is not None and len(self.__wp_site.credentials.username) > 0):
                    self.__wp_config.set('DB_USER', self.__wp_site.credentials.username)

                if (self.__wp_site.credentials.password is not None and len(self.__wp_site.credentials.password) > 0):
                    self.__wp_config.set('DB_PASSWORD', self.__wp_site.credentials.password)

            if (self.__wp_site.site_url is not None and len(self.__wp_site.site_url) > 0):
                self.__wp_config.set('WP_SITEURL', self.__wp_site.site_url)

            if (self.__wp_site.site_home is not None and len(self.__wp_site.site_home) > 0):
                self.__wp_config.set('WP_HOME', self.__wp_site.site_home)

        self.__log.debug(" Site Host='%s', Site Url='%s', Site Path='%s', Database Name='%s', Database Host='%s', Database User='%s', Database Password='%s'", # pylint: disable=line-too-long
                        self.__wp_config.get('WP_HOME'),
                        self.__wp_config.get('WP_SITEURL'),
                        self.__wp_site.site_path,
                        self.__wp_config.get('DB_NAME'),
                        self.__wp_config.get('DB_HOST'),
                        self.__wp_config.get('DB_USER'),
                        self.__wp_config.get('DB_PASSWORD')
                        )

    #########################################################################
    def __restore_files(self, archive_filename, restore_mode=WpRestoreMode.ALLCLEAN):
        """
        Restore Wordpress Files
        """

        self.__log.info('Restoring from archive: %s', archive_filename)

        with tarfile.open(archive_filename, 'r:gz') as stream:
            if WpRestoreMode.FILES in restore_mode:
                if os.path.exists(self.__wp_site.site_path) and WpRestoreMode.REMOVEFILESBEFORERESTORE in restore_mode:
                    self.__log.info('Removing existing WordPress content at "%s"...',
                                self.__wp_site.site_path)
                    if not self.__what_if:
                        shutil.rmtree(self.__wp_site.site_path, ignore_errors=True)

                self.__log.info("Restoring Wordpress Files stored in '%s' to '%s'", self.__wp_site.wp_dir, archive_filename)
                self.__log.info('Extracting WordPress directory "%s" to "%s"...',
                            WP_DIR_ARCNAME,
                            self.__wp_site.site_path)

                root_dir = WP_DIR_ARCNAME + os.path.sep
                root_dir_len = len(root_dir)

                wp_members = []

                for member in stream.getmembers():
                    if member.path.startswith(root_dir):
                        member.path = member.path[root_dir_len:]
                        wp_members.append(member)

                self.__log.debug('Extracting members: "%s"', wp_members)
                if not self.__what_if:
                    stream.extractall(members=wp_members, path=self.__wp_site.site_path)

            if WpRestoreMode.DATABASE in restore_mode:
                self.__log.info('Extracting database dump "%s" to "%s"...',
                            DB_DUMP_ARCNAME,
                            self.__temp_path)
                if not self.__what_if:
                    stream.extract(DB_DUMP_ARCNAME, path=self.__temp_path)

        self.__update_config()

        self.__log.info('File restore complete...')

    #########################################################################
    def __restore_database(self, restore_mode=WpRestoreMode.ALLCLEAN):
        """
        Restore Wordpress Database
        """

        self.__log.info("Restore Wordpress Database to '%s'", self.__wp_site.db_server)

        try:
            wpdb = wpdatabase2.WpDatabase(wp_config=self.__wp_config)
            if WpRestoreMode.DELETEDATABASEBEFORERESTORE in restore_mode and not self.__what_if:
                if wpdb.does_database_exist():
                    self.__log.info('Existing Database found. Skipping database restore')
                    return

            self.__log.info('Ensuring the database exists...')
            if not self.__what_if:
                wpdb.ensure_database_setup(admin_credentials=self.__wp_site.admin_credentials, force=force)
        except FileNotFoundError as error:
            self.__log.exception(error)
            self.__log.fatal('mysql was not found. Please install it and try again.')

            raise WpDatabaseMysqlFailed(message="mysql was not found", stdOut=None, stdError=None) from error

        db_dump_filename = os.path.join(self.__temp_path, DB_DUMP_ARCNAME)

        restore_args = [
            'mysql',
            '--host',
            self.__wp_config.get('DB_HOST'),
            '--user',
            self.__wp_site.admin_credentials.username,
            '-p' + self.__wp_site.admin_credentials.password,
            self.__wp_config.get('DB_NAME'),
            '--execute',
            'source {};'.format(db_dump_filename)
        ]

        try:
            self.__log.info('Restoring database from "%s"...', db_dump_filename)
            self.__log.debug("RESTORE CMD: %s", restore_args)

            if not self.__what_if:
                completed = subprocess.run(restore_args, capture_output=True) # pylint: disable=subprocess-run-check
                if completed.returncode != 0:
                    self.__log.fatal('Database restoration failed.\n\nmysql stdout:\n%s\n\n'
                                    'mysql stderr:\n%s',
                                    completed.stdout,
                                    completed.stderr)
                    raise WpDatabaseRestoreFailed(db_dump_filename, completed.stdout, completed.stderr)
        except FileNotFoundError as error:
            self.__log.exception(error)
            self.__log.fatal('mysql was not found. Please install it and try again.')
            raise WpDatabaseMysqlFailed(message="mysql was not found", stdOut=None, stdError=None) from error

        self.__log.info('Database restoration complete.')

    #########################################################################
    def restore(self, archive_filename, restore_mode=WpRestoreMode.ALLCLEAN):
        """
        Executes the restore process using the specified archive file
        """

        if archive_filename is None or len(archive_filename) == 0:
            raise ValueError("archive_filename must be specified")

        self.__restore_files(archive_filename)

        if WpRestoreMode.DATABASE in restore_mode:
            self.__restore_database()
