#!/usr/bin/env python

# Copyright (C) 2013 Craig Phillips.  All rights reserved.

from distutils.core import setup

version = __import__('libgsync.version').get_version()

setup(
    name = 'gsync',
    description = 'GSync - RSync for Google Drive',
    version = version,
    license = 'BSD License',
    author = 'Craig Phillips',
    author_email = 'iwonbigbro@gmail.com',
    url = 'https://github.com/iwonbigbro/gsync',
    requires = [
        'docopt',
        'apiclient',
        'apiclient.discovery',
        'httplib2',
        'json',
        'pickle',
        'cPickle',
        'oauth2client',
        'urllib3',
    ],
    packages = [
        'libgsync',
        'libgsync.drive',
        'libgsync.sync',
        'libgsync.sync.file',
        'libgsync.sync.file.local',
        'libgsync.sync.file.remote',
    ],
    data_files = [
        ('libgsync/data', [ 'libgsync/data/client.json' ]),
    ],
    scripts = [ 'bin/gsync' ],
)
