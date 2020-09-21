""" wpbackup """

# pylint: disable=line-too-long

import logging
import os
import shutil
import subprocess
import tarfile
import tempfile

from wpconfigr import WpConfigFile

import wpdatabase2
from wpdatabase2.exceptions import InvalidArgumentsError

#from wpbackup2.exceptions import WpBackupNotFoundError
from wpbackup2.exceptions import WpConfigNotFoundError
from wpbackup2.exceptions import WpDatabaseMysqlFailed
from wpbackup2.exceptions import WpDatabaseBackupFailed
from wpbackup2.exceptions import WpDatabaseRestoreFailed

from wpbackup2.classes.wpsite import WpSite

DB_DUMP_ARCNAME = 'database.sql'
WP_DIR_ARCNAME = 'wp-root'

class WpBackup:
    """ WpBackup """

    #########################################################################
    def __init__(self):
        self._log = logging.getLogger(__name__)

        self._temp_dir = tempfile.TemporaryDirectory()

    #########################################################################
    def __del__(self):
        self._temp_dir = None

    #########################################################################
    def _update_config(self, wp_site, wp_config_filename):
        wp_config = WpConfigFile(wp_config_filename)

        if (wp_site.db_host is not None and len(wp_site.db_host) > 0):
            wp_config.set('DB_HOST', "{}{}".format(wp_site.db_host, ":{}".format(wp_site.db_port) if (wp_site.db_port is not None) else ""))

        if (wp_site.db_name is not None and len(wp_site.db_name) > 0):
            wp_config.set('DB_NAME', wp_site.db_name)

        if (wp_site.credentials is not None):
            if (wp_site.credentials.username is not None and len(wp_site.credentials.username) > 0):
                wp_config.set('DB_USER', wp_site.credentials.username)

            if (wp_site.credentials.password is not None and len(wp_site.credentials.password) > 0):
                wp_config.set('DB_PASSWORD', wp_site.credentials.password)

        if (wp_site.site_url is not None and len(wp_site.site_url) > 0):
            wp_config.set('WP_SITEURL', wp_site.site_url)

        if (wp_site.site_home is not None and len(wp_site.site_home) > 0):
            wp_config.set('WP_HOME', wp_site.site_home)

        self._log.debug(" Site Host='%s', Site Url='%s', Site Path='%s', Database Name='%s', Database Host='%s', Database User='%s', Database Password='%s'", # pylint: disable=line-too-long
                        wp_config.get('WP_HOME'),
                        wp_config.get('WP_SITEURL'),
                        wp_site.site_path,
                        wp_config.get('DB_NAME'),
                        wp_config.get('DB_HOST'),
                        wp_config.get('DB_USER'),
                        wp_config.get('DB_PASSWORD')
                        )

    #########################################################################
    def _dump_database(self, wp_config_filename):
        db_dump_filename = os.path.join(self._temp_dir.name, DB_DUMP_ARCNAME)

        wp_config = WpConfigFile(wp_config_filename)

        args = [
            'mysqldump',
            '--add-drop-table',
            '-h',
            wp_config.get('DB_HOST'),
            '-u',
            wp_config.get('DB_USER'),
            '-p',
            wp_config.get('DB_NAME'),
            '-p' + wp_config.get('DB_PASSWORD')
        ]

        self._log.info('Getting database dump...')
        self._log.debug("CMD: %s", args)

        try:
            completed = subprocess.run(args, capture_output=True) # pylint: disable=subprocess-run-check
        except FileNotFoundError as error:
            self._log.exception(error)
            self._log.fatal('mysqldump was not found. Please install it and try again.')
            raise WpDatabaseMysqlFailed(message="mysqldump was not found", stdOut=None, stdError=None)

        if completed.returncode != 0:
            self._log.fatal('Database backup failed.\n\nmysqldump stdout:\n%s\n\nmysql '
                            'stderr:\n%s',
                            completed.stdout,
                            completed.stderr)
            raise WpDatabaseBackupFailed(fileName=db_dump_filename, stdOut=completed.stdout, stdError=completed.stderr)

        self._log.info('Saving database dump to "%s"...', db_dump_filename)

        with open(db_dump_filename, 'wb') as stream:
            stream.write(completed.stdout)

        self._log.info('Database dump complete.')

    #########################################################################
    def _backup_files(self, wp_site, archive_filename):
        db_dump_filename = os.path.join(self._temp_dir.name, DB_DUMP_ARCNAME)

        self._log.info('Will build the archive content in: %s', self._temp_dir.name)

        if not os.path.exists(wp_site.wp_config_filename):
            raise WpConfigNotFoundError(wp_directory=wp_site.site_path)

        self._log.info('Creating archive: %s', archive_filename)
        with tarfile.open(archive_filename, 'w:gz') as stream:
            self._log.info('Adding database dump "%s" to archive "%s" with arcname '
                           '"%s"...',
                           db_dump_filename,
                           archive_filename,
                           DB_DUMP_ARCNAME)
            stream.add(db_dump_filename, arcname=DB_DUMP_ARCNAME)

            self._log.info('Adding WordPress directory "%s" to archive "%s" with '
                           'arcname "%s"...',
                           wp_site.site_path,
                           archive_filename,
                           WP_DIR_ARCNAME)
            stream.add(wp_site.site_path, arcname=WP_DIR_ARCNAME)

    #########################################################################
    def _restore_database(self, wp_site, admin_credentials, force=False):
        wp_config = WpConfigFile(wp_site.wp_config_filename)

        try:
            wpdb = wpdatabase2.WpDatabase(wp_config=wp_config)
            if wpdb.does_database_exist() and not force:
                self._log.info('Existing Database found. Skipping database restore')
                return

            self._log.info('Ensuring the database exists...')
            wpdb.ensure_database_setup(admin_credentials=admin_credentials)
        except FileNotFoundError as error:
            self._log.exception(error)
            self._log.fatal('mysql was not found. Please install it and try again.')
            raise WpDatabaseMysqlFailed(message="mysql was not found", stdOut=None, stdError=None)

        db_dump_filename = os.path.join(self._temp_dir.name, DB_DUMP_ARCNAME)

        restore_args = [
            'mysql',
            '--host',
            wp_config.get('DB_HOST'),
            '--user',
            admin_credentials.username,
            '-p' + admin_credentials.password,
            wp_config.get('DB_NAME'),
            '--execute',
            'source {};'.format(db_dump_filename)
        ]

        try:
            self._log.info('Restoring database from "%s"...', db_dump_filename)
            self._log.debug("RESTORE CMD: %s", restore_args)
            completed = subprocess.run(restore_args, capture_output=True) # pylint: disable=subprocess-run-check
        except FileNotFoundError as error:
            self._log.exception(error)
            self._log.fatal('mysql was not found. Please install it and try again.')
            raise WpDatabaseMysqlFailed(message="mysql was not found", stdOut=None, stdError=None)

        if completed.returncode != 0:
            self._log.fatal('Database restoration failed.\n\nmysql stdout:\n%s\n\n'
                            'mysql stderr:\n%s',
                            completed.stdout,
                            completed.stderr)
            raise WpDatabaseRestoreFailed(db_dump_filename, completed.stdout, completed.stderr)

        self._log.info('Database restoration complete.')

    #########################################################################
    def _restore_files(self, wp_site, archive_filename):
        self._log.info('Will restore the archive content to: %s', wp_site.site_path)

        if os.path.exists(wp_site.site_path):
            self._log.info('Removing existing WordPress content at "%s"...',
                           wp_site.site_path)
            shutil.rmtree(wp_site.site_path, ignore_errors=True)

        self._log.info('Opening archive: %s', archive_filename)
        with tarfile.open(archive_filename, 'r:gz') as stream:
            self._log.info('Extracting WordPress directory "%s" to "%s"...',
                           WP_DIR_ARCNAME,
                           wp_site.site_path)

            root_dir = WP_DIR_ARCNAME + os.path.sep
            root_dir_len = len(root_dir)

            wp_members = []

            for member in stream.getmembers():
                if member.path.startswith(root_dir):
                    member.path = member.path[root_dir_len:]
                    wp_members.append(member)

            self._log.debug('Extracting members: "%s"', wp_members)
            stream.extractall(members=wp_members, path=wp_site.site_path)

            self._log.info('Extracting database dump "%s" to "%s"...',
                           DB_DUMP_ARCNAME,
                           self._temp_dir.name)
            stream.extract(DB_DUMP_ARCNAME, path=self._temp_dir.name)

        self._log.info('Updating database information in config file.')

        self._update_config(wp_site, wp_site.wp_config_filename)

        self._log.info('File restore complete...')

    #########################################################################
    def backup(self, wp_site, archive_filename):
        """
        Performs a backup.

        Args:
            wp_site (WpSite):        WordPress Site Details.e
            archive_filename (str): Path and filename of tar gzip file to create.

        Raises:
            WpConfigNotFoundError:  wp-config.php was not found.
        """

        self._log.info('Starting backup.')

        self._dump_database(wp_config_filename=wp_site.wp_config_filename)

        self._backup_files(wp_site, archive_filename)

        self._log.info('Backup complete.')

    #########################################################################
    def restore(self, wp_site, archive_filename, admin_credentials, force=False):
        """
        Performs a restoration.

        Args:
            wp_site (WpSite):                   WordPress Site Details.
            archive_filename (str):             Path and filename of tar gzip file to
                                                create.
            admin_credentials (Credentials):    Database admin credentials.

        Raises:
            WpConfigNotFoundError:  wp-config.php was not found.
        """

        if not isinstance(wp_site, WpSite):
            raise InvalidArgumentsError("wp_site might be an instance of WpSite")

        self._log.info('Starting restoration.')

        self._restore_files(wp_site=wp_site, archive_filename=archive_filename)

        self._restore_database(
            wp_site=wp_site,
            admin_credentials=admin_credentials,
            force=force
        )

        self._log.info('Restoration complete.')
