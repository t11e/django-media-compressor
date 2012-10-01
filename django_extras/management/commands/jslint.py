"""
Check the validity of the JavaScript files.

Usage::

    ./manage.py jslint

"""
import os
import subprocess

from django.conf import settings
from django.core.management.base import CommandError

from django_extras.management.commands import MediaAppsCommand

class Command(MediaAppsCommand):
    """Run jslint over all the JavaScript files for the applications."""
    help = "Run jslint over the JavaScript files."

    def __init__(self):
        super(Command, self).__init__('js', 'JavaScript')

    def handle_app_media(self, app_name, media_path, **options):
        """Main entry point for the command."""
        files = []
        for (dirpath, _, filenames) in os.walk(media_path):
            for filename in filenames:
                if filename.endswith('.js'):
                    files.append(os.path.join(dirpath, filename))

        print 'Running JSLint over %s' % app_name
        cmd = ['java',
            '-jar', settings.JS_LINT_PATH,
            #'--adsafe',
            '--bitwise',
            #'--browser',
            #'--cap',
            #'--css',
            #'--debug',
            '--eqeqeq',
            #'--evil',
            '--forin',
            #'--fragment'
            '--immed',
            '--indent=4',
            #'--laxbreak',
            '--newcap',
            '--nomen',
            #'--on',
            #'--onevar',
            '--passfail',
            #'--plusplus',
            '--regexp',
            #'--safe',
            #'--sidebar',
            #'--strict',
            #'--sub',
            #'--undef',
            '--white',
            #'--widget',
            ]
        ret_val = subprocess.call(cmd + files)
        if ret_val != 0:
            raise CommandError("JSLint check failed")
