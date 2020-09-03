""" wpbackup """

# pylint: disable=line-too-long

import logging
import os
import shutil
import subprocess
import tarfile
import tempfile

from wpconfigr import WpConfigFile

#from wpbackup2.exceptions import WpBackupNotFoundError
from wpbackup2.exceptions import WpConfigNotFoundError

from wpbackup2.exceptions import WpDatabaseMysqlFailed
from wpbackup2.exceptions import WpDatabaseBackupFailed
from wpbackup2.exceptions import WpDatabaseRestoreFailed

LOG = logging.getLogger(__name__)
DB_DUMP_ARCNAME = 'database.sql'
WP_DIR_ARCNAME = 'wp-root'

class WpBackup:
    """ WpBackup """

    #########################################################################
    def __init__(self):
        pass

    #########################################################################
    def _update_config(self, wp_config_filename, wp_site):
        wp_config = WpConfigFile(wp_config_filename)

        if (wp_site.DatabaseHost is not None and len(wp_site.DatabaseHost) > 0):
            wp_config.set('DB_HOST', "{}{}".format(wp_site.DatabaseHost, ":{}".format(wp_site.DatabasePort) if (wp_site.DatabasePort is not None) else ""))

        if (wp_site.DatabaseName is not None and len(wp_site.DatabaseName) > 0):
            wp_config.set('DB_NAME', wp_site.DatabaseName)

        if (wp_site.DatabaseUser is not None and len(wp_site.DatabaseUser) > 0):
            wp_config.set('DB_USER', wp_site.DatabaseUser)

        if (wp_site.DatabasePassword is not None and len(wp_site.DatabasePassword) > 0):
            wp_site.set('DB_PASSWORD', wp_site.DatabasePassword)

        if (wp_site.SiteUrl is not None and len(wp_site.SiteUrl) > 0):
            wp_config.set('WP_SITEURL', wp_site.SiteUrl)

        if (wp_site.SiteHost is not None and len(wp_site.SiteHost) > 0):
            wp_config.set('WP_HOME', wp_site.SiteHost)

        LOG.debug(" Site Host='%s', Site Url='%s', Site Path='%s', Database Name='%s', Database Host='%s', Database User='%s', Database Password='%s'", # pylint: disable=line-too-long
                  wp_config.get('WP_HOME'),
                  wp_config.get('WP_SITEURL'),
                  wp_site.SitePath,
                  wp_config.get('DB_NAME'),
                  wp_config.get('DB_HOST'),
                  wp_config.get('DB_USER'),
                  wp_config.get('DB_PASSWORD')
                  )

    #########################################################################
    def _dump_database(self, wp_config_filename, db_dump_filename):
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

        LOG.info('Getting database dump...')
        LOG.debug("CMD: %s", args)

        try:
            completed = subprocess.run(args, capture_output=True)
        except FileNotFoundError as error:
            LOG.exception(error)
            LOG.fatal('mysqldump was not found. Please install it and try again.')
            raise WpDatabaseMysqlFailed(message="mysqldump was not found", stdOut=None, stdError=None)

        if completed.returncode != 0:
            LOG.fatal('Database backup failed.\n\nmysqldump stdout:\n%s\n\nmysql '
                      'stderr:\n%s',
                      completed.stdout,
                      completed.stderr)
            raise WpDatabaseBackupFailed(fileName=db_dump_filename, stdOut=completed.stdout, stdError=completed.stderr)

        LOG.info('Saving database dump to "%s"...', db_dump_filename)

        with open(db_dump_filename, 'wb') as stream:
            stream.write(completed.stdout)

        LOG.info('Database dump complete.')

    #########################################################################
    def _restore_database(self, wp_config_filename, db_dump_filename, admin_credentials):
        wp_config = WpConfigFile(wp_config_filename)

        create_args = [
            'mysql',
            '--host',
            wp_config.get('DB_HOST'),
            '--user',
            admin_credentials.username,
            '-p' + admin_credentials.password,
            '--execute',
            'CREATE DATABASE IF NOT EXISTS {};'.format(wp_config.get('DB_NAME'))
        ]

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

        LOG.info('Copying...')
        shutil.copy(db_dump_filename, '/tmp/database.sql')

        try:
            LOG.info('Ensuring the database exists...')
            LOG.debug("CREATE CMD: %s", create_args)
            completed = subprocess.run(create_args, capture_output=True)
        except FileNotFoundError as error:
            LOG.exception(error)
            LOG.fatal('mysql was not found. Please install it and try again.')
            raise WpDatabaseMysqlFailed(message="mysql was not found", stdOut=None, stdError=None)

        if completed.returncode != 0:
            LOG.fatal('Creating database failed.\n\nmysql stdout:\n%s\n\n'
                      'mysql stderr:\n%s',
                      completed.stdout,
                      completed.stderr)
            raise WpDatabaseRestoreFailed(db_dump_filename, completed.stdout, completed.stderr)

        try:
            LOG.info('Restoring database from "%s"...', db_dump_filename)
            LOG.debug("RESTORE CMD: %s", restore_args)
            completed = subprocess.run(restore_args, capture_output=True)
        except FileNotFoundError as error:
            LOG.exception(error)
            LOG.fatal('mysql was not found. Please install it and try again.')
            raise WpDatabaseMysqlFailed(message="mysql was not found", stdOut=None, stdError=None)

        if completed.returncode != 0:
            LOG.fatal('Database restoration failed.\n\nmysql stdout:\n%s\n\n'
                      'mysql stderr:\n%s',
                      completed.stdout,
                      completed.stderr)
            raise WpDatabaseRestoreFailed(db_dump_filename, completed.stdout, completed.stderr)

        LOG.info('Database restoration complete.')

    #########################################################################
    def backup(self, wp_site, archive_filename):
        """
        Performs a backup.

        Args:
            wp_site (WpSite):        WordPress Site Details.
            archive_filename (str): Path and filename of tar gzip file to create.

        Raises:
            WpConfigNotFoundError:  wp-config.php was not found.
        """

        LOG.info('Starting backup.')

        temp_dir = tempfile.TemporaryDirectory()

        LOG.info('Will build the archive content in: %s', temp_dir.name)

        db_dump_path = os.path.join(temp_dir.name, DB_DUMP_ARCNAME)

        wp_config_filename = os.path.join(wp_site.SitePath, 'wp-config.php')

        if not os.path.exists(wp_config_filename):
            raise WpConfigNotFoundError(wp_directory=wp_site.SitePath)

        self._dump_database(wp_config_filename=wp_config_filename,
                            db_dump_filename=db_dump_path)

        LOG.info('Creating archive: %s', archive_filename)
        with tarfile.open(archive_filename, 'w:gz') as stream:
            LOG.info('Adding database dump "%s" to archive "%s" with arcname '
                     '"%s"...',
                     db_dump_path,
                     archive_filename,
                     DB_DUMP_ARCNAME)
            stream.add(db_dump_path, arcname=DB_DUMP_ARCNAME)

            LOG.info('Adding WordPress directory "%s" to archive "%s" with '
                     'arcname "%s"...',
                     wp_site.SitePath,
                     archive_filename,
                     WP_DIR_ARCNAME)
            stream.add(wp_site.SitePath, arcname=WP_DIR_ARCNAME)

        LOG.info('Backup complete.')

    #########################################################################
    def restore(self, wp_site, archive_filename, admin_credentials):
        """
        Performs a restoration.

        Args:
            wp_site (wpSite):                   WordPress Site Details.
            archive_filename (str):             Path and filename of tar gzip file to
                                                create.
            admin_credentials (Credentials):    Database admin credentials.

        Raises:
            WpConfigNotFoundError:  wp-config.php was not found.
        """

        LOG.info('Starting restoration.')

        temp_dir = tempfile.TemporaryDirectory()

        LOG.info('Will build the archive content in: %s', temp_dir.name)

        db_dump_path = os.path.join(temp_dir.name, DB_DUMP_ARCNAME)
        LOG.info('Will extract the database dump to: %s', db_dump_path)

        tmp_wp_dir_path = os.path.join(temp_dir.name, WP_DIR_ARCNAME)
        LOG.info('Will extract the WordPress content to: %s', tmp_wp_dir_path)

        if os.path.exists(wp_site.SitePath):
            LOG.info('Removing existing WordPress content at "%s"...',
                     wp_site.SitePath)
            shutil.rmtree(wp_site.SitePath, ignore_errors=True)

        LOG.info('Opening archive: %s', archive_filename)
        with tarfile.open(archive_filename, 'r:gz') as stream:
            LOG.info('Extracting WordPress directory "%s" to "%s"...',
                     WP_DIR_ARCNAME,
                     wp_site.SitePath)

            root_dir = WP_DIR_ARCNAME + os.path.sep
            root_dir_len = len(root_dir)

            wp_members = []

            for member in stream.getmembers():
                if member.path.startswith(root_dir):
                    member.path = member.path[root_dir_len:]
                    wp_members.append(member)

            stream.extractall(members=wp_members, path=wp_site.SitePath)

            LOG.info('Extracting database dump "%s" to "%s"...',
                     DB_DUMP_ARCNAME,
                     temp_dir.name)
            stream.extract(DB_DUMP_ARCNAME, path=temp_dir.name)

            wp_config_filename = os.path.join(wp_site.SitePath, 'wp-config.php')

            self._update_config(wp_config_filename, wp_site)

            self._restore_database(
                wp_config_filename=wp_config_filename,
                db_dump_filename=db_dump_path,
                admin_credentials=admin_credentials
            )

        LOG.info('Restoration complete.')
