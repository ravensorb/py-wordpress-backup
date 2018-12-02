"""
"wordpressbackup" package.
"""

import logging
import subprocess

from wpconfigr import WpConfigFile

# from wpconfigr.wp_config_string import WpConfigString
# from wpconfigr.wp_config_file import WpConfigFile

LOG = logging.getLogger(__name__)


def _dump_database(wp_config_filename, dump_filename):
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
        LOG.fatal('Database backup failed.\n\nmysqldump stdout:\n%s\n\nmysql stderr:\n%s', completed.stdout, completed.stderr)
        exit(2)

    LOG.info('Saving database dump to "%s"...', dump_filename)

    with open(dump_filename, 'w') as stream:
        stream.write(completed.stdout)

    LOG.info('Database dump complete.')


def backup(wp_config_filename, archive_filename):

    _dump_database(wp_config_filename)
    LOG.info('Backup complete.')
