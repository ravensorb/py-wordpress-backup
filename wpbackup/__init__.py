"""
A Python package for backing up and restoring all your self-hosted WordPress
content.
"""

import logging
import os
import shutil
import subprocess
import tarfile
import tempfile

from wpconfigr import WpConfigFile
from wpdatabase.classes import Credentials

from wpbackup.exceptions import WpConfigNotFoundError

LOG = logging.getLogger(__name__)


DB_DUMP_ARCNAME = 'database.sql'
WP_DIR_ARCNAME = 'wp-root'


def _dump_database(wp_config_filename, db_dump_filename):
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

    try:
        completed = subprocess.run(args, capture_output=True)
    except FileNotFoundError as error:
        LOG.fatal(error)
        LOG.fatal('mysqldump was not found. Please install it and try again.')
        exit(1)

    if completed.returncode != 0:
        LOG.fatal('Database backup failed.\n\nmysqldump stdout:\n%s\n\nmysql '
                  'stderr:\n%s',
                  completed.stdout,
                  completed.stderr)
        exit(2)

    LOG.info('Saving database dump to "%s"...', db_dump_filename)

    with open(db_dump_filename, 'wb') as stream:
        stream.write(completed.stdout)

    LOG.info('Database dump complete.')


def _restore_database(wp_config_filename, db_dump_filename, admin_credentials):
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
        wp_config.get('DB_NAME')
    ]

    try:
        LOG.info('Ensuring the database exists...')
        completed = subprocess.run(create_args, capture_output=True)
        LOG.info('Restoring from database dump...')
        completed = subprocess.run(restore_args, capture_output=True, input=db_dump_filename)
    except FileNotFoundError as error:
        LOG.fatal(error)
        LOG.fatal('mysqldump was not found. Please install it and try again.')
        exit(1)

    if completed.returncode != 0:
        LOG.fatal('Database restoration failed.\n\nmysqldump stdout:\n%s\n\n'
                  'mysql stderr:\n%s',
                  completed.stdout,
                  completed.stderr)
        exit(2)

    LOG.info('Database restoration complete.')


def backup(wp_directory, archive_filename):
    """
    Performs a backup.

    Args:
        wp_directory (str):     Root WordPress directory.
        archive_filename (str): Path and filename of tar gzip file to create.

    Raises:
        WpConfigNotFoundError:  wp-config.php was not found.
    """

    LOG.info('Starting backup.')

    temp_dir = tempfile.TemporaryDirectory()

    LOG.info('Will build the archive content in: %s', temp_dir.name)

    db_dump_path = os.path.join(temp_dir.name, DB_DUMP_ARCNAME)

    wp_config_filename = os.path.join(wp_directory, 'wp-config.php')

    if not os.path.exists(wp_config_filename):
        raise WpConfigNotFoundError(wp_directory=wp_directory)

    _dump_database(wp_config_filename=wp_config_filename,
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
                 wp_directory,
                 archive_filename,
                 WP_DIR_ARCNAME)
        stream.add(wp_directory, arcname=WP_DIR_ARCNAME)

    LOG.info('Backup complete.')


def restore(wp_directory, archive_filename, admin_credentials):
    """
    Performs a restoration.

    Args:
        wp_directory (str):              Root WordPress directory.
        archive_filename (str):          Path and filename of tar gzip file to
                                         create.
        admin_credentials (Credentials): Database admin credentials.

    Raises:
        WpConfigNotFoundError:  wp-config.php was not found.
    """

    LOG.info('Starting restoration.')

    temp_dir = tempfile.TemporaryDirectory()

    LOG.info('Will build the archive content in: %s', temp_dir.name)

    db_dump_path = os.path.join(temp_dir.name, 'database.sql')
    LOG.info('Will extract the database dump to: %s', db_dump_path)

    tmp_wp_dir_path = os.path.join(temp_dir.name, WP_DIR_ARCNAME)
    LOG.info('Will extract the WordPress content to: %s', tmp_wp_dir_path)

    if os.path.exists(wp_directory):
        LOG.info('Removing existing WordPress content at "%s"...',
                 wp_directory)
        shutil.rmtree(wp_directory)

    LOG.info('Opening archive: %s', archive_filename)
    with tarfile.open(archive_filename, 'r:gz') as stream:
        LOG.info('Extracting WordPress directory "%s" to "%s"...',
                 WP_DIR_ARCNAME,
                 wp_directory)

        root_dir = WP_DIR_ARCNAME + os.path.sep
        root_dir_len = len(root_dir)

        wp_members = []

        for member in stream.getmembers():
            if member.path.startswith(root_dir):
                member.path = member.path[root_dir_len:]
                wp_members.append(member)

        stream.extractall(members=wp_members, path=wp_directory)

        LOG.info('Extracting database dump "%s" to "%s"...',
                 DB_DUMP_ARCNAME,
                 db_dump_path)
        stream.extract(DB_DUMP_ARCNAME, path=db_dump_path)

        wp_config_filename = os.path.join(wp_directory, 'wp-config.php')

        _restore_database(
            wp_config_filename=wp_config_filename,
            db_dump_filename=db_dump_path,
            admin_credentials=admin_credentials
        )

    LOG.info('Restoration complete.')
