"""
Generate JavaScript documentation.

Usage::

    ./manage.py jsdoc

"""
import os
import subprocess

from django.conf import settings

from django_extras.management.commands import MediaAppsCommand

class Command(MediaAppsCommand):
    """Generate the JavaScript documentation for the applications using
    JSDoc."""
    help = "Run JSDoc over the JavaScript files."

    def __init__(self):
        super(Command, self).__init__('js', 'JavaScript')

    def handle_app_media(self, app_name, media_path, **options):
        """Main entry point for the command."""
        # Needs to be a relative path so that absolute paths are not displayed
        # in docs. Otherwise, the absolute path of the computer where the
        # docs were built is displayed.
        project_path = settings.PROJECT_ROOT
        if not project_path.endswith('/'):
            project_path += '/'
        media_path = media_path.replace(project_path, '')
        target_path = os.path.join('build', 'jsdoc', app_name)
        print 'Generating JSDoc for %s' % app_name
        subprocess.check_call(['java',
            '-jar', os.path.join(settings.JS_DOC_PATH, 'jsrun.jar'),
            os.path.join(settings.JS_DOC_PATH, 'app', 'run.js'),
            '-t=%s' % os.path.join(settings.JS_DOC_PATH, 'templates', 't11e_jsdoc'),
            '-d=%s' % target_path,
            '-r=5',
            media_path])
        print 'Generated: %s' % os.path.join(target_path, 'index.html')
