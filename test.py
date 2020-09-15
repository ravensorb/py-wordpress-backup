#!/usr/bin/python3 

""" Run all the unit tests. """

from subprocess import CalledProcessError, check_call
import logging

logging.basicConfig(level=logging.DEBUG)

try:
    check_call(['coverage',
                'run',
                '-m',
                'unittest',
                'discover',
                '--start-directory',
                'tests'])
except CalledProcessError:
    exit(1)

#check_call(['coverage', 'report'])
