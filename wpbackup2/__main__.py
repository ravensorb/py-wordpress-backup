"""
Backup or restore WordPress content.
"""

# pylint: disable=line-too-long

import argparse
import logging
import chesney

from wpdatabase2.classes import WpCredentials

from wpbackup2.classes.wp_internal_backup import WpBackupMode
from wpbackup2.classes.wp_internal_restore import WpRestoreMode
from wpbackup2.classes.wpbackup import WpBackup
from wpbackup2.classes.wpsite import WpSite
from wpbackup2.__version__ import __version__

#########################################################################
#########################################################################
# Main Application
#########################################################################
#########################################################################

def run_from_cli():
    """
    Perform a backup or restore instigated from a CLI.
    """

    # Setup the main parser
    arg_parser = argparse.ArgumentParser(
                    description='Backup/restore your WordPress content and database ',
                    prog='python3 -m wpbackup2')

    # Usual arguments which are applicable for the whole script / top-level args
    arg_parser.add_argument('--version', action='version',
                    version='%(prog)s {version}'.format(version=__version__))
    arg_parser.add_argument('--log-level',
                            default='CRITICAL',
                            help='Log level',
                            required=False)
    arg_parser.add_argument('--whatIf',
                            action='store_true',
                            dest='what_if',
                            help='Execute in "what if" mode (no changes actually made)')

    # Setup the subparsers container
    subparsers = arg_parser.add_subparsers(help='Action being requested', dest='action')

    # Create parent (or shared) subparser. Note `add_help=False` and creation via `argparse.`
    shared_parser = argparse.ArgumentParser(add_help=False)
    shared_parser.add_argument('--wp-dir',
                            help='Path to the root of the WordPress directory',
                            required=True)

    shared_parser.add_argument('--mode',
                               choices=['files', 'db', 'all'],
                               default='all',
                               help='Indicate what to be Backup/Restore')

    shared_parser.add_argument('--archive',
                            help='Path and filename of the archive (.tar.gz) '
                                 'to backup to/restore from.',
                            default=None,
                            required=False)

    # Setup the individual sub parers
    backup_parser = subparsers.add_parser("backup", parents=[shared_parser],
                            help='Perform a wordpress backup')

    restore_parser = subparsers.add_parser("restore", parents=[shared_parser],
                            help='Perform a wordpress restore')

    restore_parser.add_argument('--cleanfirst',
                            action='store_true',
                            help='Removes existing files/db before restoring data')

    restore_parser.add_argument('--admin-username',
                            help='Database admin username.',
                            required=False)

    restore_parser.add_argument('--admin-password',
                            help='Database admin password.',
                            required=False)

    restore_parser.add_argument('--admin-credentials-aws-secret-id',
                            help='Database admin credentials secret ID. ',
                            required=False)

    restore_parser.add_argument('--admin-credentials-aws-region',
                            help='Region in which the database admin ',
                            required=False)

    restore_parser.add_argument('--only-appointed-in-asg',
                            action='store_true',
                            help='Ensure that only one AWS EC2 instance in '
                                 'this auto-scaling group performs the '
                                 'action.')

    restore_parser.add_argument('--new-site-url',
                            default=None,
                            help='New Site Url',
                            required=False)

    restore_parser.add_argument('--new-site-home-url',
                            default=None,
                            help='New Site Home Url',
                            required=False)

    restore_parser.add_argument('--new-db-host',
                            default=None,
                            help='New Database Host',
                            required=False)

    restore_parser.add_argument('--new-db-name',
                            default=None,
                            help='New Database Name',
                            required=False)

    restore_parser.add_argument('--new-db-user',
                            default=None,
                            help='New Database User Name',
                            required=False)

    restore_parser.add_argument('--new-db-password',
                            default=None,
                            help='New Database User Password',
                            required=False)

    restore_parser.add_argument('--force',
                            action='store_true',
                            help='Force restore even if already exists',
                            required=False)

    args = arg_parser.parse_args()

    logging.basicConfig(level=str(args.log_level).upper())
    log = logging.getLogger(__name__)

    wpbackup = WpBackup(args.what_if)

    if args.what_if:
        log.info("***** WHAT IF MODE ENABLED *******")

    if args.action == "backup":
        log.info("Starting wordpress backup for site in '%s'", args.wp_dir)
        wp_site = WpSite.from_wp_path(args.wp_dir)

        backup_mode = WpBackupMode.ALL
        if str(args.mode).upper() == "DATABASE":
            backup_mode = WpBackupMode.DATABASE
        elif str(args.mode).upper() == "FILES":
            backup_mode = WpBackupMode.FILES

        wpbackup.backup(wp_site=wp_site,
                        archive_filename=args.archive,
                        backup_mode=backup_mode
                        )

    elif args.action == "restore":
        log.info("Starting wordpress restore for site to '%s' from file '%s'", args.wp_dir, args.archive)

        if args.only_appointed_in_asg:
            if not chesney.is_appointed():
                log.fatal('This EC2 instance is not appointed.')
                return -1

        if args.admin_credentials_aws_secret_id:
            admin_credentials = WpCredentials.from_aws_secrets_manager(
                secret_id=args.admin_credentials_aws_secret_id,
                region=args.admin_credentials_aws_region
            )
        else:
            admin_credentials = WpCredentials.from_username_and_password(
                username=args.admin_username,
                password=args.admin_password
            )

        wp_site = WpSite(site_home=args.new_site_home_url if "new_site_host" in args else None,
                        site_url=args.new_site_url  if "new_site_url" in args else None,
                        site_path=args.wp_dir,
                        db_host=args.new_db_host if "new_db_host" in args else None,
                        db_name=args.new_db_name if "new_db_name" in args else None,
                        credentials=WpCredentials.from_username_and_password(args.new_db_user if "new_db_user" in args else None, args.new_db_password if "new_db_password" in args else None),
                        admin_credentials=admin_credentials
                        )

        wpbackup.restore(wp_site=wp_site,
                         archive_filename=args.archive,
                         restore_mode=WpRestoreMode.ALLCLEAN if args.force else WpRestoreMode.ALLOVERWRITE
                         )

if __name__ == '__main__':
    run_from_cli()
