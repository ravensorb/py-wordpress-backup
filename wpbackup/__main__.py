"""
Update a wp-config.php file.
"""

import argparse
import logging

import chesney

import wpbackup


def run_from_cli():
    """
    Perform a backup or restore instigated from a CLI.
    """

    arg_parser = argparse.ArgumentParser(
        description='Backup and restore all your self-hosted WordPress '
                    'content.',
        prog='python -m wordpressbackup')


    arg_parser.add_argument('--backup',
                            action='store_true',
                            help='Perform a backup')

    arg_parser.add_argument('--restore',
                            action='store_true',
                            help='Perform a restoration')

    arg_parser.add_argument('--wp-dir',
                            help='Path to the root of the WordPress directory',
                            required=True)

    arg_parser.add_argument('--archive',
                            help='Path and filename of the archive (.tar.gz) '
                                 'to backup to/restore from.',
                            required=True)

    arg_parser.add_argument('--log-level',
                            default='CRITICAL',
                            help='Log level',
                            required=False)

    arg_parser.add_argument('--only-appointed-in-asg',
                            action='store_true',
                            help='Ensure that only one AWS EC2 instance in '
                                 'this auto-scaling group performs the '
                                 'action.')

    args = arg_parser.parse_args()

    if args.restore:
        arg_parser.error('Restoration is not yet supported.')

    if args.backup == args.restore:
        arg_parser.error('Must specify either --backup or --restore.')

    logging.basicConfig(level=str(args.log_level).upper())
    log = logging.getLogger(__name__)

    if args.only_appointed_in_asg:
        if not chesney.is_appointed():
            log.fatal('This EC2 instance is not appointed.')
            exit(0)

    if args.backup:
        wpbackup.backup(wp_directory=args.wp_dir,
                        archive_filename=args.archive)


if __name__ == '__main__':
    run_from_cli()
