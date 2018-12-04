"""
"wordpressbackup" package.
"""

import logging
import os
import subprocess
import tarfile
import tempfile

from wpconfigr import WpConfigFile

from wpbackup.exceptions import WpConfigNotFoundError

LOG = logging.getLogger(__name__)


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


def backup(wp_directory, archive_filename):

    LOG.info('Starting backup.')

    temp_dir = tempfile.TemporaryDirectory()

    LOG.info('Will build the archive content in: %s', temp_dir.name)

    db_dump_filename = os.path.join(temp_dir.name, 'database.sql')

    wp_config_filename = os.path.join(wp_directory, 'wp-config.php')

    if not os.path.exists(wp_config_filename):
        raise WpConfigNotFoundError(wp_directory=wp_directory)

    _dump_database(wp_config_filename=wp_config_filename,
                   db_dump_filename=db_dump_filename)

    LOG.info('Creating archive: %s', archive_filename)
    with tarfile.open(archive_filename, 'w:gz') as stream:
        LOG.info('Adding database dump "%s" to archive "%s"...',
                 db_dump_filename,
                 archive_filename)
        stream.add(db_dump_filename, arcname=db_dump_filename)

        LOG.info('Adding WordPress directory "%s" to archive "%s"...',
                 wp_directory,
                 archive_filename)
        stream.add(wp_directory, arcname=wp_directory)

    LOG.info('Backup complete.')
