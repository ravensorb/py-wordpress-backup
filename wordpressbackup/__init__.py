"""
"wordpressbackup" package.
"""

import logging
import subprocess

# from wpconfigr.wp_config_string import WpConfigString
# from wpconfigr.wp_config_file import WpConfigFile

def backup(wp_config_filename, archive_filename):

    log = logging.getLogger(__name__)

    try:
        completed = subprocess.run(['mysqldump'], capture_output=True)
    except FileNotFoundError as error:
        log.fatal('mysqldump was not found. Please install it and try again.')
        exit(1)

    if completed.returncode != 0:
        log.fatal('Database backup failed.\n\nmysqldump stdout:\n%s\n\nmysql stderr:\n%s', completed.stdout, completed.stderr)
        exit(2)

    log.info('Backup complete.')
