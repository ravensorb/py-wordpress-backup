"""
Backup or restore WordPress content.
"""

# pylint: disable=line-too-long

import argparse
import logging

import chesney

from wpdatabase2.classes import WpCredentials

from wpbackup2.classes.wpbackup import WpBackup
from wpbackup2.classes.wpsite import WpSite
from wpbackup2.__version__ import __version__

def run_from_cli():
    """
    Perform a backup or restore instigated from a CLI.
    """

    arg_parser = argparse.ArgumentParser(
        description='Backup and restore all your self-hosted WordPress '
                    'content.',
        prog='python -m wpbackup')

    arg_parser.add_argument('--version', action='version',
                    version='%(prog)s {version}'.format(version=__version__))

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

    arg_parser.add_argument('--new-site-url',
                            default=None,
                            help='New Site Url')

    arg_parser.add_argument('--new-site-home-url',
                            default=None,
                            help='New Site Home Url')

    arg_parser.add_argument('--new-db-host',
                            default=None,
                            help='New Database Host')

    arg_parser.add_argument('--new-db-name',
                            default=None,
                            help='New Database Name')

    arg_parser.add_argument('--new-db-user',
                            default=None,
                            help='New Database User Name')

    arg_parser.add_argument('--new-db-password',
                            default=None,
                            help='New Database User Password')

    args = arg_parser.parse_args()

    if args.backup == args.restore:
        arg_parser.error('Must specify either --backup or --restore.')

    logging.basicConfig(level=str(args.log_level).upper())
    log = logging.getLogger(__name__)

    if args.only_appointed_in_asg:
        if not chesney.is_appointed():
            log.fatal('This EC2 instance is not appointed.')
            return -1

    wpsite = WpSite(site_home=args.new_site_home_url if "new_site_host" in args else None,
                    site_url=args.new_site_url  if "new_site_url" in args else None,
                    site_path=args.wp_dir,
                    db_host=args.new_db_host if "new_db_host" in args else None,
                    db_name=args.new_db_name if "new_db_name" in args else None,
                    credentials=WpCredentials.from_username_and_password(args.new_db_user if "new_db_user" in args else None, args.new_db_password if "new_db_password" in args else None)
                    )

    wpbackup = WpBackup()

    if args.backup:
        wpbackup.backup(wp_site=wpsite,
                        archive_filename=args.archive)
    elif args.restore:
        if args.admin_credentials_aws_secret_id:
            credentials = WpCredentials.from_aws_secrets_manager(
                secret_id=args.admin_credentials_aws_secret_id,
                region=args.admin_credentials_aws_region
            )
        else:
            credentials = WpCredentials.from_username_and_password(
                username=args.admin_username,
                password=args.admin_password
            )

        wpbackup.restore(wp_site=wpsite,
                         archive_filename=args.archive,
                         admin_credentials=credentials)


if __name__ == '__main__':
    run_from_cli()
