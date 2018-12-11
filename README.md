# py-wordpress-backup

A Python package for backing up and restoring a self-hosted WordPress installation, including the database and uploaded content.

The backup file will contain:

 - Your database as a MySQL dump.
 - An exact copy of your entire WordPress directory.

## TODO

 - Unit tests.
 - Handle `wp-config.php` being somewhere other than the default location.

## Installation

```shell
pip install wpbackup
```

## Usage

To backup:

```shell
python3 -m wpbackup --backup                  \
                    --wp-dir  /www/wordpress  \
                    --archive ~/backup.tar.gz
```

Note that the current release of `py-wordpress-backup` expected `wp-config.php` to exist within your WordPress directory, and will use it to read your database credentials to perform the backup. Keeping your `wp-config.php` file in this location *might* not be the best practice, and I'll likely handle this in a future update.

To restore using database admin credentials held in AWS Secrets Manager:

```shell
python3 -m wpbackup --restore                                           \
                    --wp-dir                          /www/wordpress    \
                    --archive                         ~/backup.tar.gz   \
                    --admin-credentials-aws-secret-id AdminUserSecretID \
                    --admin-credentials-aws-region    eu-west-1
```

To restore with specified database admin credentials:

```shell
python3 -m wpbackup --restore                        \
                    --wp-dir         /www/wordpress  \
                    --archive        ~/backup.tar.gz \
                    --admin-user     admin           \
                    --admin-password trustno1
```

## Development

### Prerequisites

py-wordpress-backup requires Python 3.x.

### Installing dependencies

```shell
pip install -e .[dev]
```
