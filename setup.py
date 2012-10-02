#!/usr/bin/env python

import os
import fnmatch

from setuptools import setup, find_packages

def find_media(app_dir, pattern):
    for dirpath, _, filenames in os.walk(app_dir):
        for filename in filenames:
            if fnmatch.fnmatch(filename, pattern):
                yield os.path.join(os.path.pardir, dirpath, filename)

def media_for_app(app_dir):
    extensions = ['*.css', '*.png', '*.jpg', '*.gif', '*.js', '*.conf', '*.html']
    media_list = []
    for extension in extensions:
        media_list.extend(list(find_media(app_dir, extension)))
    return media_list

setup(
    name='media_compressor',
    description='Django Media Compressor',
    version='0.0.0',

    install_requires = [
        'setuptools',
        'django==1.3.3',
        'pyyaml==3.10',
    ],

    # We aren't doing anything that makes us zip unsafe but Django 1.3
    # doesn't collect static files from inside of zipped eggs.
    zip_safe = False,

    packages=find_packages(exclude=[
        'ez_setup',
    ]),
    #include_package_data = True, # See MANIFEST.in for the package_data rules
    package_data={
        'django_extras': media_for_app('django_extras'),
    },
)
