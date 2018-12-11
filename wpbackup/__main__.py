"""
Backup or restore WordPress content.
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

    arg_parser.add_argument('--admin-username',
                            help='Database admin username. Required only for '
                                 'restorations.',
                            required=False)

    arg_parser.add_argument('--admin-password',
                            help='Database admin password. Required only for '
                                 'restorations.',
                            required=False)

    arg_parser.add_argument('--admin-credentials-aws-secret-id',
                            help='Database admin credentials secret ID. '
                                 'Required only for restorations.',
                            required=False)

    arg_parser.add_argument('--admin-credentials-aws-region',
                            help='Region in which the database admin '
                                 'credentials secret resides. Required only '
                                 'for restorations.',
                            required=False)

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
    elif args.restore:
        if args.admin_credentials_aws_secret_id:
            credentials = wpbackup.Credentials.from_aws_secrets_manager(
                secret_id=args.admin_credentials_aws_secret_id,
                region=args.admin_credentials_aws_region
            )
        else:
            credentials = wpbackup.Credentials.from_username_and_password(
                username=args.admin_username,
                password=args.admin_password
            )

        wpbackup.restore(wp_directory=args.wp_dir,
                         archive_filename=args.archive,
                         admin_credentials=credentials)


if __name__ == '__main__':
    run_from_cli()
