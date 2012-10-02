"""
Check the validity of the Python files.

Explanation of codes can be found here::

    http://pylint-messages.wikidot.com/all-codes
"""
import subprocess
import os
import sys

from django.core.management.base import CommandError
from django.conf import settings

from media_compressor.management.commands import AppsCommand

class Command(AppsCommand):
    """Run pylint over the Python files for the applications."""
    help = "Run pylint over the Python files."

    def handle_app(self, app_name, app_module, _app_path, _explict_apps,
        **options):
        """Main entry point for the command."""
        print 'Running pylint over %s' % app_name
        print 'Using configuration file %s.' % settings.PY_LINT_RC_PATH
        cmd = [
            'pylint',
            '--rcfile=%s' % settings.PY_LINT_RC_PATH,
            app_name,
        ]
        # Poke in our current Python path so the Django apps can be
        # found from the subprocess.
        env = dict(os.environ)
        env['PYTHONPATH'] = os.pathsep.join(sys.path)
        ret_val = subprocess.call(cmd, env=env)
        if ret_val != 0:
            raise CommandError("pylint check failed for %s" % (app_name,))
