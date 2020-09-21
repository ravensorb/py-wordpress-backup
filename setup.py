"""
"wpbackup2" package setup.
"""

import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# with open('README.md', 'r') as stream:
#     LONG_DESCRIPTION = stream.read()

setup(
    author='Shawn Anderson',
    author_email='code@eye-catcher.com',
    long_description_content_type='text/markdown',
    long_description=README,
    description='Backup and restore all your self-hosted WordPress content',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Site Management'
    ],
    extras_require={
        'dev': [
            'autopep8',
            'coverage',
            'pylint'
        ]
    },
    install_requires=[
        'chesney>=1.0,<=2.0',
        'wpconfigr>=1.0.0,<=2.0.0',
        'wpdatabase2>=0.0.3,<=1.0.0'
    ],
    name='wpbackup2',
    license='MIT License',
    packages=[
        'wpbackup2',
        'wpbackup2.classes',
        'wpbackup2.exceptions'
    ],
    url='https://github.com/ravensorb/py-wordpress-backup',
    version='0.2.10'
)
