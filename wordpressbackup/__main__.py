"""
Update a wp-config.php file.
"""

import argparse

from logging import basicConfig

import wordpressbackup


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

    arg_parser.add_argument('--wp-config',
                            help='Path and filename of wp-config.php',
                            required=True)

    arg_parser.add_argument('--archive',
                            help='Path and filename of the archive to backup '
                                 'to/restore from.',
                            required=True)

    arg_parser.add_argument('--log-level',
                            default='CRITICAL',
                            help='Log level',
                            required=False)

    args = arg_parser.parse_args()

    if args.restore:
        arg_parser.error('Restoration is not yet supported.')

    if args.backup == args.restore:
        arg_parser.error('Must specify either --backup or --restore.')

    # if args.set_true and args.set_false:
    #     arg_parser.error('Cannot set --set-true and --set-false.')

    # if args.value and args.set_true:
    #     arg_parser.error('Cannot set --value and --set-true.')

    # if args.value and args.set_false:
    #     arg_parser.error('Cannot set --value and --set-false.')

    basicConfig(level=str(args.log_level).upper())

    if args.backup:
        wordpressbackup.backup(wp_config_filename=args.wp_config,
                               archive_filename=args.archive)


if __name__ == '__main__':
    run_from_cli()
